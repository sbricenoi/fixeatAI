"""Módulo RAG (Retrieval-Augmented Generation) para predicciones con LLM.

Este es el MOTOR PRINCIPAL del sistema. El LLM lee el contenido real de los manuales
almacenados en la KB y genera respuestas dinámicas basadas en ese contenido.

NO usa diccionarios estáticos ni patrones predefinidos. Todo se aprende del contexto.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

import requests

from services.llm.client import LLMClient
from services.predictor.heuristic import infer_from_hits, _analyze_failure_context


def build_context_from_hits(hits: List[Dict[str, Any]]) -> str:
    """Construye contexto textual enriquecido desde los hits de KB.
    
    Usa el campo "context" (contexto ampliado) cuando está disponible,
    con fallback a "snippet" para compatibilidad con versiones anteriores.
    
    Args:
        hits: Resultados de búsqueda semántica en KB
        
    Returns:
        Contexto formateado con fuentes citables
    """
    lines: List[str] = []
    for h in hits:
        doc_id = h.get("doc_id", "unknown")
        # Preferir "context" (ampliado) sobre "snippet" (limitado a 500 chars)
        text = h.get("context") or h.get("snippet", "")
        metadata = h.get("metadata", {})
        
        # Incluir metadata relevante si está disponible
        context_line = f"[source:{doc_id}]"
        if metadata.get("brand"):
            context_line += f" [marca:{metadata['brand']}]"
        if metadata.get("model"):
            context_line += f" [modelo:{metadata['model']}]"
        if metadata.get("page"):
            context_line += f" [página:{metadata['page']}]"
        context_line += f" {text}"
        
        lines.append(context_line)
    
    return "\n".join(lines)


def _parse_json_safely(raw: str) -> Dict[str, Any]:
    """Parse JSON de respuesta del LLM con manejo robusto de errores."""
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
    
    # Fallback con estructura mínima
    return {
        "fallas_probables": [],
        "feedback_coherencia": "Error al parsear respuesta del LLM. Por favor intente nuevamente.",
    }


def _search_kb(mcp_url: str, descripcion: str, brand: str | None, model: str | None, top_k: int) -> List[Dict[str, Any]]:
    """Búsqueda híbrida en KB con fallback y boost de modelo."""
    import re
    tiene_codigo_error = bool(re.search(r'\b(service|servicio|error|código|s_)\s*\d+', descripcion.lower()))
    query_enriched = descripcion if tiene_codigo_error else f"{brand or ''} {model or ''} {descripcion}".strip()
    where_brand = {"brand": brand} if brand else None
    model_boost = 1.5 if model else 1.0

    payload = {"query": query_enriched, "top_k": top_k * 2, "semantic_weight": 0.3, "keyword_weight": 0.7, "context_chars": 2000, "where": where_brand}
    print(f"🔍 Buscando en KB: query='{query_enriched[:60]}' top_k={top_k}")

    hits: List[Dict[str, Any]] = []
    try:
        res = requests.post(f"{mcp_url}/tools/kb_search_hybrid", json=payload, timeout=30)
        hits = res.json().get("hits", [])
        if not hits and where_brand:
            payload["where"] = None
            res = requests.post(f"{mcp_url}/tools/kb_search_hybrid", json=payload, timeout=30)
            hits = res.json().get("hits", [])
    except Exception as e:
        print(f"❌ Error en búsqueda KB: {e}")
        try:
            res = requests.post(f"{mcp_url}/tools/kb_search_extended", json={"query": query_enriched, "top_k": top_k, "context_chars": 2000}, timeout=10)
            hits = res.json().get("hits", [])
        except Exception:
            hits = []

    # Model boost reranking
    if hits and model:
        model_variants = [model.lower().replace(" ", ""), model.lower().replace(" ", "_"), model.lower()]
        for hit in hits:
            doc_id = hit.get("doc_id", "").lower()
            meta = hit.get("metadata", {})
            if any(v in doc_id or v in str(meta.get("model", "")).lower() for v in model_variants):
                hit["score"] = hit.get("score", 0) * model_boost
        hits.sort(key=lambda x: x.get("score", 0), reverse=True)

    print(f"🔍 {len(hits[:top_k])} hits obtenidos")
    return hits[:top_k]


def predict_with_llm(mcp_url: str, descripcion: str, equipo: Dict[str, Any], top_k: int = 5, pre_fetched_hits: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Genera predicción usando LLM con contexto de KB.

    Args:
        mcp_url: URL del servicio MCP con KB
        descripcion: Descripción del problema reportado
        equipo: Información del equipo (marca, modelo, etc)
        top_k: Número de documentos a recuperar de KB
        pre_fetched_hits: Hits pre-cargados (omite búsqueda si se proveen)

    Returns:
        Diccionario con predicción estructurada basada en contenido real
    """
    brand = (equipo or {}).get("marca") or (equipo or {}).get("brand")
    model = (equipo or {}).get("modelo") or (equipo or {}).get("model")

    if pre_fetched_hits is not None:
        hits = pre_fetched_hits
        print(f"⚡ Usando {len(hits)} hits pre-cargados")
    else:
        hits = _search_kb(mcp_url, descripcion, brand, model, top_k)
    
    context = build_context_from_hits(hits)
    num_hits = len(hits)
    context_length = len(context)
    low_evidence = num_hits == 0 or (num_hits < 2 and context_length < 200)
    
    # 2. FALLBACK: Si no hay suficiente contexto, usar heurística mínima
    if low_evidence:
        failure_context = _analyze_failure_context(hits, descripcion)
        fallback_predictions = infer_from_hits(hits, descripcion)
        
        return {
            "fallas_probables": fallback_predictions,
            "feedback_coherencia": "Análisis heurístico debido a evidencia limitada en KB. Se recomienda actualizar KB con más documentación.",
            "fuentes": [h.get("doc_id") for h in hits],
            "signals": {
                "kb_hits": num_hits,
                "context_length": context_length,
                "low_evidence": True,
                "fallback_used": True,
                "llm_used": False
            },
            "quality_metrics": {
                "context_relevance": 0.0,
                "source_diversity": 0.0,
                "prediction_confidence": 0.3
            }
        }
    
    # 3. GENERACIÓN: LLM analiza el contenido REAL de los manuales
    system_prompt = (
        "Eres un asistente técnico experto que analiza documentación de equipos industriales. "
        "Tu trabajo es leer el CONTEXTO REAL proporcionado (extractos de manuales) y generar diagnósticos precisos.\n\n"
        "Responde SOLO con JSON válido (sin markdown ni explicaciones), con esta estructura EXACTA:\n"
        "{\n"
        '  "fallas_probables": [\n'
        "    {\n"
        '      "falla": "descripción de la falla detectada",\n'
        '      "confidence": 0.85,\n'
        '      "rationale": "explicación citando [source:doc_id]",\n'
        '      "repuestos_sugeridos": ["repuesto1", "repuesto2"],\n'
        '      "herramientas_sugeridas": ["herramienta1", "herramienta2"],\n'
        "      \"pasos\": [\n"
        '        {"orden": 1, "descripcion": "paso", "tipo": "seguridad"},\n'
        '        {"orden": 2, "descripcion": "paso", "tipo": "diagnostico"},\n'
        '        {"orden": 3, "descripcion": "paso", "tipo": "reparacion"}\n'
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "feedback_coherencia": "evaluación de la coherencia del problema reportado"\n'
        "}\n\n"
        "REGLAS CRÍTICAS:\n"
        "1. USA ÚNICAMENTE información del CONTEXTO proporcionado. NO inventes datos.\n"
        "2. Cada 'rationale' DEBE citar fuentes específicas como [source:doc_id].\n"
        "3. Los 'repuestos_sugeridos' y 'herramientas_sugeridas' deben estar mencionados o derivables del contexto.\n"
        "4. Los 'pasos' DEBEN incluir:\n"
        "   - INICIO: 3 pasos de seguridad (desconexión eléctrica, EPP, verificación de presión)\n"
        "   - MEDIO: 3-5 pasos de diagnóstico específicos del problema\n"
        "   - MEDIO: 2-4 pasos de reparación si aplica\n"
        "   - FIN: 1 paso de seguridad final (verificación y prueba supervisada)\n"
        "5. 'confidence' debe estar en [0,1] con 2 decimales.\n"
        "6. Genera 1-3 fallas probables según la evidencia disponible.\n"
        "7. Si el contexto es limitado, usa confidencias bajas (0.3-0.5) y sé explícito en el rationale.\n"
        "8. Responde SOLO el JSON, sin explicaciones adicionales ni markdown."
    )
    
    equipment_info = f"Marca: {brand or 'N/A'}, Modelo: {model or 'N/A'}"
    if equipo.get("categoria"):
        equipment_info += f", Categoría: {equipo['categoria']}"
    
    user_prompt = (
        f"CONTEXTO TÉCNICO (extractos de manuales reales):\n"
        f"{context}\n\n"
        f"EQUIPO: {equipment_info}\n"
        f"PROBLEMA REPORTADO: {descripcion}\n\n"
        f"Analiza el contexto y genera diagnóstico basado ÚNICAMENTE en la información proporcionada."
    )

    # 4. INVOCACIÓN del LLM
    try:
        llm = LLMClient()
        raw = llm.complete_json(system_prompt, user_prompt, force_json=True, max_tokens=2000)
        data = _parse_json_safely(raw)
    except Exception as e:
        print(f"Error en LLM: {e}")
        # Fallback si LLM falla
        fallback_predictions = infer_from_hits(hits, descripcion)
        return {
            "fallas_probables": fallback_predictions,
            "feedback_coherencia": f"Error en LLM: {str(e)}. Usando análisis heurístico.",
            "fuentes": [h.get("doc_id") for h in hits],
            "signals": {
                "kb_hits": num_hits,
                "context_length": context_length,
                "low_evidence": False,
                "fallback_used": True,
                "llm_used": False,
                "llm_error": str(e)
            }
        }
    
    # 5. VALIDACIÓN Y ENRIQUECIMIENTO
    validated_failures = []
    for failure in data.get("fallas_probables", []):
        rationale = failure.get("rationale", "")
        
        # Validar que cite fuentes del contexto real
        if "[source:" in rationale:
            validated_failures.append(failure)
        elif low_evidence:
            # Permitir sin fuentes si evidencia es baja, pero ajustar confidence
            if failure.get("confidence", 0) > 0.5:
                failure["confidence"] = 0.5
            validated_failures.append(failure)
    
    # Si no hay fallas validadas, usar fallback
    if not validated_failures:
        fallback_predictions = infer_from_hits(hits, descripcion)
        validated_failures = fallback_predictions
    
    data["fallas_probables"] = validated_failures
    
    # 6. METADATA y señales de calidad
    fuentes = [h.get("doc_id") for h in hits]
    data["fuentes"] = fuentes
    
    data["signals"] = {
        "kb_hits": num_hits,
        "context_length": context_length,
        "low_evidence": low_evidence,
        "fallback_used": False,
        "llm_used": True,
        "validation_passed": len(validated_failures) > 0
    }
    
    # Métricas de calidad
    avg_confidence = sum(f.get("confidence", 0) for f in validated_failures) / max(1, len(validated_failures))
    data["quality_metrics"] = {
        "context_relevance": min(1.0, context_length / 1000),  # Normalizado
        "source_diversity": min(1.0, num_hits / 5),  # Normalizado
        "prediction_confidence": round(avg_confidence, 2)
    }
    
    # Agregar hits para que el endpoint pueda construir contextos
    data["_raw_hits"] = hits
    
    return data
