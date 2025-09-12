"""
Enhanced AI Schema Analyzer - Análisis IA enriquecido con documentación previa
Combina documentación rica + análisis IA para evaluaciones súper precisas
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .database_documentation import DatabaseDocumentationLoader, EnhancedContextBuilder
from .config import ETLConfig, LLMConfig

logger = logging.getLogger("etl-service.enhanced-ai-analyzer")


class EnhancedAISchemaAnalyzer:
    """Analizador IA mejorado con contexto documental rico"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.llm_config = config.llm_config
        
        # Inicializar componentes
        self.doc_loader = DatabaseDocumentationLoader("docs/database")
        self.context_builder = EnhancedContextBuilder(self.doc_loader)
        
        # Cliente LLM (importar dinámicamente para evitar dependencias)
        self._llm_client = None
        
        logger.info("🧠 EnhancedAISchemaAnalyzer inicializado")
    
    async def initialize(self) -> bool:
        """Inicializar el analizador IA"""
        try:
            # Inicializar cliente LLM
            self._llm_client = await self._init_llm_client()
            
            # Verificar disponibilidad de documentación
            await self._verify_documentation_availability()
            
            logger.info("✅ Enhanced AI Analyzer inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Enhanced AI Analyzer: {e}")
            return False
    
    async def _init_llm_client(self):
        """Inicializar cliente LLM según configuración"""
        try:
            if self.llm_config.provider.value == "openai":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(
                    api_key=self.llm_config.api_key,
                    base_url=self.llm_config.base_url
                )
            elif self.llm_config.provider.value == "ollama":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(
                    api_key="dummy-key", 
                    base_url=self.llm_config.base_url or "http://localhost:11434/v1"
                )
            else:
                raise ValueError(f"Proveedor LLM no soportado: {self.llm_config.provider}")
            
            # Test de conectividad
            await self._test_llm_connectivity(client)
            return client
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo inicializar cliente LLM: {e}")
            return None
    
    async def _test_llm_connectivity(self, client):
        """Probar conectividad con LLM"""
        try:
            response = await client.chat.completions.create(
                model=self.llm_config.model,
                messages=[{"role": "user", "content": "Test connectivity"}],
                max_tokens=10,
                temperature=0
            )
            logger.info("✅ Conectividad LLM verificada")
        except Exception as e:
            logger.warning(f"⚠️ Test de conectividad LLM falló: {e}")
            raise
    
    async def _verify_documentation_availability(self):
        """Verificar disponibilidad de documentación"""
        # Lista de BDs configuradas
        db_names = list(self.config.databases.keys())
        
        for db_name in db_names:
            db_doc = self.doc_loader.load_documentation(db_name)
            if db_doc:
                logger.info(f"📚 Documentación encontrada para BD '{db_name}': {len(db_doc.tables)} tablas documentadas")
            else:
                logger.warning(f"⚠️ No hay documentación para BD '{db_name}'. Creando plantilla...")
                template_path = self.doc_loader.create_documentation_template(db_name)
                logger.info(f"📝 Plantilla creada: {template_path}")
    
    async def analyze_table_context_enhanced(self, database_name: str, table_name: str, table_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis IA enriquecido con documentación previa"""
        
        logger.info(f"🔍 Analizando tabla '{table_name}' en BD '{database_name}' con contexto enriquecido")
        
        try:
            # 1. Construir contexto enriquecido
            enhanced_context = self.context_builder.build_enhanced_context(
                database_name, table_name, table_meta
            )
            
            # 2. Análisis IA con contexto rico
            if self._llm_client:
                ai_analysis = await self._perform_enhanced_ai_analysis(
                    database_name, table_name, enhanced_context
                )
            else:
                logger.warning("⚠️ LLM no disponible, usando análisis heurístico")
                ai_analysis = self._fallback_heuristic_analysis(enhanced_context)
            
            # 3. Combinar documentación + análisis IA
            final_analysis = self._merge_documentation_and_ai_analysis(
                enhanced_context, ai_analysis
            )
            
            logger.info(f"✅ Análisis completado para tabla '{table_name}' - Relevancia: {final_analysis.get('ai_relevance', 0)}/10")
            return final_analysis
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de tabla '{table_name}': {e}")
            return self._create_error_analysis(table_name, str(e))
    
    async def _perform_enhanced_ai_analysis(self, database_name: str, table_name: str, enhanced_context: Dict[str, Any]) -> Dict[str, Any]:
        """Realizar análisis IA con contexto enriquecido"""
        
        # Construir prompt súper detallado
        prompt = self._build_enhanced_analysis_prompt(database_name, table_name, enhanced_context)
        
        try:
            response = await self._llm_client.chat.completions.create(
                model=self.llm_config.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un experto en análisis de bases de datos y arquitectura de datos para sistemas de IA. Tu especialidad es evaluar el valor de tablas de BD para Knowledge Bases técnicos y sistemas predictivos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.llm_config.temperature,
                max_tokens=self.llm_config.max_tokens
            )
            
            # Parsear respuesta JSON
            ai_response = response.choices[0].message.content
            analysis = self._parse_ai_analysis_response(ai_response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error en llamada LLM: {e}")
            return self._fallback_heuristic_analysis(enhanced_context)
    
    def _build_enhanced_analysis_prompt(self, database_name: str, table_name: str, enhanced_context: Dict[str, Any]) -> str:
        """Construir prompt enriquecido para análisis IA"""
        
        # Información técnica
        tech_info = enhanced_context.get("technical_metadata", {})
        columns = tech_info.get("columns", [])
        column_names = [col.get("name", "") for col in columns]
        
        # Contexto de BD
        db_context = enhanced_context.get("database_context", {})
        
        # Documentación específica de tabla
        table_doc = enhanced_context.get("table_documentation", {})
        
        # Inteligencia de negocio
        business_intel = enhanced_context.get("business_intelligence", {})
        
        # Instrucciones específicas para IA
        ai_instructions = enhanced_context.get("ai_enhancement_instructions", [])
        
        prompt = f"""
        ANÁLISIS ENRIQUECIDO DE TABLA PARA ETL INTELIGENTE

        === CONTEXTO DE BASE DE DATOS ===
        Base de Datos: {database_name}
        Dominio de Negocio: {db_context.get('business_domain', 'No especificado')}
        Contexto Industrial: {db_context.get('industry_context', 'No especificado')}
        Flujo de Datos: {db_context.get('data_flow', 'No especificado')}
        Procesos de Negocio: {', '.join(db_context.get('business_processes', []))}

        === TABLA A ANALIZAR ===
        Nombre: {table_name}
        Columnas Técnicas: {', '.join(column_names)}
        Número de Columnas: {len(columns)}
        
        === DOCUMENTACIÓN PREVIA (CRÍTICA) ===
        Propósito de Negocio: {table_doc.get('business_purpose', 'No documentado')}
        
        Campos Críticos Documentados:
        {json.dumps(table_doc.get('critical_fields', {}), indent=2, ensure_ascii=False)}
        
        Reglas de Negocio:
        {json.dumps(table_doc.get('business_rules', {}), indent=2, ensure_ascii=False)}
        
        Uso para IA Documentado:
        {json.dumps(table_doc.get('ai_usage', {}), indent=2, ensure_ascii=False)}
        
        Relaciones Documentadas:
        {json.dumps(table_doc.get('relationships', {}), indent=2, ensure_ascii=False)}
        
        Ejemplos de Datos Reales:
        {json.dumps(table_doc.get('examples', []), indent=2, ensure_ascii=False)}

        === INTELIGENCIA DE NEGOCIO ===
        Score de Prioridad Previo: {business_intel.get('priority_score', 5)}/10
        Indicadores de Valor IA: {', '.join(business_intel.get('ai_value_indicators', []))}
        Hints de Transformación: {', '.join(business_intel.get('transformation_hints', []))}
        
        === INSTRUCCIONES ESPECÍFICAS PARA IA ===
        {chr(10).join(f"- {instruction}" for instruction in ai_instructions)}

        === ANÁLISIS REQUERIDO ===
        
        Con este CONTEXTO SÚPER RICO, proporciona un análisis detallado y preciso:

        1. RELEVANCIA TÉCNICA (0-10): 
           - Considera la documentación previa del propósito de negocio
           - Evalúa los campos críticos documentados
           - Pondera el valor para diagnóstico de equipos industriales
        
        2. VALOR PREDICTIVO (0-10):
           - Basándote en el uso para IA documentado
           - Considera los ejemplos reales proporcionados
           - Evalúa potencial para predecir fallas futuras
        
        3. CALIDAD NARRATIVA (0-10):
           - Analiza la riqueza de los campos de texto documentados
           - Considera la capacidad de generar contenido técnico valioso
           - Evalúa la coherencia de la información
        
        4. PRIORIDAD ETL: CRÍTICA/ALTA/MEDIA/BAJA
           - Basándote en toda la documentación previa
           - Considera el contexto industrial específico
           - Pondera el impacto en el Knowledge Base técnico
        
        5. ESTRATEGIA DE EXTRACCIÓN:
           - full_table: Toda la tabla es valiosa
           - filtered: Solo registros específicos (especifica filtros)
           - joined: Requiere JOIN con otras tablas (especifica cuáles)
           - enriched: Necesita enriquecimiento con contexto adicional
        
        6. CONFIGURACIÓN ETL RECOMENDADA:
           - SQL template sugerido considerando relaciones documentadas
           - Campos clave para extracción basados en documentación
           - Filtros recomendados según reglas de negocio
           - Batch size sugerido
        
        7. TRANSFORMACIÓN IA ESPECÍFICA:
           - Prompt de transformación personalizado para esta tabla
           - Metadata a extraer automáticamente
           - Consideraciones especiales basadas en la documentación
        
        8. JUSTIFICACIÓN DETALLADA:
           - Explica cómo la documentación previa influyó en tu análisis
           - Destaca elementos críticos encontrados en la documentación
           - Reasoning específico para las puntuaciones asignadas

        RESPONDE EN JSON ESTRICTO:
        {{
          "relevancia_tecnica": 8.5,
          "valor_predictivo": 9.0,
          "calidad_narrativa": 8.0,
          "prioridad": "CRÍTICA",
          "estrategia": "joined",
          "configuracion_etl": {{
            "sql_template": "SELECT s.*, e.brand, e.model FROM {table_name} s JOIN equipments e ON s.equipment_id = e.id",
            "campos_clave": ["campo1", "campo2"],
            "filtros_recomendados": "WHERE status = 'completed'",
            "batch_size": 500
          }},
          "transformacion_ia": {{
            "prompt_personalizado": "Convierte este registro de servicio técnico en una narrativa...",
            "metadata_automatica": ["brand", "model", "issue_type"],
            "consideraciones_especiales": ["Preservar terminología técnica", "Extraer códigos de repuestos"]
          }},
          "justificacion": "La documentación previa revela que esta tabla contiene casos reales de falla y resolución...",
          "confianza_analisis": 0.95,
          "fuentes_utilizadas": ["documentacion_previa", "business_context", "technical_metadata"]
        }}
        """
        
        return prompt
    
    def _parse_ai_analysis_response(self, ai_response: str) -> Dict[str, Any]:
        """Parsear respuesta JSON del análisis IA"""
        try:
            # Limpiar respuesta si viene con texto adicional
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
            else:
                raise ValueError("No se encontró JSON válido en respuesta IA")
                
        except Exception as e:
            logger.error(f"❌ Error parseando respuesta IA: {e}")
            # Fallback a análisis básico
            return {
                "relevancia_tecnica": 5.0,
                "valor_predictivo": 5.0,
                "calidad_narrativa": 5.0,
                "prioridad": "MEDIA",
                "estrategia": "full_table",
                "justificacion": f"Error parseando respuesta IA: {str(e)}",
                "confianza_analisis": 0.3
            }
    
    def _fallback_heuristic_analysis(self, enhanced_context: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis heurístico cuando LLM no está disponible"""
        
        table_doc = enhanced_context.get("table_documentation", {})
        business_intel = enhanced_context.get("business_intelligence", {})
        tech_metadata = enhanced_context.get("technical_metadata", {})
        
        # Calcular relevancia basada en documentación
        relevancia = business_intel.get("priority_score", 5)
        
        # Ajustar según campos críticos documentados
        critical_fields = table_doc.get("critical_fields", {})
        if len(critical_fields) > 3:
            relevancia += 1
        
        # Ajustar según uso de IA documentado
        ai_usage = table_doc.get("ai_usage", {})
        if ai_usage and "CRÍTICO" in str(ai_usage):
            relevancia += 2
        
        # Normalizar a escala 0-10
        relevancia = min(10, max(0, relevancia))
        
        return {
            "relevancia_tecnica": relevancia,
            "valor_predictivo": relevancia,
            "calidad_narrativa": relevancia - 1,
            "prioridad": "ALTA" if relevancia >= 8 else "MEDIA" if relevancia >= 6 else "BAJA",
            "estrategia": "joined" if table_doc.get("relationships") else "full_table",
            "justificacion": "Análisis heurístico basado en documentación previa",
            "confianza_analisis": 0.7,
            "metodo_analisis": "heuristic_fallback"
        }
    
    def _merge_documentation_and_ai_analysis(self, enhanced_context: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combinar documentación previa con análisis IA"""
        
        table_doc = enhanced_context.get("table_documentation", {})
        business_intel = enhanced_context.get("business_intelligence", {})
        
        # Crear análisis final combinado
        final_analysis = {
            # Scores de IA
            "ai_relevance": ai_analysis.get("relevancia_tecnica", 5.0),
            "predictive_value": ai_analysis.get("valor_predictivo", 5.0),
            "narrative_quality": ai_analysis.get("calidad_narrativa", 5.0),
            
            # Configuración ETL
            "priority": ai_analysis.get("prioridad", "MEDIA"),
            "extraction_strategy": ai_analysis.get("estrategia", "full_table"),
            "etl_config": ai_analysis.get("configuracion_etl", {}),
            
            # Transformación IA
            "transformation_config": ai_analysis.get("transformacion_ia", {}),
            
            # Análisis y justificación
            "analysis_reasoning": ai_analysis.get("justificacion", ""),
            "confidence_score": ai_analysis.get("confianza_analisis", 0.5),
            
            # Contexto documental preservado
            "documented_purpose": table_doc.get("business_purpose", ""),
            "critical_fields": table_doc.get("critical_fields", {}),
            "business_rules": table_doc.get("business_rules", {}),
            "documented_ai_usage": table_doc.get("ai_usage", {}),
            "relationships": table_doc.get("relationships", {}),
            "examples": table_doc.get("examples", []),
            
            # Inteligencia de negocio
            "business_intelligence": business_intel,
            
            # Metadata del análisis
            "analysis_method": "enhanced_ai_with_documentation",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "documentation_quality": len(table_doc.get("critical_fields", {})),
            "enhancement_instructions": enhanced_context.get("ai_enhancement_instructions", [])
        }
        
        return final_analysis
    
    def _create_error_analysis(self, table_name: str, error_message: str) -> Dict[str, Any]:
        """Crear análisis de error cuando falla el proceso"""
        return {
            "ai_relevance": 0.0,
            "predictive_value": 0.0,
            "narrative_quality": 0.0,
            "priority": "BAJA",
            "extraction_strategy": "skip",
            "analysis_reasoning": f"Error en análisis: {error_message}",
            "confidence_score": 0.0,
            "analysis_method": "error_fallback",
            "error": error_message
        }
    
    async def infer_business_context_enhanced(self, schema: Dict[str, Any], database_name: str) -> Dict[str, Any]:
        """Inferir contexto de negocio enriquecido con documentación"""
        
        try:
            # Cargar documentación de BD
            db_doc = self.doc_loader.load_documentation(database_name)
            
            if db_doc:
                # Usar contexto documentado
                business_context = {
                    "business_type": db_doc.business_domain,
                    "industry_context": db_doc.industry_context,
                    "data_classification": db_doc.data_classification,
                    "business_processes": db_doc.business_processes,
                    "data_flow": db_doc.data_flow,
                    "main_entities": list(db_doc.tables.keys()),
                    "documented": True,
                    "documentation_quality": len(db_doc.tables)
                }
                
                logger.info(f"✅ Contexto de negocio cargado desde documentación para '{database_name}'")
                return business_context
            else:
                # Fallback a inferencia IA
                logger.warning(f"⚠️ No hay documentación para '{database_name}', usando inferencia IA")
                return await self._infer_context_with_ai(schema, database_name)
                
        except Exception as e:
            logger.error(f"❌ Error inferiendo contexto para '{database_name}': {e}")
            return {"business_type": "Unknown", "documented": False, "error": str(e)}
    
    async def _infer_context_with_ai(self, schema: Dict[str, Any], database_name: str) -> Dict[str, Any]:
        """Inferir contexto usando IA cuando no hay documentación"""
        
        if not self._llm_client:
            return {"business_type": "Unknown", "method": "no_llm_available"}
        
        table_names = list(schema.get("tables", {}).keys())
        
        prompt = f"""
        Analiza estos nombres de tablas de la base de datos '{database_name}' e infiere el contexto de negocio:
        
        TABLAS: {', '.join(table_names)}
        
        Responde en JSON:
        {{
          "business_type": "Tipo de negocio inferido",
          "industry_context": "Contexto industrial",
          "main_entities": ["entidad1", "entidad2"],
          "business_processes": ["proceso1", "proceso2"],
          "data_flow": "Flujo principal de datos inferido"
        }}
        """
        
        try:
            response = await self._llm_client.chat.completions.create(
                model=self.llm_config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            context = self._parse_ai_analysis_response(ai_response)
            context["documented"] = False
            context["method"] = "ai_inference"
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Error en inferencia IA de contexto: {e}")
            return {"business_type": "Unknown", "method": "ai_error", "error": str(e)}
    
    async def generate_etl_recommendations_enhanced(self, table_analyses: Dict[str, Any], database_name: str) -> List[Dict[str, Any]]:
        """Generar recomendaciones ETL enriquecidas"""
        
        recommendations = []
        
        # Agrupar por prioridad
        critical_tables = []
        high_tables = []
        medium_tables = []
        
        for table_name, analysis in table_analyses.items():
            priority = analysis.get("priority", "MEDIA")
            if priority == "CRÍTICA":
                critical_tables.append((table_name, analysis))
            elif priority == "ALTA":
                high_tables.append((table_name, analysis))
            elif priority == "MEDIA":
                medium_tables.append((table_name, analysis))
        
        # Recomendaciones por prioridad
        if critical_tables:
            recommendations.append({
                "type": "critical_extraction",
                "priority": 1,
                "tables": [t[0] for t in critical_tables],
                "strategy": "immediate_full_extraction",
                "reasoning": "Tablas críticas con máximo valor para IA y Knowledge Base",
                "estimated_value": "MÁXIMO"
            })
        
        if high_tables:
            recommendations.append({
                "type": "high_priority_extraction", 
                "priority": 2,
                "tables": [t[0] for t in high_tables],
                "strategy": "scheduled_extraction",
                "reasoning": "Tablas de alta prioridad con valor significativo",
                "estimated_value": "ALTO"
            })
        
        # Recomendaciones de JOIN basadas en documentación
        join_recommendations = self._generate_join_recommendations(table_analyses, database_name)
        recommendations.extend(join_recommendations)
        
        return recommendations
    
    def _generate_join_recommendations(self, table_analyses: Dict[str, Any], database_name: str) -> List[Dict[str, Any]]:
        """Generar recomendaciones de JOIN basadas en documentación"""
        
        recommendations = []
        
        # Buscar tablas que requieren JOIN según documentación
        for table_name, analysis in table_analyses.items():
            relationships = analysis.get("relationships", {})
            extraction_strategy = analysis.get("extraction_strategy", "")
            
            if extraction_strategy == "joined" and relationships:
                recommendations.append({
                    "type": "join_extraction",
                    "primary_table": table_name,
                    "join_tables": list(relationships.values()),
                    "reasoning": "Documentación indica que tabla requiere contexto de relaciones",
                    "priority": 2 if analysis.get("priority") == "CRÍTICA" else 3
                })
        
        return recommendations
    
    def health_check(self) -> bool:
        """Verificar salud del componente"""
        try:
            # Verificar componentes clave
            doc_available = self.doc_loader is not None
            context_builder_available = self.context_builder is not None
            
            return doc_available and context_builder_available
            
        except Exception as e:
            logger.error(f"❌ Health check falló: {e}")
            return False


# ================================================================
# EJEMPLO DE USO
# ================================================================

if __name__ == "__main__":
    import asyncio
    from .config import ETLConfig
    
    async def test_enhanced_analyzer():
        # Crear configuración de prueba
        config = ETLConfig()
        
        # Inicializar analizador
        analyzer = EnhancedAISchemaAnalyzer(config)
        await analyzer.initialize()
        
        # Simular metadata de tabla
        table_meta = {
            "columns": [
                {"name": "id", "type": "int"},
                {"name": "equipment_id", "type": "int"},
                {"name": "issue_description", "type": "text"},
                {"name": "resolution", "type": "text"}
            ],
            "primary_key": ["id"],
            "foreign_keys": [{"column": "equipment_id", "ref_table": "equipments"}]
        }
        
        # Analizar tabla con contexto enriquecido
        analysis = await analyzer.analyze_table_context_enhanced(
            "production_db", "services", table_meta
        )
        
        print("Análisis enriquecido:", json.dumps(analysis, indent=2, ensure_ascii=False))
    
    # Ejecutar test
    asyncio.run(test_enhanced_analyzer())
