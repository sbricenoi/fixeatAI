from __future__ import annotations

import json
from typing import Any, Dict

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
        "es_valido": False,
        "inconsistencias": ["No se pudo interpretar la respuesta del modelo"],
        "correcciones_sugeridas": {},
        "feedback_coherencia": "Parsing error",
        "descripcion_mejorada": "",
    }


def validate_with_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Valida coherencia y mejora redacción usando LLM.

    Espera un payload con claves: cliente, equipo, descripcion_problema, campos_formulario.
    Devuelve el mismo esquema base de validación más `descripcion_mejorada`.
    """

    system_prompt = (
        "Eres un asistente de validación de formularios técnicos. Responde SOLO con JSON válido, en español, conforme a: "
        "{"
        '"es_valido": true,'
        '"inconsistencias": ["string"],'
        '"correcciones_sugeridas": {"campo":"valor_sugerido"},'
        '"feedback_coherencia": "string",'
        '"descripcion_mejorada": "string"'
        "}. "
        "Reglas: 1) No inventes datos; si falta información, sugiere pedirla. 2) Mantén nombres de campos simples. 3) Mejora la redacción de descripcion_problema sin cambiar el sentido."
    )

    user_prompt = (
        "Valida el siguiente formulario y mejora la redacción de la descripción del problema.\n\n"
        f"Formulario: {json.dumps(payload, ensure_ascii=False)}\n\n"
        "Devuelve SOLO el JSON solicitado."
    )

    llm = LLMClient()
    raw = llm.complete_json(system_prompt, user_prompt)
    data = _parse_json_safely(raw)
    return data


