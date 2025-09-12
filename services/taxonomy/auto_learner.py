"""
Auto-aprendizaje de taxonomía usando análisis híbrido LLM + heurísticas.

Sistema que:
1. Extrae máximo valor de cada documento técnico
2. Previene fugas de información sensible
3. Valida calidad con múltiples capas
4. Auto-expande taxonomía sin intervención manual
"""

from __future__ import annotations

import re
import json
import hashlib
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime

from services.llm.client import LLMClient


@dataclass
class EntityCandidate:
    """Candidato a entidad con métricas de calidad."""
    value: str
    category: str  # brand, model, category
    confidence: float
    frequency: int
    context_snippets: List[str]
    validation_source: str  # heuristic, llm, pattern


class TaxonomyAutoLearner:
    """Auto-aprendizaje inteligente de taxonomía con máxima extracción de valor."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient(agent="taxonomy")
        self.confidence_threshold = 0.7
        self.min_frequency = 2
        self.sensitive_patterns = self._load_sensitive_patterns()
        
    def _load_sensitive_patterns(self) -> List[str]:
        """Patrones para detectar y filtrar información sensible."""
        return [
            r"\b\d{1,2}[.-]\d{3}[.-]\d{3}[-k]\b",  # RUT chileno
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",  # emails
            r"\b\+?56\s?9\s?\d{8}\b",  # teléfonos chilenos
            r"\b\d{4,16}\b(?=.*tarjeta|card|visa|master)",  # números de tarjeta
            r"\bserie[:\s]+[a-z0-9\-\.]{10,}\b",  # números de serie largos
            r"\bclave[:\s]+\w+\b",  # claves/passwords
            r"\btoken[:\s]+\w+\b",  # tokens
        ]
    
    def sanitize_text(self, text: str) -> str:
        """Sanitiza texto removiendo información sensible."""
        sanitized = text
        
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, "[SANITIZADO]", sanitized, flags=re.IGNORECASE)
        
        # Remover direcciones específicas manteniendo información técnica
        sanitized = re.sub(r"\b[A-Z][a-z]+\s+\d+", "[DIRECCION]", sanitized)
        
        return sanitized
    
    def extract_comprehensive_entities(self, text: str, document_id: str = "") -> Dict[str, List[EntityCandidate]]:
        """Extracción exhaustiva de entidades con múltiples estrategias."""
        
        # Sanitizar antes de procesar
        safe_text = self.sanitize_text(text)
        
        candidates = {
            "brands": [],
            "models": [],
            "categories": []
        }
        
        # 1. Extracción heurística de alta precisión
        heuristic_entities = self._extract_heuristic_entities(safe_text)
        
        # 2. Extracción por patrones contextuales específicos
        pattern_entities = self._extract_pattern_entities(safe_text)
        
        # 3. Merge y validación
        merged = self._merge_entity_sources(heuristic_entities, pattern_entities)
        
        # 4. Conversión a EntityCandidates con métricas
        for category, entities in merged.items():
            for entity, data in entities.items():
                candidate = EntityCandidate(
                    value=entity,
                    category=category,
                    confidence=data["confidence"],
                    frequency=data["frequency"],
                    context_snippets=data["contexts"][:3],  # Top 3 contextos
                    validation_source=data["source"]
                )
                candidates[category].append(candidate)
        
        return candidates
    
    def _extract_heuristic_entities(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Extracción heurística de alta precisión basada en patrones técnicos."""
        
        entities = {
            "brands": defaultdict(lambda: {"confidence": 0.0, "frequency": 0, "contexts": [], "source": "heuristic"}),
            "models": defaultdict(lambda: {"confidence": 0.0, "frequency": 0, "contexts": [], "source": "heuristic"}),
            "categories": defaultdict(lambda: {"confidence": 0.0, "frequency": 0, "contexts": [], "source": "heuristic"})
        }
        
        # Patrones de marcas con contexto técnico específico
        brand_patterns = [
            # Patrones explícitos con contexto
            (r"(?:LAMINADORA\s+SOBREMESÓN\s+|HORNO\s+ROTATORIO\s+|DIVISORA\s+OVILLADORA\s+)([A-Z][A-Z0-9\s]+?)(?:,\s+MOD\.)", 0.95),
            (r"(?:marca|fabricante)[:\s]+([A-Z][A-Z0-9\s]+?)(?:\s+MOD\.|\s+modelo|\s*,)", 0.9),
            (r"equipo[:\s]+([A-Z][A-Z0-9\s]+?)(?:\s+MOD\.|\s+modelo)", 0.85),
            # Patrones con equipos específicos
            (r"(?:HORNO|LAMINADORA|DIVISORA|AMASADORA|BATIDORA)\s+[A-Z\s]*?\b([A-Z]{3,}[A-Z0-9\s]*?)(?:\s+MOD\.|\s*,)", 0.8),
            # Patrones de marcas conocidas con variaciones
            (r"\b(SINMAG|ZUCCHELLI|FUTURE\s+TRIMA|RATIONAL|UNOX|UNIQUE|LAGUNA|KOLB)\b", 0.95),
        ]
        
        # Patrones de modelos técnicos
        model_patterns = [
            # Modelos específicos con formato técnico
            (r"MOD\.\s*([A-Z0-9\-\s]+?)(?:\s*,|\s*\(|\s*RODILLO|\s*$)", 0.95),
            (r"modelo[:\s]+([A-Z0-9\-]+)", 0.9),
            (r"\b(SM-\d+|UHP?\d+|PRIMA\s+EVO\s+KE\s+\d+|MINIFANTON\s+\d+X\d+[A-Z]?)\b", 0.95),
            (r"serie[:\s]+([A-Z0-9\.]+)", 0.8),
            # Patrones de dimensiones como modelos
            (r"\b(\d{2}X\d{2}[A-Z]?)\b(?=.*(?:HORNO|LAMINADORA))", 0.7),
        ]
        
        # Patrones de categorías de equipos
        category_patterns = [
            # Categorías explícitas con contexto
            (r"\b(LAMINADORA\s+SOBREMESÓN|HORNO\s+ROTATORIO|DIVISORA\s+OVILLADORA|HORNO\s+DE\s+PISO)\b", 0.95),
            (r"\b(laminadora|horno|divisora|ovilladora|amasadora|batidora|freidora|plancha)\b", 0.8),
            (r"Equipo:\s+([A-Z][a-z]+)", 0.9),  # Del formato "Equipo: Laminadora"
        ]
        
        # Procesar patrones de marcas
        for pattern, confidence in brand_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                brand = match.group(1).strip().upper()
                if self._is_valid_brand(brand):
                    context = self._extract_context(text, match.start(), match.end())
                    entities["brands"][brand]["confidence"] = max(entities["brands"][brand]["confidence"], confidence)
                    entities["brands"][brand]["frequency"] += 1
                    entities["brands"][brand]["contexts"].append(context)
        
        # Procesar patrones de modelos
        for pattern, confidence in model_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                model = match.group(1).strip().upper()
                if self._is_valid_model(model):
                    context = self._extract_context(text, match.start(), match.end())
                    entities["models"][model]["confidence"] = max(entities["models"][model]["confidence"], confidence)
                    entities["models"][model]["frequency"] += 1
                    entities["models"][model]["contexts"].append(context)
        
        # Procesar patrones de categorías
        for pattern, confidence in category_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                category = match.group(1).strip().lower()
                category = self._normalize_category(category)
                if category:
                    context = self._extract_context(text, match.start(), match.end())
                    entities["categories"][category]["confidence"] = max(entities["categories"][category]["confidence"], confidence)
                    entities["categories"][category]["frequency"] += 1
                    entities["categories"][category]["contexts"].append(context)
        
        return entities
    
    def _extract_pattern_entities(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Extracción adicional por patrones contextuales específicos."""
        
        entities = {
            "brands": defaultdict(lambda: {"confidence": 0.0, "frequency": 0, "contexts": [], "source": "pattern"}),
            "models": defaultdict(lambda: {"confidence": 0.0, "frequency": 0, "contexts": [], "source": "pattern"}),
            "categories": defaultdict(lambda: {"confidence": 0.0, "frequency": 0, "contexts": [], "source": "pattern"})
        }
        
        # Búsqueda de marcas en líneas de especificación técnica
        spec_lines = [line.strip() for line in text.split('\n') if any(keyword in line.upper() for keyword in ['MOD.', 'MODELO', 'MARCA', 'EQUIPO'])]
        
        for line in spec_lines:
            # Extraer marca de líneas técnicas
            brand_match = re.search(r'\b([A-Z]{3,}[A-Z0-9\s]*?)\b(?=.*MOD\.)', line)
            if brand_match and self._is_valid_brand(brand_match.group(1)):
                brand = brand_match.group(1).strip()
                entities["brands"][brand]["confidence"] = 0.85
                entities["brands"][brand]["frequency"] += 1
                entities["brands"][brand]["contexts"].append(line[:100])
            
            # Extraer modelo de líneas técnicas
            model_match = re.search(r'MOD\.\s*([A-Z0-9\-\s]+?)(?:\s*,|\s*\(|$)', line)
            if model_match and self._is_valid_model(model_match.group(1)):
                model = model_match.group(1).strip()
                entities["models"][model]["confidence"] = 0.9
                entities["models"][model]["frequency"] += 1
                entities["models"][model]["contexts"].append(line[:100])
        
        return entities
    
    def _is_valid_brand(self, brand: str) -> bool:
        """Valida si un candidato es una marca válida."""
        if not brand or len(brand) < 2:
            return False
        
        # Filtrar palabras comunes que no son marcas
        invalid_brands = {
            "GENERICO", "GENERAL", "EQUIPO", "MODELO", "MARCA", "FABRICANTE",
            "SERVICIO", "CLIENTE", "LOCAL", "COMUNA", "DIRECCION", "TELEFONO",
            "EMAIL", "CARGO", "ADMIN", "TECNICO", "HORA", "FECHA", "BITACORA"
        }
        
        if brand.upper() in invalid_brands:
            return False
        
        # Debe contener al menos una letra
        if not re.search(r'[A-Z]', brand):
            return False
        
        # No debe ser solo números
        if re.match(r'^\d+$', brand):
            return False
        
        return True
    
    def _is_valid_model(self, model: str) -> bool:
        """Valida si un candidato es un modelo válido."""
        if not model or len(model) < 2:
            return False
        
        # Debe tener formato técnico (letras + números o guiones)
        if not re.search(r'[A-Z0-9]', model):
            return False
        
        # Filtrar modelos inválidos
        if model.upper() in ["GENERICO", "N/A", "SIN", "CON"]:
            return False
        
        return True
    
    def _normalize_category(self, category: str) -> Optional[str]:
        """Normaliza categorías a formas canónicas."""
        category = category.lower().strip()
        
        # Mapeo de normalizaciones
        normalizations = {
            "laminadora sobremesón": "laminadora",
            "laminadora sobremeson": "laminadora",
            "horno rotatorio": "horno",
            "horno de piso": "horno",
            "divisora ovilladora": "divisora",
            "ovilladora": "ovilladora",
            "amasadora": "amasadora",
            "batidora": "amasadora",  # Batidora es tipo de amasadora
        }
        
        return normalizations.get(category, category if category in ["laminadora", "horno", "divisora", "ovilladora", "amasadora"] else None)
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extrae contexto alrededor de una posición."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _merge_entity_sources(self, heuristic: Dict, pattern: Dict) -> Dict[str, Dict[str, Any]]:
        """Merge inteligente de entidades de múltiples fuentes."""
        merged = {"brands": {}, "models": {}, "categories": {}}
        
        for category in ["brands", "models", "categories"]:
            # Combinar entidades de ambas fuentes
            all_entities = {}
            
            # Agregar entidades heurísticas
            for entity, data in heuristic[category].items():
                all_entities[entity] = data.copy()
            
            # Merge con entidades de patrones
            for entity, data in pattern[category].items():
                if entity in all_entities:
                    # Combinar datos existentes
                    all_entities[entity]["confidence"] = max(all_entities[entity]["confidence"], data["confidence"])
                    all_entities[entity]["frequency"] += data["frequency"]
                    all_entities[entity]["contexts"].extend(data["contexts"])
                    all_entities[entity]["source"] = "merged"
                else:
                    all_entities[entity] = data.copy()
            
            # Filtrar por calidad
            for entity, data in all_entities.items():
                if (data["confidence"] >= self.confidence_threshold and 
                    data["frequency"] >= self.min_frequency):
                    merged[category][entity] = data
        
        return merged
    
    def bootstrap_from_corpus(self, corpus_text: str) -> Dict[str, Any]:
        """Análisis masivo del corpus existente para bootstrap inicial."""
        
        print("🔄 Iniciando bootstrap de taxonomía desde corpus...")
        
        # Sanitizar corpus completo
        safe_corpus = self.sanitize_text(corpus_text)
        
        # Dividir en chunks manejables
        chunks = self._split_text_intelligent(safe_corpus, max_tokens=3000)
        
        all_candidates = {"brands": [], "models": [], "categories": []}
        
        # Procesar cada chunk
        for i, chunk in enumerate(chunks):
            print(f"📄 Procesando chunk {i+1}/{len(chunks)}...")
            
            chunk_entities = self.extract_comprehensive_entities(chunk, f"bootstrap_chunk_{i}")
            
            for category in ["brands", "models", "categories"]:
                all_candidates[category].extend(chunk_entities[category])
        
        # Consolidar candidatos por frecuencia global
        consolidated = self._consolidate_candidates(all_candidates)
        
        # Si no hay LLM disponible, usar solo validación heurística
        if self.llm is None:
            print("🔧 Usando validación heurística (sin LLM)")
            validated = self._fallback_validation(consolidated)
        else:
            print("🤖 Usando validación LLM")
            # Validación LLM para candidatos de alta frecuencia  
            validated = self._validate_high_frequency_with_llm(consolidated, safe_corpus)
        
        print(f"✅ Bootstrap completado: {len(validated['brands'])} marcas, {len(validated['models'])} modelos, {len(validated['categories'])} categorías")
        
        return validated
    
    def _split_text_intelligent(self, text: str, max_tokens: int = 3000) -> List[str]:
        """División inteligente de texto manteniendo contexto técnico."""
        
        # Dividir por llamadas de servicio si es posible
        service_calls = re.split(r'Llamada de Servicio N°', text)
        
        chunks = []
        current_chunk = ""
        
        for call in service_calls:
            if not call.strip():
                continue
                
            # Agregar prefijo si no es el primer elemento
            call_text = "Llamada de Servicio N°" + call if call != service_calls[0] else call
            
            # Estimar tokens (aproximadamente 4 caracteres por token)
            estimated_tokens = len(current_chunk + call_text) // 4
            
            if estimated_tokens > max_tokens and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = call_text
            else:
                current_chunk += "\n" + call_text
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _consolidate_candidates(self, all_candidates: Dict[str, List[EntityCandidate]]) -> Dict[str, List[EntityCandidate]]:
        """Consolida candidatos por frecuencia global y calidad."""
        
        consolidated = {"brands": {}, "models": {}, "categories": {}}
        
        for category in ["brands", "models", "categories"]:
            # Agrupar por valor
            grouped = defaultdict(list)
            for candidate in all_candidates[category]:
                grouped[candidate.value].append(candidate)
            
            # Consolidar cada grupo
            for value, candidates in grouped.items():
                total_frequency = sum(c.frequency for c in candidates)
                max_confidence = max(c.confidence for c in candidates)
                all_contexts = []
                sources = set()
                
                for c in candidates:
                    all_contexts.extend(c.context_snippets)
                    sources.add(c.validation_source)
                
                # Crear candidato consolidado
                if total_frequency >= self.min_frequency:
                    consolidated_candidate = EntityCandidate(
                        value=value,
                        category=category,
                        confidence=max_confidence,
                        frequency=total_frequency,
                        context_snippets=all_contexts[:5],  # Top 5 contextos
                        validation_source="consolidated_" + "_".join(sources)
                    )
                    consolidated[category][value] = consolidated_candidate
        
        return consolidated
    
    def _validate_high_frequency_with_llm(self, candidates: Dict[str, Dict[str, EntityCandidate]], corpus_sample: str) -> Dict[str, Dict[str, List[str]]]:
        """Validación LLM solo para candidatos de alta frecuencia."""
        
        # Tomar muestra representativa del corpus para contexto
        sample = corpus_sample[:2000] if len(corpus_sample) > 2000 else corpus_sample
        
        # Preparar candidatos para validación
        high_freq_candidates = {}
        for category, entities in candidates.items():
            high_freq_candidates[category] = [
                entity.value for entity in entities.values() 
                if entity.frequency >= 3 or entity.confidence >= 0.9
            ]
        
        if not any(high_freq_candidates.values()):
            return {"brands": {}, "models": {}, "categories": {}}
        
        system_prompt = """
        Eres un experto en equipos industriales de panadería y gastronomía.
        
        Analiza estos candidatos extraídos de documentos técnicos y valida:
        1. ¿Son marcas reales de equipos industriales?
        2. ¿Son modelos técnicos válidos?
        3. ¿Son categorías correctas de equipos?
        
        CONTEXTO: Los documentos son órdenes de servicio técnico reales.
        
        REGLAS:
        - Solo valida entidades que reconozcas como reales
        - Para marcas: deben ser fabricantes conocidos de equipos industriales
        - Para modelos: deben tener formato técnico válido
        - Para categorías: deben ser tipos de equipos industriales
        - Si no estás seguro, no incluyas la entidad
        
        Responde en JSON con sinónimos y variaciones:
        {
          "brands": {"MARCA_VALIDA": ["sinónimo1", "variación2"]},
          "models": {"MODELO_VALIDO": ["variación1"]},
          "categories": {"categoria": ["sinónimo1", "variación2"]}
        }
        """
        
        user_prompt = f"""
        MUESTRA DEL CORPUS:
        {sample}
        
        CANDIDATOS A VALIDAR:
        Marcas: {high_freq_candidates.get('brands', [])}
        Modelos: {high_freq_candidates.get('models', [])}
        Categorías: {high_freq_candidates.get('categories', [])}
        
        Valida y estructura la respuesta en JSON.
        """
        
        try:
            raw_response = self.llm.complete_json(system_prompt, user_prompt)
            validated = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
            
            # Sanitizar respuesta LLM
            return self._sanitize_llm_response(validated)
            
        except Exception as e:
            print(f"⚠️ Error en validación LLM: {e}")
            # Fallback: usar candidatos heurísticos de alta confianza
            return self._fallback_validation(candidates)
    
    def _sanitize_llm_response(self, llm_response: Dict) -> Dict[str, Dict[str, List[str]]]:
        """Sanitiza y valida respuesta del LLM."""
        
        sanitized = {"brands": {}, "models": {}, "categories": {}}
        
        for category in ["brands", "models", "categories"]:
            if category in llm_response and isinstance(llm_response[category], dict):
                for entity, synonyms in llm_response[category].items():
                    # Validar entidad principal
                    if self._is_valid_entity(entity, category):
                        # Validar sinónimos
                        valid_synonyms = []
                        if isinstance(synonyms, list):
                            for syn in synonyms:
                                if isinstance(syn, str) and self._is_valid_entity(syn, category):
                                    valid_synonyms.append(syn.strip())
                        
                        sanitized[category][entity] = valid_synonyms
        
        return sanitized
    
    def _is_valid_entity(self, entity: str, category: str) -> bool:
        """Validación final de entidades."""
        if not entity or not isinstance(entity, str):
            return False
        
        entity = entity.strip()
        
        if len(entity) < 2:
            return False
        
        # Filtros específicos por categoría
        if category == "brands":
            return self._is_valid_brand(entity)
        elif category == "models":
            return self._is_valid_model(entity)
        elif category == "categories":
            return entity.lower() in ["laminadora", "horno", "divisora", "ovilladora", "amasadora", "freidora", "plancha", "refrigerador"]
        
        return False
    
    def _fallback_validation(self, candidates: Dict[str, Dict[str, EntityCandidate]]) -> Dict[str, Dict[str, List[str]]]:
        """Validación fallback usando solo heurísticas."""
        
        fallback = {"brands": {}, "models": {}, "categories": {}}
        
        for category, entities in candidates.items():
            for entity_name, candidate in entities.items():
                if candidate.confidence >= 0.85 and candidate.frequency >= 2:
                    fallback[category][entity_name] = []  # Sin sinónimos en fallback
        
        return fallback
    
    def learn_incrementally(self, new_text: str, existing_taxonomy: Dict[str, Any]) -> Dict[str, Any]:
        """Aprendizaje incremental durante ingesta nueva."""
        
        # Extraer entidades del nuevo contenido
        candidates = self.extract_comprehensive_entities(new_text)
        
        # Filtrar solo entidades nuevas no presentes en taxonomía
        new_entities = {"brands": {}, "models": {}, "categories": {}}
        
        for category in ["brands", "models", "categories"]:
            existing_entities = set()
            
            # Obtener entidades existentes (canonical + aliases)
            for canonical, aliases in existing_taxonomy.get(category, {}).items():
                existing_entities.add(canonical.upper())
                for alias in aliases:
                    existing_entities.add(alias.upper())
            
            # Filtrar candidatos nuevos
            for candidate in candidates[category]:
                if candidate.value.upper() not in existing_entities and candidate.confidence >= self.confidence_threshold:
                    new_entities[category][candidate.value] = []
        
        # Solo procesar si hay entidades nuevas significativas
        if sum(len(entities) for entities in new_entities.values()) > 0:
            print(f"🔍 Detectadas {sum(len(entities) for entities in new_entities.values())} entidades nuevas para aprendizaje")
            return new_entities
        
        return {"brands": {}, "models": {}, "categories": {}}
    
    def get_learning_stats(self, learned_entities: Dict[str, Any]) -> Dict[str, Any]:
        """Genera estadísticas del aprendizaje para monitoreo."""
        
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "new_brands": len(learned_entities.get("brands", {})),
            "new_models": len(learned_entities.get("models", {})),
            "new_categories": len(learned_entities.get("categories", {})),
            "total_new_entities": sum(len(entities) for entities in learned_entities.values()),
            "confidence_threshold": self.confidence_threshold,
            "min_frequency": self.min_frequency
        }
        
        # Agregar ejemplos de entidades aprendidas
        stats["examples"] = {}
        for category, entities in learned_entities.items():
            if entities:
                stats["examples"][category] = list(entities.keys())[:3]  # Top 3 ejemplos
        
        return stats
