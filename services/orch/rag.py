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


def predict_with_llm(mcp_url: str, descripcion: str, equipo: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
    """Genera predicción usando LLM con contexto de KB.
    
    Este es el FLUJO PRINCIPAL del sistema:
    1. Recupera contexto relevante de KB usando embeddings semánticos
    2. Construye prompt enriquecido con ese contexto
    3. El LLM lee el contenido REAL de los manuales y genera respuesta
    4. NO usa diccionarios estáticos - todo viene del contenido
    
    Args:
        mcp_url: URL del servicio MCP con KB
        descripcion: Descripción del problema reportado
        equipo: Información del equipo (marca, modelo, etc)
        top_k: Número de documentos a recuperar de KB
        
    Returns:
        Diccionario con predicción estructurada basada en contenido real
    """
    # 1. RECUPERACIÓN: Búsqueda HÍBRIDA OPTIMIZADA para iCombi Classic
    brand = (equipo or {}).get("marca") or (equipo or {}).get("brand")
    model = (equipo or {}).get("modelo") or (equipo or {}).get("model")
    
    # Normalizar modelo para filtrado
    model_normalized = None
    if model:
        model_lower = model.lower().replace(" ", "").replace("-", "")
        if "icombiclassic" in model_lower or "classic" in model_lower:
            model_normalized = "iCombi Classic"
        elif "icombipro" in model_lower or "pro" in model_lower:
            model_normalized = "iCombi Pro"
    
    # OPTIMIZACIÓN: Para búsqueda híbrida con códigos de error,
    # NO diluir la query con marca/modelo ya que reduce keyword matching
    # Los códigos de error son más específicos que la marca
    import re
    tiene_codigo_error = bool(re.search(r'\b(service|servicio|error|código|s_)\s*\d+', descripcion.lower()))
    
    if tiene_codigo_error:
        # Query limpia para mejor keyword matching
        query_enriched = descripcion
    else:
        # Query enriquecida para búsqueda semántica general
        query_enriched = f"{brand or ''} {model or ''} {descripcion}".strip()
    
    # FILTRADO POR METADATA: Si tenemos modelo específico, lo usamos para RERANKING
    # No usamos where filter porque ChromaDB tiene limitaciones y querríamos más resultados
    # En su lugar, haremos post-processing para dar boost a docs del modelo correcto
    model_boost = 1.5 if model_normalized else 1.0  # 50% boost para modelo correcto
    print(f"🎯 Modelo detectado: {model_normalized or 'N/A'}, boost={model_boost}x")

    # Usar kb_search_hybrid: combina búsqueda semántica + keyword matching
    # Esto mejora SIGNIFICATIVAMENTE la relevancia para códigos de error técnicos
    payload = {
        "query": query_enriched, 
        "top_k": top_k * 2,  # Obtener más resultados para post-filtering
        "semantic_weight": 0.3,  # Reducimos peso semántico para códigos
        "keyword_weight": 0.7,   # Aumentamos peso keywords (detecta "service 25", "error 42", etc.)
        "context_chars": 2000,   # Contexto ampliado
    }
    
    print(f"🔍 Buscando en KB HÍBRIDA: query='{query_enriched}' top_k={top_k}")
    print(f"🔍 MCP URL: {mcp_url}/tools/kb_search_hybrid")
    print(f"🔍 Pesos: semantic=0.4, keyword=0.6")
    
    try:
        res = requests.post(f"{mcp_url}/tools/kb_search_hybrid", json=payload, timeout=30)
        print(f"🔍 Status KB: {res.status_code}")
        hits = res.json().get("hits", [])
        print(f"🔍 Hits encontrados: {len(hits)}")
        if hits:
            first_hit = hits[0]
            context_len = len(first_hit.get("context", ""))
            print(f"🔍 Primer hit: {first_hit.get('doc_id', 'N/A')} - score: {first_hit.get('score', 0):.3f} - context_len: {context_len}")
            # Mostrar scores híbridos si están disponibles
            if 'semantic_score' in first_hit and 'keyword_score' in first_hit:
                print(f"    └─ semantic: {first_hit['semantic_score']:.3f}, keyword: {first_hit['keyword_score']:.3f}")
            if 'error_codes_found' in first_hit:
                print(f"    └─ códigos detectados: {first_hit['error_codes_found']}")
    except Exception as e:
        print(f"❌ Error en búsqueda KB híbrida: {e}")
        # Fallback a kb_search_extended si híbrida falla
        try:
            print(f"🔄 Fallback a kb_search_extended...")
            payload_fallback = {
                "query": query_enriched,
                "top_k": top_k,
                "context_chars": 2000,
                "include_full_text": False
            }
            res = requests.post(f"{mcp_url}/tools/kb_search_extended", json=payload_fallback, timeout=10)
            hits = res.json().get("hits", [])
            print(f"🔍 Hits con fallback: {len(hits)}")
        except Exception as e2:
            print(f"❌ Error en fallback: {e2}")
            hits = []
    
    # POST-PROCESSING: Reranking para dar boost a documentos del modelo correcto
    if hits and model_normalized:
        print(f"🎯 Aplicando reranking para modelo: {model_normalized}")
        
        # Normalizar variantes del modelo para matching flexible
        model_variants = [
            model_normalized.lower().replace(" ", ""),  # "icombiclassic"
            model_normalized.lower().replace(" ", "_"),  # "icombi_classic"
            model_normalized.lower(),  # "icombi classic"
            model_normalized.replace(" ", ""),  # "iCombiClassic"
        ]
        
        reranked_hits = []
        for hit in hits:
            doc_id = hit.get("doc_id", "").lower()
            metadata = hit.get("metadata", {})
            model_meta = str(metadata.get("model", "")).lower()
            source_meta = str(metadata.get("source", "")).lower()
            
            # Verificar si el documento es del modelo correcto
            is_correct_model = any(
                variant in doc_id or variant in model_meta or variant in source_meta
                for variant in model_variants
            )
            
            # Aplicar boost al score
            original_score = hit.get("score", 0)
            if is_correct_model:
                hit["score"] = original_score * model_boost
                hit["model_boosted"] = True
                print(f"  ✅ Boost aplicado a: {hit.get('doc_id')[:60]} (score: {original_score:.3f} → {hit['score']:.3f})")
            
            reranked_hits.append(hit)
        
        # Reordenar por score (ahora con boost)
        hits = sorted(reranked_hits, key=lambda x: x.get("score", 0), reverse=True)
        print(f"🔄 Top 3 después de reranking:")
        for i, hit in enumerate(hits[:3], 1):
            boosted = "⭐" if hit.get("model_boosted") else "  "
            print(f"  {boosted}{i}. {hit.get('doc_id')[:60]} (score: {hit.get('score', 0):.3f})")
        
        # Limitar a top_k original después de reranking
        hits = hits[:top_k]
    
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
        raw = llm.complete_json(system_prompt, user_prompt)
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
