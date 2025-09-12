from __future__ import annotations

import json
from typing import Any, Dict, List

import requests

from services.llm.client import LLMClient
from services.predictor.heuristic import infer_from_hits, suggest_parts_and_tools, _analyze_failure_context


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

    # Análisis inteligente de fallas usando la nueva lógica
    failure_context = _analyze_failure_context(hits, descripcion)
    intelligent_predictions = infer_from_hits(hits, descripcion)
    intelligent_parts_tools = suggest_parts_and_tools(intelligent_predictions, failure_context)

    # Prompt mejorado con validación estricta
    system_prompt = (
        "Eres un asistente técnico experto y debes responder en español. Responde SOLO con JSON válido, sin texto adicional ni explicaciones, cumpliendo EXACTAMENTE este esquema: "
        "{"
        "\"fallas_probables\": [{\"falla\": \"string\", \"confidence\": 0.0, \"rationale\": \"string\"}],"
        "\"repuestos_sugeridos\": [\"string\"],"
        "\"herramientas_sugeridas\": [\"string\"],"
        "\"pasos\": [{\"orden\": 1, \"descripcion\": \"string\", \"tipo\": \"diagnostico|reparacion\"}],"
        "\"feedback_coherencia\": \"string\""
        "}. "
        "REGLAS CRÍTICAS: "
        "1) USA ÚNICAMENTE la evidencia del CONTEXTO proporcionado. PROHIBIDO inventar información no presente. "
        "2) Si el contexto es insuficiente (<200 caracteres o <2 fuentes), usa confidencias bajas (0.2–0.4) y sé explícito sobre la limitación. "
        "3) confidence debe estar en [0,1] con exactamente 2 decimales. "
        "4) Cada rationale DEBE citar específicamente las fuentes como [source:doc_id] y explicar la conexión directa. "
        "5) Devuelve 3–7 pasos específicos, con orden consecutivo desde 1, descripciones técnicas precisas, tipo en {diagnostico,reparacion}. "
        "6) Para repuestos/herramientas: SOLO menciona los que estén explícitamente referenciados en el contexto o sean directamente derivables. "
        "7) VALIDA que cada elemento de la respuesta tenga base en el contexto. No agregues información genérica. "
        "8) Si no hay suficiente evidencia, devuelve listas vacías en lugar de inventar. "
        "9) No uses markdown, bloques de código, ni explicaciones adicionales; SOLO el JSON válido."
    )
    
    # Incluir análisis inteligente en el prompt para guiar al LLM
    intelligent_summary = ""
    if intelligent_predictions:
        intelligent_summary = f"\nAnálisis inteligente previo (usar como guía, no como verdad absoluta):\n"
        for pred in intelligent_predictions[:2]:  # Solo top 2 para no sobrecargar
            intelligent_summary += f"- {pred.get('falla', '')} (confianza: {pred.get('confidence', 0)})\n"
        
    user_prompt = (
        f"Contexto técnico (fuentes verificadas de KB):\n{context}\n"
        f"{intelligent_summary}"
        f"Equipo analizado: {json.dumps(equipo, ensure_ascii=False)}\n"
        f"Descripción del problema reportado: {descripcion}\n\n"
        "IMPORTANTE: Basa tu respuesta ÚNICAMENTE en el contexto técnico proporcionado. "
        "Devuelve SOLO el JSON estructurado (sin explicaciones adicionales)."
    )

    llm = LLMClient()
    raw = llm.complete_json(system_prompt, user_prompt)
    data = _parse_json_safely(raw)
    
    # Validación y enriquecimiento de la respuesta
    num_hits = len(hits)
    context_length = len(context)
    low_evidence = num_hits == 0 or (num_hits < 2 and context_length < 200)
    
    # Si la evidencia es muy baja, usar predicciones inteligentes como fallback
    if low_evidence and intelligent_predictions:
        data["fallas_probables"] = intelligent_predictions[:3]  # Top 3
        data["repuestos_sugeridos"] = intelligent_parts_tools.get("repuestos_sugeridos", [])[:5]
        data["herramientas_sugeridas"] = intelligent_parts_tools.get("herramientas_sugeridas", [])[:6]
        data["feedback_coherencia"] = "Respuesta basada en análisis heurístico debido a evidencia limitada en KB"
    
    # Validación de coherencia post-LLM
    validated_failures = []
    for failure in data.get("fallas_probables", []):
        rationale = failure.get("rationale", "")
        # Verificar que el rationale cite fuentes reales
        if "[source:" in rationale or "análisis" in rationale.lower():
            validated_failures.append(failure)
        elif low_evidence:  # Permitir si evidencia es baja
            validated_failures.append(failure)
    
    data["fallas_probables"] = validated_failures
    
    # Señales mejoradas para transparencia
    data["signals"] = {
        "kb_hits": num_hits,
        "context_length": context_length,
        "low_evidence": bool(low_evidence),
        "intelligent_analysis_used": bool(low_evidence and intelligent_predictions),
        "validation_passed": len(validated_failures) > 0
    }
    
    fuentes = [h.get("doc_id") for h in hits]
    data["fuentes"] = fuentes
    
    # Agregar métricas de calidad
    data["quality_metrics"] = {
        "context_relevance": min(1.0, context_length / 500),  # Normalizado
        "source_diversity": min(1.0, num_hits / 5),  # Normalizado
        "prediction_confidence": sum(f.get("confidence", 0) for f in data["fallas_probables"]) / max(1, len(data["fallas_probables"]))
    }
    
    return data


