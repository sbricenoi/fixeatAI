"""Sistema de Scoring de Relevancia sin Alucinaciones.

Este módulo calcula la relevancia REAL de cada documento basándose en:
- Scores de búsqueda (keyword + semántica)
- Factores objetivos verificables
- NO usa predicciones del LLM que puedan alucinar
"""

from __future__ import annotations
from typing import Any, List, Dict
import re


def extract_error_codes(text: str) -> List[str]:
    """Extrae códigos de error de un texto.
    
    Args:
        text: Texto donde buscar códigos (query o contenido de documento)
        
    Returns:
        Lista de códigos encontrados (e.g., ["25", "42"])
    """
    patterns = [
        r'\bservice\s+(\d+)',
        r'\bservicio\s+(\d+)',
        r'\berror\s+(\d+)',
        r'\bS_?(\d+)',
        r'\bcódigo\s+(\d+)',
    ]
    
    codes = set()
    text_lower = text.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        codes.update(matches)
    
    return sorted(list(codes))


def detect_document_type(doc_id: str, metadata: Dict[str, Any]) -> str:
    """Detecta el tipo de documento basándose en ID y metadata.
    
    Args:
        doc_id: ID del documento
        metadata: Metadata del documento
        
    Returns:
        Tipo: "troubleshooting", "technical_manual", "installation", "other"
    """
    doc_id_lower = doc_id.lower()
    source = str(metadata.get("source", "")).lower()
    
    # Patrones para troubleshooting/error guides
    if any(x in doc_id_lower or x in source for x in [
        "et_", "error", "troubleshooting", "serviceref", 
        "service_guide", "fault", "diagnostic"
    ]):
        return "troubleshooting"
    
    # Manuales técnicos
    if any(x in doc_id_lower or x in source for x in [
        "_tm_", "technical", "manual", "training"
    ]):
        return "technical_manual"
    
    # Manuales de instalación
    if any(x in doc_id_lower or x in source for x in [
        "_im_", "installation", "mounting", "setup"
    ]):
        return "installation"
    
    return "other"


def calculate_relevance(
    hit: Dict[str, Any],
    query: str,
    target_model: str | None = None,
    query_error_codes: List[str] | None = None
) -> Dict[str, Any]:
    """Calcula la relevancia REAL de un documento sin alucinaciones.
    
    Este scoring es 100% basado en datos objetivos:
    - Scores de búsqueda (híbrida)
    - Matches exactos verificables
    - Tipo de documento
    - Metadata
    
    Args:
        hit: Resultado de búsqueda con score, doc_id, metadata, etc.
        query: Query original del usuario
        target_model: Modelo objetivo (e.g., "iCombi Classic")
        query_error_codes: Códigos de error en la query
        
    Returns:
        Dict con:
        - relevance_score: Score final (0-100)
        - confidence_label: "Muy Alta", "Alta", "Media", "Baja"
        - relevance_factors: Desglose de factores
    """
    # 1. Score base de búsqueda (normalizado a 0-100)
    base_score = hit.get("score", 0.0)
    
    # Normalizar score híbrido a rango 0-100
    # Los scores híbridos típicamente van de 0 a ~2.0 en casos extremos
    # AJUSTE: Reducir peso del score base para dar más importancia a los factores objetivos
    normalized_base = min(60, (base_score / 2.0) * 60)  # Máximo 60 puntos del score base
    
    # 2. Factores adicionales
    factors = {
        "base_search": normalized_base,
        "error_code_match": 0.0,
        "model_match": 0.0,
        "document_type_boost": 0.0,
        "keyword_strength": 0.0
    }
    
    doc_id = hit.get("doc_id", "")
    metadata = hit.get("metadata", {})
    content = hit.get("context", "") or hit.get("snippet", "")
    source = metadata.get("source", "")
    
    # 3. Match exacto de código de error (+20 puntos si hay match perfecto)
    if query_error_codes:
        # Buscar códigos en TODOS los campos disponibles
        search_text = f"{doc_id} {content} {source}"
        doc_error_codes = extract_error_codes(search_text)
        common_codes = set(query_error_codes) & set(doc_error_codes)
        
        if common_codes:
            # Match perfecto del código específico
            factors["error_code_match"] = 20.0
            print(f"    🎯 Match código {common_codes} en: {doc_id[:50]}")
    
    # 4. Match de modelo (+15 puntos)
    if target_model:
        model_variants = [
            target_model.lower().replace(" ", ""),
            target_model.lower().replace(" ", "_"),
            target_model.lower()
        ]
        
        doc_text = f"{doc_id} {metadata.get('model', '')} {metadata.get('source', '')}".lower()
        
        if any(variant in doc_text for variant in model_variants):
            factors["model_match"] = 15.0
    
    # 5. Boost por tipo de documento
    doc_type = detect_document_type(doc_id, metadata)
    
    type_boosts = {
        "troubleshooting": 15.0,  # Los más valiosos para diagnóstico
        "technical_manual": 10.0,
        "installation": 5.0,
        "other": 0.0
    }
    
    factors["document_type_boost"] = type_boosts.get(doc_type, 0.0)
    
    # 6. Fuerza del keyword matching (si disponible)
    keyword_score = hit.get("keyword_score", 0.0)
    if keyword_score > 0:
        # Keyword score alto indica match muy específico
        factors["keyword_strength"] = min(10.0, keyword_score * 10)
    
    # 7. Score final (suma de todos los factores, máximo 100)
    total_score = sum(factors.values())
    final_score = min(100.0, total_score)
    
    # 8. Etiqueta de confianza
    if final_score >= 80:
        confidence_label = "Muy Alta"
        confidence_emoji = "🎯"
    elif final_score >= 60:
        confidence_label = "Alta"
        confidence_emoji = "⭐"
    elif final_score >= 40:
        confidence_label = "Media"
        confidence_emoji = "📄"
    else:
        confidence_label = "Baja"
        confidence_emoji = "📝"
    
    return {
        "relevance_score": round(final_score, 1),
        "confidence_label": confidence_label,
        "confidence_emoji": confidence_emoji,
        "document_type": doc_type,
        "relevance_factors": {k: round(v, 1) for k, v in factors.items()},
        "has_error_code_match": factors["error_code_match"] > 0,
        "has_model_match": factors["model_match"] > 0,
    }


def rank_documents_by_relevance(
    hits: List[Dict[str, Any]],
    query: str,
    target_model: str | None = None
) -> List[Dict[str, Any]]:
    """Ordena documentos por relevancia calculada sin alucinaciones.
    
    Args:
        hits: Lista de resultados de búsqueda
        query: Query original
        target_model: Modelo objetivo (opcional)
        
    Returns:
        Lista de hits ordenados por relevance_score, enriquecidos con:
        - relevance_score (0-100)
        - confidence_label
        - relevance_factors
    """
    # Extraer códigos de error de la query una sola vez
    query_error_codes = extract_error_codes(query)
    
    # Calcular relevancia para cada hit
    enriched_hits = []
    for hit in hits:
        relevance_data = calculate_relevance(
            hit=hit,
            query=query,
            target_model=target_model,
            query_error_codes=query_error_codes
        )
        
        # Agregar datos de relevancia al hit
        enriched_hit = {**hit, **relevance_data}
        enriched_hits.append(enriched_hit)
    
    # Ordenar por relevance_score descendente
    sorted_hits = sorted(
        enriched_hits,
        key=lambda x: x["relevance_score"],
        reverse=True
    )
    
    return sorted_hits

