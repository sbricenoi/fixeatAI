from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple
from collections import Counter


def _extract_technical_patterns(text: str) -> Dict[str, List[str]]:
    """Extrae patrones técnicos del texto usando análisis contextual."""
    if not text:
        return {"symptoms": [], "parts": [], "actions": []}
    
    text_lower = text.lower()
    
    # Patrones de síntomas (más específicos)
    symptom_patterns = {
        r"no\s+(enciende|prende|funciona)": "No enciende",
        r"(ruido|sonido)\s+(mecánico|extraño|anormal)": "Ruido mecánico anormal",
        r"(falla|problema|error)\s+(temperatura|temp)": "Problema de temperatura",
        r"(filtración|fuga|goteo)": "Filtración detectada",
        r"(trabado|bloqueado|atascado)": "Mecanismo trabado",
        r"(descompensado|desbalanceado|disparejo)": "Funcionamiento irregular",
        r"(cortocircuito|corto\s+circuito)": "Cortocircuito eléctrico",
        r"(sobrecalentamiento|muy\s+caliente)": "Sobrecalentamiento",
        r"(vibracion|vibración)\s+(excesiva|anormal)": "Vibración excesiva",
        r"(pantalla|display)\s+(negra|apagada|error)": "Falla en display",
        r"(presión|presion)\s+(baja|alta|incorrecta)": "Problema de presión",
        r"(conexión|contacto)\s+(suelta|mala|defectuosa)": "Conexión defectuosa"
    }
    
    # Patrones de componentes
    component_patterns = {
        r"\b(bomba|pump)\b": "bomba",
        r"\b(sensor|sonda|termocupla)\b": "sensor",
        r"\b(válvula|valvula|valve)\b": "válvula",
        r"\b(motor|engine)\b": "motor",
        r"\b(correa|belt|banda)\b": "correa",
        r"\b(cadena|chain)\b": "cadena",
        r"\b(piñón|piñon|engranaje|gear)\b": "piñón",
        r"\b(resistencia|heating element)\b": "resistencia",
        r"\b(fusible|fuse)\b": "fusible",
        r"\b(filtro|filter)\b": "filtro",
        r"\b(quemador|burner|inyector)\b": "quemador",
        r"\b(ventilador|fan)\b": "ventilador",
        r"\b(termostato|thermostat)\b": "termostato",
        r"\b(contactor|relay|relé)\b": "contactor",
        r"\b(junta|gasket|burlete)\b": "junta",
        r"\b(manguera|hose|tubo)\b": "manguera",
        r"\b(electrodo|electrode|chispero)\b": "electrodo",
        r"\b(rodamiento|bearing|cojinete)\b": "rodamiento",
        r"\b(tarjeta|pcb|placa|card)\b": "tarjeta",
        r"\b(pantalla|display|panel)\b": "pantalla",
        r"\b(manilla|handle|manija)\b": "manilla",
        r"\b(puerta|door|tapa)\b": "puerta",
        r"\b(gozne|hinge|bisagra)\b": "gozne",
        r"\b(desagüe|desague|drain)\b": "desagüe"
    }
    
    # Patrones de acciones técnicas
    action_patterns = {
        r"(cambiar|cambio|reemplazar|reemplazo)": "cambio",
        r"(reparar|reparación|arreglar)": "reparación",
        r"(limpiar|limpieza)": "limpieza",
        r"(regular|regulación|ajustar|ajuste)": "regulación",
        r"(lubricar|lubricación|engrasar)": "lubricación",
        r"(revisar|revisión|inspeccionar)": "revisión",
        r"(calibrar|calibración)": "calibración",
        r"(soldar|soldadura)": "soldadura",
        r"(apretar|reaprete|tensar)": "reaprete",
        r"(medir|medición)": "medición"
    }
    
    results = {"symptoms": [], "parts": [], "actions": []}
    
    # Extraer síntomas
    for pattern, symptom in symptom_patterns.items():
        if re.search(pattern, text_lower):
            results["symptoms"].append(symptom)
    
    # Extraer componentes
    for pattern, component in component_patterns.items():
        if re.search(pattern, text_lower):
            results["parts"].append(component)
    
    # Extraer acciones
    for pattern, action in action_patterns.items():
        if re.search(pattern, text_lower):
            results["actions"].append(action)
    
    return results


def _analyze_failure_context(hits: List[Dict[str, Any]], description: str = "") -> Dict[str, Any]:
    """Analiza el contexto de fallas combinando KB hits y descripción."""
    all_text = description + " " + " ".join(h.get("snippet", "") for h in hits)
    patterns = _extract_technical_patterns(all_text)
    
    # Contar frecuencias para determinar patrones dominantes
    symptom_freq = Counter(patterns["symptoms"])
    part_freq = Counter(patterns["parts"])
    action_freq = Counter(patterns["actions"])
    
    # Calcular contexto de falla basado en evidencia
    context = {
        "primary_symptoms": [s for s, c in symptom_freq.most_common(3)],
        "affected_parts": [p for p, c in part_freq.most_common(5)],
        "recommended_actions": [a for a, c in action_freq.most_common(3)],
        "evidence_strength": len(hits),
        "text_length": len(all_text)
    }
    
    return context


def _generate_intelligent_failure_predictions(context: Dict[str, Any], hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Genera predicciones inteligentes basadas en análisis contextual."""
    predictions = []
    
    symptoms = context.get("primary_symptoms", [])
    parts = context.get("affected_parts", [])
    evidence_strength = context.get("evidence_strength", 0)
    
    # Mapeo de síntomas a fallas específicas con lógica mejorada
    failure_mapping = {
        "No enciende": {
            "electrical": ["fusible", "contactor", "tarjeta", "resistencia"],
            "mechanical": ["motor", "sensor"],
            "base_confidence": 0.8
        },
        "Ruido mecánico anormal": {
            "mechanical": ["rodamiento", "piñón", "cadena", "correa", "motor"],
            "base_confidence": 0.85
        },
        "Problema de temperatura": {
            "thermal": ["sensor", "termostato", "resistencia", "quemador"],
            "base_confidence": 0.9
        },
        "Filtración detectada": {
            "sealing": ["junta", "manguera", "válvula", "desagüe"],
            "base_confidence": 0.75
        },
        "Mecanismo trabado": {
            "mechanical": ["cadena", "piñón", "rodamiento", "correa"],
            "base_confidence": 0.8
        },
        "Funcionamiento irregular": {
            "control": ["sensor", "tarjeta", "termostato"],
            "mechanical": ["motor", "rodamiento"],
            "base_confidence": 0.7
        },
        "Cortocircuito eléctrico": {
            "electrical": ["fusible", "tarjeta", "contactor", "resistencia"],
            "base_confidence": 0.95
        },
        "Falla en display": {
            "electronic": ["pantalla", "tarjeta"],
            "base_confidence": 0.9
        }
    }
    
    # Generar predicciones basadas en síntomas y partes encontradas
    for symptom in symptoms:
        if symptom in failure_mapping:
            mapping = failure_mapping[symptom]
            base_conf = mapping["base_confidence"]
            
            # Encontrar intersección entre partes mencionadas y partes relevantes
            relevant_parts = []
            for category, category_parts in mapping.items():
                if category != "base_confidence":
                    relevant_parts.extend(category_parts)
            
            intersect_parts = [p for p in parts if p in relevant_parts]
            
            if intersect_parts:
                # Falla específica con partes identificadas
                part_list = ", ".join(intersect_parts)
                confidence = min(base_conf + 0.1, 0.95)
                failure_desc = f"{symptom} - posible falla en {part_list}"
            else:
                # Falla general sin partes específicas
                confidence = base_conf * 0.8
                failure_desc = symptom
            
            # Ajustar confianza basada en evidencia
            if evidence_strength > 3:
                confidence = min(confidence + 0.05, 0.95)
            elif evidence_strength < 2:
                confidence = max(confidence - 0.15, 0.3)
            
            # Buscar rationale específico en los hits
            rationale_sources = []
            for i, hit in enumerate(hits[:3]):
                if any(part in hit.get("snippet", "").lower() for part in intersect_parts):
                    rationale_sources.append(hit.get("doc_id", f"source_{i}"))
            
            if not rationale_sources:
                rationale_sources = [h.get("doc_id", "unknown") for h in hits[:2]]
            
            rationale = f"Basado en análisis contextual. Fuentes: {', '.join(rationale_sources[:2])}"
            
            predictions.append({
                "falla": failure_desc,
                "confidence": round(confidence, 2),
                "rationale": rationale
            })
    
    # Si no hay síntomas específicos, usar análisis de partes directamente
    if not predictions and parts:
        common_parts = parts[:3]
        confidence = 0.6 if evidence_strength > 2 else 0.4
        
        failure_desc = f"Posible problema en componentes: {', '.join(common_parts)}"
        rationale = f"Basado en análisis de componentes mencionados. Fuentes: {len(hits)} documentos"
        
        predictions.append({
            "falla": failure_desc,
            "confidence": round(confidence, 2),
            "rationale": rationale
        })
    
    # Limitar a top 4 predicciones y ordenar por confianza
    predictions = sorted(predictions, key=lambda x: x["confidence"], reverse=True)[:4]
    
    return predictions


def _suggest_intelligent_parts_and_tools(predictions: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, List[str]]:
    """Sugiere repuestos y herramientas basado en predicciones inteligentes."""
    
    # Mapeo de componentes a repuestos específicos
    parts_mapping = {
        "bomba": ["Kit de reparación de bomba", "Bomba de repuesto"],
        "sensor": ["Sensor de temperatura", "Termocupla"],
        "válvula": ["Válvula solenoide", "Kit de válvula"],
        "motor": ["Motor de repuesto", "Escobillas de motor"],
        "correa": ["Correa de transmisión", "Tensor de correa"],
        "cadena": ["Cadena de transmisión", "Eslabones de cadena"],
        "piñón": ["Piñón de repuesto", "Kit de engranajes"],
        "resistencia": ["Resistencia calefactora", "Elemento calefactor"],
        "fusible": ["Fusibles de repuesto", "Portafusibles"],
        "filtro": ["Filtro de repuesto", "Kit de filtros"],
        "quemador": ["Quemador completo", "Inyectores"],
        "ventilador": ["Motor de ventilador", "Aspas de ventilador"],
        "termostato": ["Termostato de repuesto", "Bulbo termostático"],
        "contactor": ["Contactor eléctrico", "Relé de control"],
        "junta": ["Junta de repuesto", "Kit de juntas"],
        "manguera": ["Manguera de repuesto", "Abrazaderas"],
        "electrodo": ["Electrodo de encendido", "Cable de electrodo"],
        "rodamiento": ["Rodamiento de bolas", "Kit de rodamientos"],
        "tarjeta": ["Tarjeta electrónica", "PCB de control"],
        "pantalla": ["Display LCD", "Panel de control"],
        "manilla": ["Manilla de puerta", "Kit de manilla"],
        "puerta": ["Junta de puerta", "Bisagras de puerta"],
        "gozne": ["Gozne de puerta", "Kit de bisagras"],
        "desagüe": ["Kit de desagüe", "Manguera de desagüe"]
    }
    
    # Mapeo de componentes a herramientas necesarias
    tools_mapping = {
        "bomba": ["Multímetro", "Llaves Allen", "Destornilladores"],
        "sensor": ["Multímetro", "Tester de temperatura"],
        "válvula": ["Llave inglesa", "Destornilladores"],
        "motor": ["Multímetro", "Llaves mixtas", "Destornilladores"],
        "correa": ["Llaves Allen", "Tensor de correa"],
        "cadena": ["Llaves Allen", "Lubricante", "Limpiador"],
        "piñón": ["Llaves Allen", "Extractor de piñones"],
        "resistencia": ["Multímetro", "Destornilladores", "Tester de continuidad"],
        "fusible": ["Multímetro", "Alicate"],
        "filtro": ["Destornilladores", "Llaves"],
        "quemador": ["Llaves mixtas", "Destornilladores", "Manómetro"],
        "ventilador": ["Destornilladores", "Multímetro"],
        "termostato": ["Multímetro", "Destornilladores"],
        "contactor": ["Multímetro", "Destornilladores"],
        "junta": ["Raspador de juntas", "Sellador"],
        "manguera": ["Cortador de manguera", "Abrazaderas"],
        "electrodo": ["Multímetro", "Destornilladores"],
        "rodamiento": ["Extractor de rodamientos", "Prensa"],
        "tarjeta": ["Destornilladores", "Multímetro", "Antiestático"],
        "pantalla": ["Destornilladores"],
        "manilla": ["Destornilladores", "Llaves Allen"],
        "puerta": ["Destornilladores", "Llaves Allen"],
        "gozne": ["Destornilladores", "Lubricante"],
        "desagüe": ["Destornilladores", "Sellador"]
    }
    
    suggested_parts = []
    suggested_tools = []
    
    # Extraer componentes de las predicciones
    affected_parts = context.get("affected_parts", [])
    
    for part in affected_parts:
        if part in parts_mapping:
            suggested_parts.extend(parts_mapping[part])
        if part in tools_mapping:
            suggested_tools.extend(tools_mapping[part])
    
    # Herramientas básicas siempre útiles
    basic_tools = ["Multímetro", "Destornilladores", "Llaves mixtas"]
    suggested_tools.extend(basic_tools)
    
    # Remover duplicados manteniendo orden
    unique_parts = list(dict.fromkeys(suggested_parts))
    unique_tools = list(dict.fromkeys(suggested_tools))
    
    return {
        "repuestos_sugeridos": unique_parts[:6],  # Máximo 6 repuestos
        "herramientas_sugeridas": unique_tools[:8]  # Máximo 8 herramientas
    }


def infer_from_hits(hits: List[Dict[str, Any]], description: str = "") -> List[Dict[str, Any]]:
    """Genera predicciones inteligentes a partir de los hits de la KB y descripción del problema.
    
    Reemplaza la lógica simplista anterior con análisis contextual profundo.
    """
    if not hits and not description:
        return []
    
    # Análisis contextual
    context = _analyze_failure_context(hits, description)
    
    # Generar predicciones inteligentes
    predictions = _generate_intelligent_failure_predictions(context, hits)
    
    return predictions


def suggest_parts_and_tools(preds: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, List[str]]:
    """Sugiere repuestos y herramientas basado en predicciones y contexto."""
    if context is None:
        # Fallback para compatibilidad
        context = {"affected_parts": []}
        for pred in preds:
            falla = pred.get("falla", "").lower()
            # Extraer partes mencionadas de las fallas
            if "bomba" in falla:
                context["affected_parts"].append("bomba")
            if "sensor" in falla:
                context["affected_parts"].append("sensor")
            if "válvula" in falla:
                context["affected_parts"].append("válvula")
            if "motor" in falla:
                context["affected_parts"].append("motor")
    
    return _suggest_intelligent_parts_and_tools(preds, context)


