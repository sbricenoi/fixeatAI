"""LLM Re-ranker: Usa el LLM para analizar y ordenar documentos por relevancia real.

Este módulo implementa un segundo paso de análisis donde el LLM:
1. Recibe la query del usuario
2. Recibe todos los documentos candidatos encontrados en KB
3. Analiza semánticamente cuál documento responde mejor a la query
4. Retorna un ranking con scores de relevancia (0-100) y explicaciones
"""

from __future__ import annotations
from typing import Any, List, Dict
import json

from services.llm.client import LLMClient


def rerank_with_llm(
    query: str,
    candidates: List[Dict[str, Any]],
    model_name: str | None = None,
    marca: str | None = None,
    modelo: str | None = None,
    top_k: int = 8
) -> List[Dict[str, Any]]:
    """Usa el LLM para re-rankear documentos candidatos por relevancia real.
    
    El LLM analiza:
    - La query completa del usuario
    - El contenido de cada documento candidato
    - El contexto del equipo (marca, modelo)
    
    Y determina:
    - Qué documento responde mejor a la pregunta
    - Qué tan relevante es cada documento (0-100)
    - Por qué ese documento es relevante
    
    Args:
        query: Pregunta/problema del usuario
        candidates: Lista de documentos candidatos de KB search
        model_name: Nombre del modelo LLM a usar
        marca: Marca del equipo (opcional)
        modelo: Modelo del equipo (opcional)
        top_k: Número de documentos a retornar después del ranking
        
    Returns:
        Lista de documentos ordenados por relevancia según el LLM, enriquecidos con:
        - llm_relevance_score: Score de 0-100 determinado por el LLM
        - llm_explanation: Por qué el LLM considera este documento relevante
        - llm_confidence: Alta, Media, Baja
    """
    
    if not candidates:
        return []

    # Construir contexto para el LLM
    context_info = f"Marca: {marca or 'N/A'}, Modelo: {modelo or 'N/A'}"
    
    # Preparar resumen de documentos para el LLM
    documents_summary = []
    for idx, candidate in enumerate(candidates[:15], 1):  # Limitar a 15 para no saturar el LLM
        doc_id = candidate.get("doc_id", f"doc_{idx}")
        content = candidate.get("context") or candidate.get("snippet", "")
        page = candidate.get("metadata", {}).get("page", "N/A")
        source = candidate.get("metadata", {}).get("source", "")
        
        # Truncar contenido a 500 caracteres para reducir tokens
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        documents_summary.append({
            "id": idx,
            "doc_id": doc_id,
            "page": page,
            "source": source,
            "content": content_preview
        })
    
    # Prompt para el LLM
    system_prompt = """Eres un experto en diagnóstico de equipos industriales de cocina profesional.

Tu tarea es ANALIZAR documentos técnicos y determinar cuál responde MEJOR a la pregunta del usuario.

Debes:
1. Leer la pregunta del usuario cuidadosamente
2. Analizar cada documento candidato
3. Determinar qué documento contiene la información MÁS RELEVANTE para responder la pregunta
4. Asignar un score de relevancia de 0-100 a cada documento
5. Explicar brevemente POR QUÉ cada documento es relevante (o no)

CRITERIOS DE RELEVANCIA:
- 90-100: El documento responde DIRECTAMENTE la pregunta (ej. manual de troubleshooting del error específico)
- 70-89: El documento contiene información MUY relacionada pero no es específico
- 50-69: El documento tiene información relacionada pero parcial
- 30-49: El documento menciona el tema pero no es útil para resolver el problema
- 0-29: El documento NO es relevante para la pregunta

RETORNA un JSON con esta estructura EXACTA:
{
  "rankings": [
    {
      "id": 1,
      "relevance_score": 95,
      "confidence": "Alta",
      "explanation": "Este documento es el manual de troubleshooting específico para el error Service 25 en iCombi Classic."
    },
    {
      "id": 2,
      "relevance_score": 75,
      "confidence": "Media",
      "explanation": "Documento de referencia general que menciona errores de service, pero no es específico para el error 25."
    }
  ]
}

IMPORTANTE:
- Sé crítico: No todos los documentos son relevantes
- Si un documento NO responde la pregunta, dale un score bajo (0-40)
- Prioriza documentos de TROUBLESHOOTING sobre manuales de instalación
- Si la pregunta menciona un código de error específico (ej. "service 25"), prioriza documentos que mencionen ese código exacto
"""

    user_prompt = f"""**CONTEXTO DEL EQUIPO:**
{context_info}

**PREGUNTA DEL USUARIO:**
"{query}"

**DOCUMENTOS CANDIDATOS:**
{json.dumps(documents_summary, indent=2, ensure_ascii=False)}

Analiza cada documento y retorna el JSON con los rankings de relevancia."""

    # Llamar al LLM usando LLMClient (respeta LLM_BASE_URL y OPENAI_API_KEY)
    try:
        llm = LLMClient()
        print(f"🤖 Llamando LLM re-ranker ({llm._model})...")
        raw = llm.complete_json(system_prompt, user_prompt, force_json=True, max_tokens=2000)

        # Parsing robusto: extraer JSON aunque el LLM añada texto antes/después
        raw = (raw or "").strip()
        rankings_data: dict = {}
        if raw:
            try:
                rankings_data = json.loads(raw)
            except json.JSONDecodeError:
                start, end = raw.find("{"), raw.rfind("}")
                if start != -1 and end > start:
                    try:
                        rankings_data = json.loads(raw[start : end + 1])
                    except Exception:
                        pass
        rankings = rankings_data.get("rankings", [])
        
        print(f"✅ LLM re-ranker completado: {len(rankings)} documentos analizados")
        
        # Crear un mapa de rankings por ID
        rankings_map = {r["id"]: r for r in rankings}
        
        # Enriquecer documentos originales con scores del LLM
        enriched_candidates = []
        for idx, candidate in enumerate(candidates[:15], 1):
            ranking_info = rankings_map.get(idx, {
                "relevance_score": 0,
                "confidence": "Baja",
                "explanation": "No analizado por el LLM"
            })
            
            candidate["llm_relevance_score"] = ranking_info["relevance_score"]
            candidate["llm_confidence"] = ranking_info["confidence"]
            candidate["llm_explanation"] = ranking_info["explanation"]
            enriched_candidates.append(candidate)
        
        # Ordenar por score del LLM
        enriched_candidates.sort(
            key=lambda x: x.get("llm_relevance_score", 0),
            reverse=True
        )
        
        # Log de top 3
        print(f"🏆 Top 3 según LLM:")
        for i, doc in enumerate(enriched_candidates[:3], 1):
            doc_id = doc.get("doc_id", "N/A")[:50]
            score = doc.get("llm_relevance_score", 0)
            confidence = doc.get("llm_confidence", "N/A")
            print(f"  {i}. {doc_id} - {score}% ({confidence})")
        
        return enriched_candidates[:top_k]
        
    except Exception as e:
        print(f"❌ Error en LLM re-ranker: {e}")
        import traceback
        traceback.print_exc()
        return candidates[:top_k]


