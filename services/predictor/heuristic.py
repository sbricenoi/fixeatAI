from __future__ import annotations

from typing import Any, Dict, List


def infer_from_hits(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Genera "predicciones" simples a partir de los hits de la KB.

    - Extrae señales por palabras clave del snippet
    - Asigna una confianza proporcional al rank
    """

    results: List[Dict[str, Any]] = []
    for rank, h in enumerate(hits, start=1):
        snippet = (h.get("snippet") or "").lower()
        candidate: str | None = None
        if any(k in snippet for k in ["bomba", "obstru", "flujo"]):
            candidate = "Posible obstrucción en bomba/flujo"
        elif any(k in snippet for k in ["sensor", "temperatura"]):
            candidate = "Posible falla en sensor de temperatura"
        elif any(k in snippet for k in ["válvula", "valvula"]):
            candidate = "Posible válvula con fallo o bloqueo"

        if candidate:
            confidence = max(0.3, 1.0 - (rank - 1) * 0.15)
            results.append({
                "falla": candidate,
                "confidence": round(confidence, 2),
                "rationale": f"Derivado de fuente {h.get('doc_id')}",
            })

    # Devolver top-3 únicas por texto
    seen = set()
    unique: List[Dict[str, Any]] = []
    for r in results:
        key = r["falla"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
        if len(unique) >= 3:
            break

    return unique


def suggest_parts_and_tools(preds: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    parts: List[str] = []
    tools: List[str] = []
    for p in preds:
        name = p.get("falla", "").lower()
        if "bomba" in name or "flujo" in name:
            parts.append("Bomba/kit limpieza")
            tools.extend(["Multímetro", "Llave 12mm"])
        if "sensor" in name and "temperatura" in name:
            parts.append("Sensor de temperatura compatible")
            tools.append("Multímetro")
        if "válvula" in name or "valvula" in name:
            parts.append("Válvula de reemplazo")
            tools.append("Llave inglesa")
    return {"repuestos_sugeridos": list(dict.fromkeys(parts)), "herramientas_sugeridas": list(dict.fromkeys(tools))}


