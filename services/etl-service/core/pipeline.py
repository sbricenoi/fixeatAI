"""
ETL Pipeline - Pipeline principal de extracción, transformación y carga
Orquesta el proceso completo de ETL con IA
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from .config import ETLConfig
from .database import DatabaseManager
from .ai_analyzer import AISchemaAnalyzer

logger = logging.getLogger("etl-service.pipeline")


class ETLPipeline:
    """Pipeline principal de ETL con IA"""
    
    def __init__(self, config: ETLConfig, db_manager: DatabaseManager, ai_analyzer: AISchemaAnalyzer):
        self.config = config
        self.db_manager = db_manager
        self.ai_analyzer = ai_analyzer
        
        self.current_configs: Dict[str, Any] = {}
        self.job_progress: Dict[str, Dict[str, Any]] = {}
        
        logger.info("🔄 ETLPipeline inicializado")
    
    async def load_configs(self) -> Dict[str, Any]:
        """Cargar configuraciones ETL existentes"""
        
        try:
            config_file = "configs/etl_configurations.json"
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.current_configs = json.load(f)
                logger.info(f"✅ Configuraciones ETL cargadas: {len(self.current_configs)} bases de datos")
            else:
                self.current_configs = {}
                logger.info("📝 No hay configuraciones ETL previas, se crearán automáticamente")
            
            return self.current_configs
            
        except Exception as e:
            logger.error(f"❌ Error cargando configuraciones ETL: {e}")
            self.current_configs = {}
            return {}
    
    async def generate_config_from_analysis(self, analysis_results: Dict[str, Any], 
                                          priority_filter: Optional[List[str]] = None,
                                          custom_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generar configuración ETL desde análisis IA"""
        
        logger.info("⚙️ Generando configuración ETL desde análisis IA")
        
        generated_config = {
            "generation_timestamp": datetime.utcnow().isoformat(),
            "generation_method": "ai_analysis",
            "databases": {}
        }
        
        for db_name, db_analysis in analysis_results.items():
            db_config = {"tables": {}}
            
            table_analysis = db_analysis.get("table_analysis", {})
            
            for table_name, analysis in table_analysis.items():
                # Filtrar por prioridad si se especifica
                table_priority = analysis.get("priority", "MEDIA")
                if priority_filter and table_priority not in priority_filter:
                    continue
                
                # Generar configuración de tabla
                table_config = self._generate_table_config(table_name, analysis, custom_rules)
                
                if table_config:
                    db_config["tables"][table_name] = table_config
            
            if db_config["tables"]:
                generated_config["databases"][db_name] = db_config
        
        logger.info(f"✅ Configuración generada para {len(generated_config['databases'])} bases de datos")
        
        # Limpiar el config para asegurar serialización JSON
        clean_config = self._clean_for_json_serialization(generated_config)
        return clean_config
    
    def _clean_for_json_serialization(self, obj: Any) -> Any:
        """Limpiar objeto para asegurar serialización JSON"""
        if isinstance(obj, dict):
            return {k: self._clean_for_json_serialization(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json_serialization(item) for item in obj]
        elif isinstance(obj, set):
            return list(obj)
        elif str(type(obj)) in ["<class 'dict_keys'>", "<class 'dict_values'>", "<class 'dict_items'>"]:
            return list(obj)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            # Cualquier iterable que no sea string/bytes, convertir a lista
            try:
                return [self._clean_for_json_serialization(item) for item in obj]
            except:
                return str(obj)
        elif hasattr(obj, '__dict__'):
            # Objeto personalizado, convertir a dict
            return self._clean_for_json_serialization(obj.__dict__)
        else:
            return obj
    
    def _generate_table_config(self, table_name: str, analysis: Dict[str, Any], 
                              custom_rules: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Generar configuración específica de tabla"""
        
        try:
            priority = analysis.get("priority", "MEDIA")
            ai_relevance = analysis.get("ai_relevance", 5.0)
            
            # Solo configurar tablas con relevancia mínima
            if ai_relevance < 5.0:
                return None
            
            # Configuración base - compatible con TableConfig Pydantic model
            extraction_config = self._build_extraction_config(table_name, analysis)
            table_config = {
                "enabled": True,
                "priority": priority,
                "strategy": extraction_config.get("strategy", "full_table"),  # Campo requerido
                "extraction_config": extraction_config,                       # Campo requerido
                "transformation_config": self._build_transformation_config(table_name, analysis),  # Campo requerido
                "metadata_config": self._build_quality_config(table_name, analysis),  # Campo requerido (renombrado)
                "estimated_docs": analysis.get("estimated_docs", 0)
            }
            
            # Aplicar reglas personalizadas si existen
            if custom_rules and table_name in custom_rules:
                custom_table_rules = custom_rules[table_name]
                table_config = self._apply_custom_rules(table_config, custom_table_rules)
            
            return table_config
            
        except Exception as e:
            logger.error(f"❌ Error generando configuración para tabla '{table_name}': {e}")
            return None
    
    def _build_extraction_config(self, table_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Construir configuración de extracción"""
        
        extraction_strategy = analysis.get("extraction_strategy", "full_table")
        etl_config = analysis.get("etl_config", {})
        
        config = {
            "strategy": extraction_strategy,
            "batch_size": self.config.batch_size,
            "incremental": True,
            "incremental_column": "updated_at"  # Default
        }
        
        # Configuración específica según estrategia
        if extraction_strategy == "joined":
            relationships = analysis.get("relationships", {})
            if relationships:
                # Construir JOIN automáticamente
                joins = []
                # Convertir relationships a dict si no lo es
                if not isinstance(relationships, dict):
                    relationships = {}
                
                for local_field, foreign_ref in relationships.items():
                    if isinstance(foreign_ref, str) and "." in foreign_ref:
                        try:
                            foreign_table, foreign_field = foreign_ref.split(".", 1)
                            joins.append({
                                "table": foreign_table,
                                "on": f"{table_name}.{local_field.split('.')[-1]} = {foreign_table}.{foreign_field}",
                                "type": "INNER"
                            })
                        except Exception as e:
                            logger.warning(f"⚠️ Error procesando relación {local_field}->{foreign_ref}: {e}")
                            continue
                
                config["joins"] = joins
        
        elif extraction_strategy == "filtered":
            # Usar filtros del análisis IA si están disponibles
            if "filtros_recomendados" in etl_config:
                config["where_clause"] = etl_config["filtros_recomendados"]
        
        # Usar configuración específica del análisis IA si existe
        if etl_config:
            if "sql_template" in etl_config:
                config["sql_template"] = etl_config["sql_template"]
            if "campos_clave" in etl_config:
                config["key_fields"] = etl_config["campos_clave"]
            if "batch_size" in etl_config:
                config["batch_size"] = etl_config["batch_size"]
        
        return config
    
    def _build_transformation_config(self, table_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Construir configuración de transformación"""
        
        transformation_config = analysis.get("transformation_config", {})
        documented_ai_usage = analysis.get("documented_ai_usage", {})
        
        config = {
            "enabled": True,
            "method": "ai_narrative",
            "target_format": "technical_narrative"
        }
        
        # Configuración específica de IA si existe
        if transformation_config:
            if "prompt_personalizado" in transformation_config:
                config["ai_prompt"] = transformation_config["prompt_personalizado"]
            if "metadata_automatica" in transformation_config:
                config["auto_metadata"] = transformation_config["metadata_automatica"]
            if "consideraciones_especiales" in transformation_config:
                config["special_considerations"] = transformation_config["consideraciones_especiales"]
        
        # Usar información documentada para enriquecer transformación
        if documented_ai_usage:
            if "metadata_source" in documented_ai_usage:
                config["metadata_fields"] = documented_ai_usage["metadata_source"]
        
        return config
    
    def _build_quality_config(self, table_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Construir configuración de calidad"""
        
        narrative_quality = analysis.get("narrative_quality", 5.0)
        confidence_score = analysis.get("confidence_score", 0.5)
        
        return {
            "min_confidence": max(0.7, confidence_score),
            "min_narrative_quality": max(5.0, narrative_quality),
            "required_fields": analysis.get("critical_fields", {}).keys() if analysis.get("critical_fields") else [],
            "quality_threshold": self.config.quality_threshold
        }
    
    def _apply_custom_rules(self, base_config: Dict[str, Any], custom_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Aplicar reglas personalizadas a configuración base"""
        
        # Merge profundo de configuraciones
        import copy
        config = copy.deepcopy(base_config)
        
        for section, rules in custom_rules.items():
            if section in config and isinstance(config[section], dict) and isinstance(rules, dict):
                config[section].update(rules)
            else:
                config[section] = rules
        
        return config
    
    async def save_config(self, config: Dict[str, Any]) -> str:
        """Guardar configuración ETL"""
        
        try:
            config_id = f"etl_config_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Crear directorio si no existe
            os.makedirs("configs", exist_ok=True)
            
            # Guardar configuración
            config_file = f"configs/etl_configurations.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Actualizar configuración actual
            self.current_configs = config
            
            logger.info(f"✅ Configuración ETL guardada: {config_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"❌ Error guardando configuración ETL: {e}")
            raise
    
    async def get_current_config(self) -> Dict[str, Any]:
        """Obtener configuración ETL actual"""
        return self.current_configs
    
    async def update_table_config(self, table_name: str, new_config: Dict[str, Any]) -> bool:
        """Actualizar configuración de tabla específica"""
        
        try:
            # Buscar tabla en configuraciones
            for db_name, db_config in self.current_configs.get("databases", {}).items():
                if table_name in db_config.get("tables", {}):
                    # Actualizar configuración
                    db_config["tables"][table_name].update(new_config)
                    
                    # Guardar cambios
                    await self.save_config(self.current_configs)
                    
                    logger.info(f"✅ Configuración actualizada para tabla '{table_name}'")
                    return True
            
            logger.warning(f"⚠️ Tabla '{table_name}' no encontrada en configuraciones")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error actualizando configuración de tabla '{table_name}': {e}")
            return False
    
    async def execute_sync(self, databases: Optional[List[str]] = None,
                          tables: Optional[List[str]] = None,
                          sync_type: str = "incremental",
                          batch_size: Optional[int] = None,
                          force: bool = False) -> Dict[str, Any]:
        """Ejecutar sincronización ETL"""
        
        logger.info(f"🚀 Iniciando sincronización ETL - Tipo: {sync_type}")
        
        # Determinar bases de datos a procesar
        target_databases = databases or list(self.current_configs.get("databases", {}).keys())
        
        if not target_databases:
            target_databases = self.db_manager.get_database_names()
        
        # Ejecutar sincronización por BD
        results = {}
        
        for db_name in target_databases:
            try:
                db_result = await self._execute_database_sync(
                    db_name, tables, sync_type, batch_size, force
                )
                results[db_name] = db_result
                
            except Exception as e:
                logger.error(f"❌ Error sincronizando BD '{db_name}': {e}")
                results[db_name] = {
                    "status": "error",
                    "error": str(e),
                    "extracted": 0,
                    "transformed": 0,
                    "ingested": 0
                }
        
        logger.info(f"✅ Sincronización ETL completada: {len(results)} bases de datos")
        return results
    
    async def _execute_database_sync(self, db_name: str, tables: Optional[List[str]],
                                   sync_type: str, batch_size: Optional[int], force: bool) -> Dict[str, Any]:
        """Ejecutar sincronización para una BD específica"""
        
        logger.info(f"📊 Sincronizando BD '{db_name}'")
        
        # Obtener configuración de BD
        db_config = self.current_configs.get("databases", {}).get(db_name, {})
        table_configs = db_config.get("tables", {})
        
        # Determinar tablas a procesar
        target_tables = tables or list(table_configs.keys())
        
        if not target_tables:
            logger.warning(f"⚠️ No hay tablas configuradas para BD '{db_name}'")
            return {"status": "no_tables", "extracted": 0, "transformed": 0, "ingested": 0}
        
        # Procesar cada tabla
        db_result = {
            "status": "completed",
            "tables_processed": 0,
            "extracted": 0,
            "transformed": 0,
            "ingested": 0,
            "errors": []
        }
        
        for table_name in target_tables:
            try:
                table_config = table_configs.get(table_name, {})
                
                if not table_config.get("enabled", True):
                    logger.info(f"⏭️ Tabla '{table_name}' deshabilitada, omitiendo")
                    continue
                
                table_result = await self._process_table(
                    db_name, table_name, table_config, sync_type, batch_size, force
                )
                
                db_result["tables_processed"] += 1
                db_result["extracted"] += table_result.get("extracted", 0)
                db_result["transformed"] += table_result.get("transformed", 0)
                db_result["ingested"] += table_result.get("ingested", 0)
                
                if table_result.get("errors"):
                    db_result["errors"].extend(table_result["errors"])
                
            except Exception as e:
                error_msg = f"Error procesando tabla '{table_name}': {str(e)}"
                logger.error(f"❌ {error_msg}")
                db_result["errors"].append(error_msg)
        
        return db_result
    
    async def _process_table(self, db_name: str, table_name: str, table_config: Dict[str, Any],
                           sync_type: str, batch_size: Optional[int], force: bool) -> Dict[str, Any]:
        """Procesar tabla específica"""
        
        logger.info(f"🔄 Procesando tabla '{table_name}' en BD '{db_name}'")
        
        # TODO: Implementar lógica de extracción, transformación e ingesta real
        # Por ahora, simulamos el proceso
        
        extraction_config = table_config.get("extraction", {})
        transformation_config = table_config.get("transformation", {})
        
        # Simular extracción
        extracted_count = 0
        try:
            # Usar batch_size de parámetro o configuración
            effective_batch_size = batch_size or extraction_config.get("batch_size", self.config.batch_size)
            
            # Extraer datos reales según la estrategia configurada
            if extraction_config.get("strategy") == "joined":
                extracted_data = await self.db_manager.extract_with_joins(
                    db_name, table_name, extraction_config, limit=effective_batch_size
                )
            else:
                # extract_table_data es un async generator, necesitamos iterar
                extracted_data = []
                async for batch in self.db_manager.extract_table_data(
                    db_name, table_name, batch_size=effective_batch_size, limit=effective_batch_size
                ):
                    extracted_data.extend(batch)
            
            extracted_count = len(extracted_data)
            logger.info(f"📦 Extraídos {extracted_count} registros de '{table_name}'")
            
        except Exception as e:
            logger.error(f"❌ Error en extracción de '{table_name}': {e}")
            return {"status": "extraction_error", "error": str(e), "extracted": 0, "transformed": 0, "ingested": 0}
        
        # Transformar datos con AI
        try:
            transformed_data = await self._transform_data_with_ai(
                extracted_data, table_name, transformation_config
            )
            transformed_count = len(transformed_data)
            logger.info(f"🔄 Transformados {transformed_count} registros de '{table_name}'")
        except Exception as e:
            logger.error(f"❌ Error en transformación de '{table_name}': {e}")
            transformed_data = extracted_data  # Fallback a datos sin transformar
            transformed_count = extracted_count
        
        # Ingerir datos reales al Knowledge Base
        try:
            ingested_count = await self._ingest_to_kb(
                transformed_data, table_name, db_name, metadata_config
            )
            logger.info(f"💾 Ingresados {ingested_count} registros de '{table_name}' al KB")
        except Exception as e:
            logger.error(f"❌ Error en ingestión de '{table_name}': {e}")
            ingested_count = 0
        
        return {
            "status": "completed",
            "extracted": extracted_count,
            "transformed": transformed_count,
            "ingested": ingested_count,
            "errors": []
        }
    
    async def get_job_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtener progreso de job específico"""
        return self.job_progress.get(job_id)
    
    async def _transform_data_with_ai(self, data: List[Dict], table_name: str, transformation_config: Dict) -> List[Dict]:
        """Transformar datos usando AI para crear narrativas técnicas"""
        if not data or not transformation_config.get("enabled", True):
            return data
        
        transformed_data = []
        for record in data:
            try:
                # Crear narrativa técnica del registro
                narrative = await self._create_technical_narrative(record, table_name, transformation_config)
                
                # Agregar narrativa al registro
                enhanced_record = record.copy()
                enhanced_record["technical_narrative"] = narrative
                enhanced_record["source_table"] = table_name
                enhanced_record["transformation_method"] = transformation_config.get("method", "ai_narrative")
                
                transformed_data.append(enhanced_record)
                
            except Exception as e:
                logger.warning(f"⚠️ Error transformando registro de {table_name}: {e}")
                # Incluir registro sin transformar
                record["source_table"] = table_name
                transformed_data.append(record)
        
        return transformed_data
    
    async def _create_technical_narrative(self, record: Dict, table_name: str, config: Dict) -> str:
        """Crear narrativa técnica usando LLM"""
        try:
            # Formatear datos del registro
            record_text = "\n".join([f"{k}: {v}" for k, v in record.items() if v is not None])
            
            prompt = f"""Convierte este registro de la tabla '{table_name}' en una narrativa técnica clara y útil para un sistema de conocimiento técnico:

{record_text}

Crea una descripción técnica de 2-3 oraciones que capture la información esencial de manera que sea útil para diagnósticos y resolución de problemas. Enfócate en aspectos técnicos relevantes."""

            # En una implementación real, aquí se llamaría al LLM
            # Por ahora, crear narrativa básica
            if table_name == "activities":
                return f"Actividad técnica realizada por {record.get('performed_by', 'técnico')} en equipo {record.get('company_branch_equipment_id', 'N/A')}. Estado: {record.get('activity_status_id', 'N/A')}. Tiempo: {record.get('started_at', 'N/A')} - {record.get('finished_at', 'N/A')}."
            elif table_name == "equipment_parts":
                return f"Repuesto {record.get('name', 'N/A')} para equipo {record.get('equipment_id', 'N/A')}. Código: {record.get('code', 'N/A')}. Stock: {record.get('stock', 'N/A')}."
            elif table_name == "services":
                return f"Servicio técnico #{record.get('id', 'N/A')} en sucursal {record.get('company_branch_id', 'N/A')}. Prioridad: {record.get('service_priority_id', 'N/A')}. Estado: {record.get('service_status_id', 'N/A')}."
            else:
                return f"Registro de {table_name}: {', '.join([f'{k}={v}' for k, v in list(record.items())[:3]])}"
                
        except Exception as e:
            logger.error(f"❌ Error creando narrativa para {table_name}: {e}")
            return f"Registro de {table_name} con datos técnicos disponibles."
    
    async def _ingest_to_kb(self, data: List[Dict], table_name: str, db_name: str, metadata_config: Dict) -> int:
        """Ingerir datos transformados al Knowledge Base"""
        if not data:
            return 0
        
        try:
            import httpx
            kb_url = f"{self.config.kb_url}/tools/kb_ingest"
            
            # Preparar documentos para ingestión
            documents = []
            for i, record in enumerate(data):
                doc_id = f"{db_name}_{table_name}_{record.get('id', i)}"
                content = record.get('technical_narrative', str(record))
                
                document = {
                    "doc_id": doc_id,
                    "content": content,
                    "metadata": {
                        "source_type": "database",
                        "source": f"{db_name}.{table_name}",
                        "table_name": table_name,
                        "database_name": db_name,
                        "extraction_date": "2025-09-12",
                        "record_id": record.get('id', i),
                        **metadata_config
                    }
                }
                documents.append(document)
            
            # Enviar a KB
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    kb_url,
                    json={"documents": documents},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ingested_count = result.get("ingested_count", len(documents))
                    logger.info(f"✅ KB ingestión exitosa: {ingested_count} documentos")
                    return ingested_count
                else:
                    logger.error(f"❌ Error en KB ingestión: {response.status_code} - {response.text}")
                    return 0
                    
        except Exception as e:
            logger.error(f"❌ Error conectando con KB: {e}")
            return 0
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del pipeline"""
        
        return {
            "configured_databases": len(self.current_configs.get("databases", {})),
            "total_tables": sum(len(db.get("tables", {})) for db in self.current_configs.get("databases", {}).values()),
            "enabled_tables": sum(
                len([t for t in db.get("tables", {}).values() if t.get("enabled", True)])
                for db in self.current_configs.get("databases", {}).values()
            ),
            "active_jobs": len(self.job_progress)
        }
    
    def is_healthy(self) -> bool:
        """Verificar salud del pipeline"""
        try:
            return (
                self.db_manager is not None and
                self.ai_analyzer is not None and
                isinstance(self.current_configs, dict)
            )
        except Exception:
            return False


# ================================================================
# EJEMPLO DE USO
# ================================================================

if __name__ == "__main__":
    import asyncio
    from .config import ETLConfig
    from .database import DatabaseManager
    from .ai_analyzer import AISchemaAnalyzer
    
    async def test_pipeline():
        # Inicializar componentes
        config = ETLConfig()
        db_manager = DatabaseManager(config)
        ai_analyzer = AISchemaAnalyzer(config)
        
        # Inicializar
        await db_manager.test_connections()
        await ai_analyzer.initialize()
        
        # Crear pipeline
        pipeline = ETLPipeline(config, db_manager, ai_analyzer)
        await pipeline.load_configs()
        
        # Simular análisis y configuración
        mock_analysis = {
            "default": {
                "table_analysis": {
                    "test_table": {
                        "priority": "ALTA",
                        "ai_relevance": 8.5,
                        "extraction_strategy": "full_table"
                    }
                }
            }
        }
        
        # Generar configuración
        config_data = await pipeline.generate_config_from_analysis(mock_analysis)
        print("Configuración generada:", json.dumps(config_data, indent=2))
        
        # Cerrar recursos
        await db_manager.close_connections()
    
    asyncio.run(test_pipeline())
