from __future__ import annotations

from typing import Any, Dict, List


def inferir_fallas_probables(equipo: Dict[str, Any], descripcion: str) -> List[Dict[str, Any]]:
    """Reglas simples para inferir fallas probables a partir del texto y equipo.

    MVP: heurísticas básicas. En el futuro, reemplazar/combinar con modelos.
    """

    texto = f"{equipo.get('marca','')} {equipo.get('modelo','')} {descripcion}".lower()
    resultados: List[Dict[str, Any]] = []

    if "bomba" in texto or "obstru" in texto:
        resultados.append({
            "falla": "Bomba obstruida",
            "confidence": 0.7,
            "rationale": "Mención de bomba/obstrucción en descripción"
        })

    if "sensor" in texto and "temperatura" in texto:
        resultados.append({
            "falla": "Sensor de temperatura defectuoso",
            "confidence": 0.6,
            "rationale": "Referencia a sensor de temperatura"
        })

    if not resultados:
        resultados.append({
            "falla": "Falla no determinada",
            "confidence": 0.3,
            "rationale": "Sin coincidencias en reglas"
        })

    return resultados


def sugerir_repuestos_y_herramientas(fallas: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    repuestos: List[str] = []
    herramientas: List[str] = []

    for f in fallas:
        nombre = f.get("falla", "").lower()
        if "bomba" in nombre:
            repuestos.append("Bomba A123")
            herramientas.extend(["Multímetro", "Llave 12mm"])
        if "sensor" in nombre:
            repuestos.append("Sensor T-900")
            herramientas.append("Multímetro")

    # de-duplicar manteniendo orden
    repuestos = list(dict.fromkeys(repuestos))
    herramientas = list(dict.fromkeys(herramientas))
    return {"repuestos_sugeridos": repuestos, "herramientas_sugeridas": herramientas}


