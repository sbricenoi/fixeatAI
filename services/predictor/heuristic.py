"""Módulo de heurísticas mínimas como fallback cuando LLM no está disponible.

Este módulo proporciona análisis básico solo cuando:
- USE_LLM=false
- No hay conexión a LLM
- Error en el servicio LLM

El flujo principal debe usar el LLM con contexto de KB para análisis dinámico.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _get_safety_protocols() -> List[Dict[str, Any]]:
    """Retorna protocolos de seguridad estándar universales.
    
    Estos son aplicables a cualquier equipo industrial y no requieren
    conocimiento específico del dominio.
    """
    return [
        {
            "orden": 1,
            "descripcion": "Verificar que el equipo esté completamente apagado y desconectado de la fuente de alimentación eléctrica",
            "tipo": "seguridad"
        },
        {
            "orden": 2,
            "descripcion": "Usar equipo de protección personal (EPP): guantes, gafas de seguridad y calzado adecuado",
            "tipo": "seguridad"
        },
        {
            "orden": 3,
            "descripcion": "Verificar que no haya presión residual en el sistema (gas, agua, vapor)",
            "tipo": "seguridad"
        }
    ]


def _get_final_safety_step() -> Dict[str, Any]:
    """Retorna paso final de seguridad universal."""
    return {
        "descripcion": "Verificar que todas las conexiones estén seguras, reconectar alimentación y realizar prueba de funcionamiento supervisada",
        "tipo": "seguridad"
    }


def _get_minimal_diagnostic_steps(problem_description: str = "") -> List[Dict[str, Any]]:
    """Genera pasos de diagnóstico mínimos basados en la descripción del problema.
    
    Estos son pasos generales aplicables a cualquier equipo.
    """
    steps = [
        {
            "descripcion": "Inspección visual completa del equipo en busca de daños evidentes, fugas o componentes sueltos",
            "tipo": "diagnostico"
        },
        {
            "descripcion": "Verificar alimentación eléctrica, fusibles y conexiones principales con multímetro",
            "tipo": "diagnostico"
        },
        {
            "descripcion": "Revisar el manual del fabricante para códigos de error específicos (si aplica)",
            "tipo": "diagnostico"
        }
    ]
    
    # Agregar paso específico si hay descripción
    if problem_description and len(problem_description) > 10:
        steps.append({
            "descripcion": f"Investigar específicamente: {problem_description[:100]}",
            "tipo": "diagnostico"
        })
    
    return steps


def _build_minimal_failure_prediction(hits: List[Dict[str, Any]], description: str) -> Dict[str, Any]:
    """Construye una predicción mínima basada solo en el contexto disponible.
    
    No usa diccionarios estáticos. Confía en que el LLM hará el análisis real.
    """
    num_hits = len(hits)
    
    # Determinar confianza basada en cantidad de contexto
    if num_hits == 0:
        confidence = 0.2
        rationale = "Sin documentación disponible en KB. Se recomienda consultar manual del fabricante."
        falla_desc = "Información insuficiente para diagnóstico preciso"
    elif num_hits < 3:
        confidence = 0.4
        rationale = f"Análisis basado en {num_hits} documento(s) de la KB. Contexto limitado."
        falla_desc = f"Posible problema: {description[:80] if description else 'requiere inspección técnica'}"
    else:
        confidence = 0.6
        rationale = f"Análisis heurístico basado en {num_hits} documentos relevantes de la KB."
        falla_desc = f"Problema detectado: {description[:80] if description else 'requiere análisis detallado'}"
    
    # Construir pasos con protocolos de seguridad
    safety_start = _get_safety_protocols()
    diagnostic_steps = _get_minimal_diagnostic_steps(description)
    safety_end = _get_final_safety_step()
    
    # Combinar todos los pasos
    all_steps = safety_start + diagnostic_steps
    final_order = len(all_steps) + 1
    safety_end["orden"] = final_order
    all_steps.append(safety_end)
    
    # Renumerar consecutivamente
    for idx, step in enumerate(all_steps, start=1):
        step["orden"] = idx
    
    # Herramientas básicas universales
    basic_tools = ["Multímetro", "Destornilladores", "Llaves mixtas", "Linterna"]
    
    return {
        "falla": falla_desc,
        "confidence": round(confidence, 2),
        "rationale": rationale,
        "repuestos_sugeridos": [],  # El LLM debe determinar esto del contexto real
        "herramientas_sugeridas": basic_tools,
        "pasos": all_steps
    }


def infer_from_hits(hits: List[Dict[str, Any]], description: str = "") -> List[Dict[str, Any]]:
    """Genera predicción mínima de fallback cuando LLM no está disponible.
    
    IMPORTANTE: Esta función es solo un FALLBACK. El flujo principal debe:
    1. Recuperar contexto de KB con embeddings semánticos
    2. Enviar al LLM para análisis real del contenido de los manuales
    3. El LLM extrae fallas, repuestos y pasos del contenido real
    
    Esta función NO debe ser la fuente principal de inteligencia del sistema.
    
    Args:
        hits: Resultados de búsqueda semántica en KB
        description: Descripción del problema reportado
        
    Returns:
        Lista con una predicción mínima que incluye protocolos de seguridad
    """
    prediction = _build_minimal_failure_prediction(hits, description)
    return [prediction]


def suggest_parts_and_tools(preds: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, List[str]]:
    """Función de compatibilidad hacia atrás.
    
    La nueva estructura incluye repuestos y herramientas dentro de cada falla.
    Esta función extrae y agrega para mantener compatibilidad con código legacy.
    """
    all_parts = []
    all_tools = []
    
    for pred in preds:
        all_parts.extend(pred.get("repuestos_sugeridos", []))
        all_tools.extend(pred.get("herramientas_sugeridas", []))
    
    # Remover duplicados manteniendo orden
    unique_parts = list(dict.fromkeys(all_parts))
    unique_tools = list(dict.fromkeys(all_tools))
    
    return {
        "repuestos_sugeridos": unique_parts[:10],
        "herramientas_sugeridas": unique_tools[:10]
    }


# Funciones legacy mantenidas para compatibilidad pero simplificadas
def _analyze_failure_context(hits: List[Dict[str, Any]], description: str = "") -> Dict[str, Any]:
    """Análisis de contexto simplificado.
    
    Solo cuenta elementos básicos sin patrones estáticos.
    El LLM debe hacer el análisis real del contenido.
    """
    all_text = description + " " + " ".join(h.get("snippet", "") for h in hits)
    
    return {
        "evidence_strength": len(hits),
        "text_length": len(all_text),
        "has_description": bool(description and len(description) > 10)
    }
