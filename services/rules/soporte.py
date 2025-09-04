from __future__ import annotations

from typing import Any, Dict, List


def generar_pasos_soporte(equipo: Dict[str, Any], descripcion: str) -> List[Dict[str, Any]]:
    """Secuencia simple de pasos de diagnóstico/reparación."""

    pasos: List[Dict[str, Any]] = [
        {"orden": 1, "descripcion": "Verificar alimentación eléctrica", "tipo": "diagnostico"},
        {"orden": 2, "descripcion": "Inspección visual de conexiones y mangueras", "tipo": "diagnostico"},
    ]

    texto = f"{equipo.get('marca','')} {equipo.get('modelo','')} {descripcion}".lower()
    if "bomba" in texto or "obstru" in texto:
        pasos.append({"orden": 3, "descripcion": "Limpiar/Desobstruir línea de bomba", "tipo": "reparacion"})
    if "sensor" in texto and "temperatura" in texto:
        pasos.append({"orden": 3, "descripcion": "Probar y sustituir sensor de temperatura", "tipo": "reparacion"})

    # Asegurar orden consecutivo
    for i, p in enumerate(pasos, start=1):
        p["orden"] = i

    return pasos


