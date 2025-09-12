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
        return generated_config
    
    def _generate_table_config(self, table_name: str, analysis: Dict[str, Any], 
                              custom_rules: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Generar configuración específica de tabla"""
        
        try:
            priority = analysis.get("priority", "MEDIA")
            ai_relevance = analysis.get("ai_relevance", 5.0)
            
            # Solo configurar tablas con relevancia mínima
            if ai_relevance < 5.0:
                return None
            
            # Configuración base
            table_config = {
                "enabled": True,
                "priority": priority,
                "ai_relevance": ai_relevance,
                "extraction": self._build_extraction_config(table_name, analysis),
                "transformation": self._build_transformation_config(table_name, analysis),
                "quality": self._build_quality_config(table_name, analysis)
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
                for local_field, foreign_ref in relationships.items():
                    if "." in foreign_ref:
                        foreign_table, foreign_field = foreign_ref.split(".", 1)
                        joins.append({
                            "table": foreign_table,
                            "on": f"{table_name}.{local_field.split('.')[-1]} = {foreign_table}.{foreign_field}",
                            "type": "INNER"
                        })
                
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
            
            # Simular conteo (en implementación real, extraería datos)
            sample_data = await self.db_manager.get_sample_data(db_name, table_name, 5)
            extracted_count = len(sample_data)
            
            logger.info(f"📦 Simulación: extraídos {extracted_count} registros de '{table_name}'")
            
        except Exception as e:
            logger.error(f"❌ Error en extracción de '{table_name}': {e}")
            return {"status": "extraction_error", "error": str(e), "extracted": 0, "transformed": 0, "ingested": 0}
        
        # Simular transformación
        transformed_count = extracted_count  # En implementación real, aplicaría transformaciones IA
        
        # Simular ingesta (en implementación real, enviaría a KB)
        ingested_count = transformed_count
        
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
