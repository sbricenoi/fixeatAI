from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List


def validar_formulario(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Valida coherencia básica del formulario y sugiere correcciones.

    Reglas MVP: fechas válidas y en rango, ejemplo de lectura de temperatura.
    """

    inconsistencias: List[Dict[str, str]] = []
    correcciones: Dict[str, Any] = {}

    campos = payload.get("campos_formulario", {})

    # Validación de fecha_visita
    fecha_visita = campos.get("fecha_visita")
    if isinstance(fecha_visita, str):
        try:
            dt = datetime.strptime(fecha_visita, "%Y-%m-%d").date()
            if dt > date.today():
                inconsistencias.append({
                    "campo": "fecha_visita",
                    "tipo": "coherencia",
                    "detalle": "fecha en el futuro"
                })
        except ValueError:
            inconsistencias.append({
                "campo": "fecha_visita",
                "tipo": "formato",
                "detalle": "usar YYYY-MM-DD"
            })

    # Rango ejemplo: lectura de temperatura 2..8
    temp = campos.get("lectura_temperatura")
    if isinstance(temp, (int, float)):
        if not (2 <= float(temp) <= 8):
            inconsistencias.append({
                "campo": "lectura_temperatura",
                "tipo": "rango",
                "detalle": "fuera de rango esperado 2-8C"
            })
            correcciones["lectura_temperatura"] = 6.0

    es_valido = len(inconsistencias) == 0
    return {
        "es_valido": es_valido,
        "inconsistencias": inconsistencias,
        "correcciones_sugeridas": correcciones,
        "feedback_coherencia": "OK" if es_valido else "Revisar inconsistencias"
    }


