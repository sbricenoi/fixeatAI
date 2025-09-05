from __future__ import annotations

import json
from typing import Any, Dict, List

import requests

from services.llm.client import LLMClient


def build_context_from_hits(hits: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for h in hits:
        doc_id = h.get("doc_id")
        snippet = h.get("snippet")
        lines.append(f"[source:{doc_id}] {snippet}")
    return "\n".join(lines)


def _parse_json_safely(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except Exception:
        # Intento: extraer el primer bloque que parece JSON
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except Exception:
                pass
    return {
        "fallas_probables": [],
        "repuestos_sugeridos": [],
        "herramientas_sugeridas": [],
        "pasos": [],
        "feedback_coherencia": "Parsing error",
    }


def predict_with_llm(mcp_url: str, descripcion: str, equipo: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
    # Recuperación
    # Construcción de filtros para Chroma (requiere operador en top-level, ej. "$and")
    conds: List[Dict[str, Any]] = []
    brand = (equipo or {}).get("marca") or (equipo or {}).get("brand")
    model = (equipo or {}).get("modelo") or (equipo or {}).get("model")
    if brand:
        conds.append({"brand": {"$eq": str(brand)}})
    if model:
        conds.append({"model": {"$eq": str(model)}})

    payload = {"query": descripcion, "top_k": top_k}
    if conds:
        payload["where"] = {"$and": conds}
    res = requests.post(f"{mcp_url}/tools/kb_search", json=payload, timeout=10)
    hits = res.json().get("hits", [])
    context = build_context_from_hits(hits)

    # Prompt
    system_prompt = (
        "Eres un asistente técnico y debes responder en español. Responde SOLO con JSON válido, sin texto adicional ni explicaciones, cumpliendo EXACTAMENTE este esquema: "
        "{"
        "\"fallas_probables\": [{\"falla\": \"string\", \"confidence\": 0.0, \"rationale\": \"string\"}],"
        "\"repuestos_sugeridos\": [\"string\"],"
        "\"herramientas_sugeridas\": [\"string\"],"
        "\"pasos\": [{\"orden\": 1, \"descripcion\": \"string\", \"tipo\": \"diagnostico|reparacion\"}],"
        "\"feedback_coherencia\": \"string\""
        "}. "
        "Reglas: "
        "1) Usa SOLO la evidencia del CONTEXTO; si es insuficiente, deja listas vacías o usa confidencias bajas (0.2–0.4). "
        "2) confidence en [0,1] con 2 decimales. "
        "3) Cada rationale DEBE citar fuentes como [source:doc_id]. "
        "4) Devuelve 3–7 pasos, orden consecutivo desde 1, descripciones cortas, tipo en {diagnostico,reparacion}. "
        "5) Deduplica repuestos/herramientas. No inventes piezas o datos no presentes. "
        "6) No uses markdown ni bloques de código; SOLO el JSON."
    )
    user_prompt = (
        f"Contexto (fuentes de KB):\n{context}\n\n"
        f"Equipo: {json.dumps(equipo, ensure_ascii=False)}\n"
        f"Descripcion del problema: {descripcion}\n\n"
        "Devuelve SOLO el JSON (sin explicaciones adicionales)."
    )

    llm = LLMClient()
    raw = llm.complete_json(system_prompt, user_prompt)
    data = _parse_json_safely(raw)
    # Señales: confianza y lagunas
    num_hits = len(hits)
    low_evidence = num_hits == 0 or (num_hits < 3 and len(context) < 400)
    data["signals"] = {
        "kb_hits": num_hits,
        "low_evidence": bool(low_evidence),
    }
    fuentes = [h.get("doc_id") for h in hits]
    data["fuentes"] = fuentes
    return data


