from __future__ import annotations

import json
from typing import Any, Dict, List
import requests

from services.llm.client import LLMClient


def _parse_json_safely(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except Exception:
                pass
    return {
        "alertas": [],
        "accionables": [],
        "metricas": {},
        "recomendaciones": [],
        "signals": {"low_evidence": True},
    }


def _compute_hints(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula señales heurísticas simples para dar contexto al LLM.

    Espera llaves opcionales en payload: visitas (list), inventario (list), equipos (list), tickets (list).
    """
    visitas: List[Dict[str, Any]] = payload.get("visitas") or []
    inventario: List[Dict[str, Any]] = payload.get("inventario") or []

    stock_critico = [p for p in inventario if isinstance(p.get("stock"), (int, float)) and p.get("stock", 0) <= 0]
    uso_estimado_alto = []
    # Conteo simple de uso por repuesto en la última semana (si viene timestamp/semana)
    for v in visitas:
        for rep in v.get("repuestos_usados", []) or []:
            uso_estimado_alto.append(rep)

    tecnicos = {}
    for v in visitas:
        t = (v.get("tecnico") or {}).get("id")
        if not t:
            continue
        tecnicos.setdefault(t, {"post_falla": 0, "total": 0})
        tecnicos[t]["total"] += 1
        if v.get("post_falla", False):
            tecnicos[t]["post_falla"] += 1

    outliers_tecnico = [tid for tid, m in tecnicos.items() if m["total"] >= 3 and (m["post_falla"] / max(1, m["total"])) > 0.4]

    return {
        "stock_cero": [p.get("sku") or p.get("nombre") for p in stock_critico],
        "repuestos_con_uso_reciente": uso_estimado_alto,
        "tecnicos_outliers": outliers_tecnico,
        "counts": {
            "visitas": len(visitas),
            "inventario_items": len(inventario),
        },
    }


def analyze_ops(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analiza visitas, inventario y equipos para generar accionables de operaciones."""
    hints = _compute_hints(payload)

    system_prompt = (
        "Eres un analista de operaciones. Responde SOLO con JSON válido en español con este esquema: "
        "{"
        '"alertas": [{"titulo":"string","severidad":"alta|media|baja","impacto":"string","rationale":"string","fuentes":["string"]}],'
        '"accionables": [{"accion":"string","prioridad":"alta|media|baja","due_days":7,"owner":"ops|compras|capacitacion|soporte","rationale":"string"}],'
        '"metricas": {"stock_critico":0,"tasa_fallas":0.0,"tecnicos_outliers":["string"]},'
        '"recomendaciones": ["string"],'
        '"signals": {"low_evidence": false},'
        "}. "
        "Reglas: 1) Usa SOLO la evidencia del input; 2) No inventes datos; 3) Si faltan datos, marca low_evidence=true y sugiere cómo obtenerlos; 4) Incluye 2–6 accionables claros."
    )

    user_prompt = (
        f"Datos (visitas/inventario/equipos/tickets):\n{json.dumps(payload, ensure_ascii=False)[:18000]}\n\n"
        f"Señales heurísticas: {json.dumps(hints, ensure_ascii=False)}\n\n"
        "Genera alertas, accionables, métricas y recomendaciones para el jefe de operaciones. Devuelve SOLO el JSON."
    )

    llm = LLMClient()
    raw = llm.complete_json(system_prompt, user_prompt)
    data = _parse_json_safely(raw)
    data.setdefault("signals", {})
    # Señal mínima según cobertura de datos
    low = (payload.get("visitas") is None) or (payload.get("inventario") is None)
    data["signals"].setdefault("low_evidence", bool(low))
    data["signals"]["hints"] = hints
    return data


def _build_context_from_hits(hits: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for h in hits:
        doc_id = h.get("doc_id")
        snippet = h.get("snippet")
        lines.append(f"[source:{doc_id}] {snippet}")
    return "\n".join(lines)


def analyze_ops_from_kb(mcp_url: str, prompt: str, filtros: Dict[str, Any] | None = None, top_k: int = 20) -> Dict[str, Any]:
    """Analiza usando solo información recuperada de la KB según un prompt y filtros opcionales."""
    payload: Dict[str, Any] = {"query": prompt, "top_k": top_k}
    if filtros:
        payload["where"] = filtros
    res = requests.post(f"{mcp_url}/tools/kb_search", json=payload, timeout=15)
    hits = res.json().get("hits", [])
    context = _build_context_from_hits(hits)

    system_prompt = (
        "Eres un analista de operaciones. Responde SOLO con JSON válido y CONCRETO: "
        "{"
        '"stock_alerts": [{"sku":"string","item_name":"string","current_stock":0,"reorder_point":0,"projected_usage_next_7d":0,"shortfall":0,"order_qty":0,"due_date":"YYYY-MM-DD","rationale":"string","sources":["string"]}],'
        '"technician_alerts": [{"technician_id":"string","post_visit_failure_rate":0.0,"team_avg":0.0,"delta":0.0,"visits":0,"action":"capacitacion|seguimiento","due_days":7,"rationale":"string","sources":["string"]}],'
        '"equipment_alerts": [{"brand":"string","model":"string","failure_rate":0.0,"baseline":0.0,"delta":0.0,"action":"campana_preventiva|revision_config","due_days":7,"rationale":"string","sources":["string"]}],'
        '"global_metrics": {"visits_last_7d":0,"stock_items":0,"overall_failure_rate":0.0},'
        '"recomendaciones": ["string"],'
        '"missing_data": ["string"],'
        '"signals": {"low_evidence": false},'
        '"fuentes": ["string"]'
        "}. "
        "Reglas: 1) Prohibido dar consejos genéricos (no digas 'implementar sistema'); 2) Incluye cantidades, tasas y fechas concretas; 3) Usa SOLO el contexto; si falta, deja listas vacías y completa missing_data; 4) Toda cifra o SKU debe poder rastrearse a texto del contexto y citar su fuente en 'sources'. Si el contexto no contiene datos cuantitativos o SKUs, no inventes."
    )
    system_prompt = (
        "Eres un analista de operaciones. Responde SOLO con JSON válido y CONCRETO: "
        "{"
        '"stock_alerts": [{"sku":"string","item_name":"string","current_stock":0,"reorder_point":0,"projected_usage_next_7d":0,"shortfall":0,"order_qty":0,"due_date":"YYYY-MM-DD","rationale":"string"}],'
        '"technician_alerts": [{"technician_id":"string","post_visit_failure_rate":0.0,"team_avg":0.0,"delta":0.0,"visits":0,"action":"capacitacion|seguimiento","due_days":7,"rationale":"string"}],'
        '"equipment_alerts": [{"brand":"string","model":"string","failure_rate":0.0,"baseline":0.0,"delta":0.0,"action":"campana_preventiva|revision_config","due_days":7,"rationale":"string"}],'
        '"global_metrics": {"visits_last_7d":0,"stock_items":0,"overall_failure_rate":0.0},'
        '"recomendaciones": ["string"],'
        '"missing_data": ["string"],'
        '"signals": {"low_evidence": false}'
        "}. "
        "Reglas: entrega cantidades, tasas y fechas; nada genérico. Si falta evidencia, usa missing_data y low_evidence=true."
    )

    user_prompt = (
        f"Tarea del jefe de operaciones: {prompt}\n\n"
        f"Contexto (fragmentos de KB):\n{context}\n\n"
        "Devuelve SOLO el JSON del esquema indicado."
    )

    llm = LLMClient()
    raw = llm.complete_json(system_prompt, user_prompt)
    data = _parse_json_safely(raw)
    data.setdefault("signals", {})
    low = len(hits) < 3
    data["signals"].setdefault("low_evidence", bool(low))
    data["fuentes"] = [h.get("doc_id") for h in hits]
    # Guardrails: filtrar elementos que no aparecen en el contexto
    ctx_lower = context.lower()
    def appears(s: str | None) -> bool:
        return bool(s) and (str(s).lower() in ctx_lower)
    # stock
    clean_stock = []
    for it in data.get("stock_alerts", []) or []:
        if appears(it.get("sku")) or appears(it.get("item_name")):
            clean_stock.append(it)
    data["stock_alerts"] = clean_stock
    # técnicos
    clean_tech = []
    for it in data.get("technician_alerts", []) or []:
        if appears(it.get("technician_id")):
            clean_tech.append(it)
    data["technician_alerts"] = clean_tech
    # equipos
    clean_eq = []
    for it in data.get("equipment_alerts", []) or []:
        b_ok = appears(it.get("brand")) if it.get("brand") else True
        m_ok = appears(it.get("model")) if it.get("model") else True
        if b_ok or m_ok:
            clean_eq.append(it)
    data["equipment_alerts"] = clean_eq
    if not (clean_stock or clean_tech or clean_eq):
        data["signals"]["low_evidence"] = True
        data.setdefault("missing_data", [])
        if "datos cuantitativos (stock, tasas, SKUs)" not in data["missing_data"]:
            data["missing_data"].append("datos cuantitativos (stock, tasas, SKUs)")
    return data


