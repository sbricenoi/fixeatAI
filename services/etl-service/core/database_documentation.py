"""
Database Documentation Loader - Carga documentación rica de BD para contexto IA
Permite cargar documentación detallada en múltiples formatos para enriquecer el análisis IA
"""

from __future__ import annotations

import os
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger("etl-service.db-docs")


@dataclass
class TableDocumentation:
    """Documentación completa de una tabla"""
    name: str
    business_purpose: str
    data_lifecycle: Optional[str] = None
    update_frequency: Optional[str] = None
    critical_fields: Dict[str, str] = field(default_factory=dict)
    business_rules: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, str] = field(default_factory=dict)
    ai_usage: Dict[str, Any] = field(default_factory=dict)
    quality_notes: Optional[str] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class DatabaseDocumentation:
    """Documentación completa de una base de datos"""
    database_name: str
    business_domain: str
    industry_context: str
    data_classification: str
    update_frequency: str
    tables: Dict[str, TableDocumentation] = field(default_factory=dict)
    business_processes: List[str] = field(default_factory=list)
    data_flow: str = ""
    relationships_overview: Dict[str, Any] = field(default_factory=dict)
    extraction_priorities: Dict[str, Any] = field(default_factory=dict)
    special_considerations: List[str] = field(default_factory=list)


class DatabaseDocumentationLoader:
    """Cargador de documentación de BD desde múltiples fuentes"""
    
    def __init__(self, docs_directory: str = "docs/database"):
        self.docs_directory = Path(docs_directory)
        self.loaded_docs: Dict[str, DatabaseDocumentation] = {}
        
        # Crear directorio si no existe
        self.docs_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📚 DatabaseDocumentationLoader inicializado en: {self.docs_directory}")
    
    def load_documentation(self, database_name: str) -> Optional[DatabaseDocumentation]:
        """Cargar documentación de una BD específica"""
        
        if database_name in self.loaded_docs:
            return self.loaded_docs[database_name]
        
        try:
            # Buscar archivos de documentación en orden de prioridad
            doc_files = [
                self.docs_directory / f"{database_name}_documentation.json",
                self.docs_directory / f"{database_name}_documentation.yaml",
                self.docs_directory / f"{database_name}_documentation.yml",
                self.docs_directory / f"{database_name}.json",
                self.docs_directory / f"{database_name}.yaml",
                self.docs_directory / "database_documentation.json",  # Documentación general
                self.docs_directory / "database_documentation.yaml"
            ]
            
            for doc_file in doc_files:
                if doc_file.exists():
                    logger.info(f"📖 Cargando documentación de BD desde: {doc_file}")
                    documentation = self._load_from_file(doc_file, database_name)
                    if documentation:
                        self.loaded_docs[database_name] = documentation
                        return documentation
            
            # Si no hay documentación específica, crear estructura básica
            logger.warning(f"⚠️ No se encontró documentación para BD '{database_name}'. Creando estructura básica.")
            return self._create_basic_documentation(database_name)
            
        except Exception as e:
            logger.error(f"❌ Error cargando documentación de BD '{database_name}': {e}")
            return None
    
    def _load_from_file(self, file_path: Path, database_name: str) -> Optional[DatabaseDocumentation]:
        """Cargar documentación desde archivo específico"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    data = json.load(f)
                elif file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    logger.error(f"❌ Formato de archivo no soportado: {file_path}")
                    return None
            
            return self._parse_documentation_data(data, database_name)
            
        except Exception as e:
            logger.error(f"❌ Error leyendo archivo {file_path}: {e}")
            return None
    
    def _parse_documentation_data(self, data: Dict[str, Any], database_name: str) -> DatabaseDocumentation:
        """Parsear datos de documentación desde diccionario"""
        
        # Obtener metadata de BD
        db_metadata = data.get("database_metadata", {})
        
        # Crear documentación de BD
        db_doc = DatabaseDocumentation(
            database_name=database_name,
            business_domain=db_metadata.get("business_domain", "No especificado"),
            industry_context=db_metadata.get("industry_context", "No especificado"),
            data_classification=db_metadata.get("data_classification", "No especificado"),
            update_frequency=db_metadata.get("update_frequency", "No especificado"),
            business_processes=db_metadata.get("business_processes", []),
            data_flow=db_metadata.get("data_flow", ""),
            relationships_overview=data.get("relationships_overview", {}),
            extraction_priorities=data.get("extraction_priorities", {}),
            special_considerations=data.get("special_considerations", [])
        )
        
        # Parsear documentación de tablas
        tables_data = data.get("tables", {})
        for table_name, table_info in tables_data.items():
            table_doc = TableDocumentation(
                name=table_name,
                business_purpose=table_info.get("business_purpose", "No especificado"),
                data_lifecycle=table_info.get("data_lifecycle"),
                update_frequency=table_info.get("update_frequency"),
                critical_fields=table_info.get("critical_fields", {}),
                business_rules=table_info.get("business_rules", {}),
                relationships=table_info.get("relationships", {}),
                ai_usage=table_info.get("ai_usage", {}),
                quality_notes=table_info.get("quality_notes"),
                examples=table_info.get("examples", []),
                tags=table_info.get("tags", [])
            )
            db_doc.tables[table_name] = table_doc
        
        logger.info(f"✅ Documentación parseada: {len(db_doc.tables)} tablas documentadas")
        return db_doc
    
    def _create_basic_documentation(self, database_name: str) -> DatabaseDocumentation:
        """Crear documentación básica cuando no existe archivo"""
        
        return DatabaseDocumentation(
            database_name=database_name,
            business_domain="Por determinar",
            industry_context="Por determinar", 
            data_classification="Por determinar",
            update_frequency="Por determinar"
        )
    
    def get_table_documentation(self, database_name: str, table_name: str) -> Optional[TableDocumentation]:
        """Obtener documentación de tabla específica"""
        
        db_doc = self.load_documentation(database_name)
        if db_doc and table_name in db_doc.tables:
            return db_doc.tables[table_name]
        return None
    
    def get_business_context_summary(self, database_name: str) -> Dict[str, Any]:
        """Obtener resumen de contexto de negocio para IA"""
        
        db_doc = self.load_documentation(database_name)
        if not db_doc:
            return {}
        
        return {
            "database_overview": {
                "business_domain": db_doc.business_domain,
                "industry_context": db_doc.industry_context,
                "data_classification": db_doc.data_classification,
                "business_processes": db_doc.business_processes,
                "data_flow": db_doc.data_flow
            },
            "table_purposes": {
                name: table.business_purpose 
                for name, table in db_doc.tables.items()
            },
            "critical_relationships": db_doc.relationships_overview,
            "extraction_priorities": db_doc.extraction_priorities,
            "special_considerations": db_doc.special_considerations
        }
    
    def create_documentation_template(self, database_name: str, output_path: Optional[str] = None) -> str:
        """Crear plantilla de documentación para una BD"""
        
        if output_path is None:
            output_path = self.docs_directory / f"{database_name}_documentation_template.json"
        
        template = {
            "database_metadata": {
                "business_domain": "Ejemplo: Servicios técnicos de equipos industriales",
                "industry_context": "Ejemplo: Reparación y mantenimiento de equipos de panadería/cocina industrial",
                "data_classification": "Ejemplo: Operacional y técnico",
                "update_frequency": "Ejemplo: Tiempo real durante servicios",
                "business_processes": [
                    "Gestión de órdenes de servicio",
                    "Seguimiento de equipos",
                    "Gestión de inventario de repuestos"
                ],
                "data_flow": "Ejemplo: Cliente reporta problema → Orden creada → Técnico asignado → Servicio ejecutado → Resolución documentada"
            },
            "tables": {
                "services": {
                    "business_purpose": "Órdenes de trabajo para servicios técnicos en equipos industriales",
                    "data_lifecycle": "Creado → En progreso → Completado/Cancelado",
                    "update_frequency": "Tiempo real durante ejecución del servicio",
                    "critical_fields": {
                        "equipment_id": "Referencia al equipo atendido (FK a equipments) - CRÍTICO para contexto",
                        "issue_description": "Problema reportado por cliente - CRÍTICO para IA predictiva",
                        "resolution": "Pasos realizados por técnico - CRÍTICO para Knowledge Base",
                        "parts_used": "Lista de repuestos utilizados - CRÍTICO para predicción de stock",
                        "technician_id": "Técnico asignado - relevante para contexto de calidad",
                        "status": "Estado actual del servicio (pending/in_progress/completed)"
                    },
                    "business_rules": {
                        "status_flow": "pending → in_progress → completed/cancelled",
                        "required_completion": "resolution y parts_used obligatorios al completar",
                        "data_retention": "Histórico completo para análisis de tendencias"
                    },
                    "relationships": {
                        "services.equipment_id": "equipments.id",
                        "services.customer_id": "customers.id", 
                        "services.technician_id": "technicians.id"
                    },
                    "ai_usage": {
                        "prediction_input": ["equipment_id", "issue_description", "equipment_brand"],
                        "training_data": ["issue_description", "resolution", "parts_used"],
                        "metadata_source": ["technician_id", "service_date", "priority"],
                        "kb_value": "CRÍTICO: Casos reales de diagnóstico y resolución para entrenamiento IA"
                    },
                    "examples": [
                        {
                            "equipment_id": 1234,
                            "issue_description": "Horno RATIONAL CombiMaster no enciende, display apagado",
                            "resolution": "Se identificó falla en tarjeta de control. Reemplazo de módulo principal y recalibración",
                            "parts_used": "Tarjeta control RATIONAL RC-001, Cable datos RC-002"
                        }
                    ],
                    "tags": ["high_priority", "ai_training", "technical_content"]
                },
                "equipments": {
                    "business_purpose": "Catálogo maestro de equipos industriales instalados en clientes",
                    "critical_fields": {
                        "brand": "Marca del equipo - CRÍTICO para filtros KB y predicciones",
                        "model": "Modelo específico - CRÍTICO para búsquedas precisas",
                        "equipment_type": "Categoría (horno, laminadora, etc.) - CRÍTICO para taxonomía",
                        "installation_date": "Fecha instalación - relevante para patrones de desgaste",
                        "customer_id": "Cliente propietario - contexto del entorno operativo"
                    },
                    "ai_usage": {
                        "entity_extraction": ["brand", "model", "equipment_type"],
                        "failure_patterns": ["installation_date", "equipment_type", "usage_intensity"],
                        "context_enrichment": ["customer_location", "maintenance_history"]
                    },
                    "tags": ["master_data", "taxonomy_source", "equipment_catalog"]
                }
            },
            "relationships_overview": {
                "core_entities": ["services", "equipments", "customers"],
                "main_flows": {
                    "service_lifecycle": "services → equipments → customers",
                    "knowledge_flow": "services.resolution → Knowledge Base → AI Training"
                }
            },
            "extraction_priorities": {
                "high_priority": {
                    "tables": ["services", "equipments"],
                    "reason": "Contienen información técnica directamente relevante para IA"
                },
                "medium_priority": {
                    "tables": ["customers", "technicians"],
                    "reason": "Proveen contexto complementario importante"
                },
                "low_priority": {
                    "tables": ["user_sessions", "audit_logs"],
                    "reason": "Datos operacionales sin valor técnico directo"
                }
            },
            "special_considerations": [
                "Datos de servicios contienen información técnica valiosa para IA",
                "Equipments table es fuente principal para taxonomía automática",
                "Campos de resolución requieren procesamiento de texto avanzado",
                "Relación services-equipments es crítica para contexto de fallas"
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📝 Plantilla de documentación creada: {output_path}")
        return str(output_path)
    
    def validate_documentation(self, database_name: str) -> Dict[str, Any]:
        """Validar completitud y calidad de la documentación"""
        
        db_doc = self.load_documentation(database_name)
        if not db_doc:
            return {"valid": False, "error": "No se pudo cargar documentación"}
        
        validation_results = {
            "valid": True,
            "completeness_score": 0.0,
            "missing_fields": [],
            "recommendations": [],
            "tables_documented": len(db_doc.tables),
            "critical_fields_documented": 0,
            "ai_usage_documented": 0
        }
        
        # Validar metadata de BD
        required_db_fields = ["business_domain", "industry_context", "data_classification"]
        missing_db_fields = [
            field for field in required_db_fields
            if not getattr(db_doc, field) or getattr(db_doc, field) == "No especificado"
        ]
        
        if missing_db_fields:
            validation_results["missing_fields"].extend([f"database.{field}" for field in missing_db_fields])
        
        # Validar documentación de tablas
        for table_name, table_doc in db_doc.tables.items():
            if not table_doc.business_purpose or table_doc.business_purpose == "No especificado":
                validation_results["missing_fields"].append(f"{table_name}.business_purpose")
            
            if table_doc.critical_fields:
                validation_results["critical_fields_documented"] += 1
            
            if table_doc.ai_usage:
                validation_results["ai_usage_documented"] += 1
        
        # Calcular score de completitud
        total_checks = len(required_db_fields) + len(db_doc.tables) * 3  # 3 checks por tabla
        missing_checks = len(validation_results["missing_fields"])
        validation_results["completeness_score"] = max(0.0, (total_checks - missing_checks) / total_checks)
        
        # Generar recomendaciones
        if validation_results["completeness_score"] < 0.7:
            validation_results["recommendations"].append("Documentación incompleta. Completar campos faltantes.")
        
        if validation_results["ai_usage_documented"] < len(db_doc.tables) * 0.5:
            validation_results["recommendations"].append("Documentar mejor el uso de IA para más tablas.")
        
        if not db_doc.data_flow:
            validation_results["recommendations"].append("Agregar descripción del flujo de datos de negocio.")
        
        return validation_results


# ================================================================
# INTEGRACIÓN CON AI ANALYZER
# ================================================================

class EnhancedContextBuilder:
    """Constructor de contexto enriquecido para análisis IA"""
    
    def __init__(self, doc_loader: DatabaseDocumentationLoader):
        self.doc_loader = doc_loader
    
    def build_enhanced_context(self, database_name: str, table_name: str, table_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Construir contexto enriquecido combinando documentación + metadata técnico"""
        
        # Cargar documentación
        db_doc = self.doc_loader.load_documentation(database_name)
        table_doc = self.doc_loader.get_table_documentation(database_name, table_name)
        
        enhanced_context = {
            "technical_metadata": table_meta,
            "database_context": {},
            "table_documentation": {},
            "business_intelligence": {},
            "ai_enhancement_instructions": []
        }
        
        # Contexto de BD
        if db_doc:
            enhanced_context["database_context"] = {
                "business_domain": db_doc.business_domain,
                "industry_context": db_doc.industry_context,
                "data_flow": db_doc.data_flow,
                "business_processes": db_doc.business_processes
            }
        
        # Documentación de tabla
        if table_doc:
            enhanced_context["table_documentation"] = {
                "business_purpose": table_doc.business_purpose,
                "critical_fields": table_doc.critical_fields,
                "business_rules": table_doc.business_rules,
                "ai_usage": table_doc.ai_usage,
                "relationships": table_doc.relationships,
                "examples": table_doc.examples[:2]  # Solo 2 ejemplos para no sobrecargar
            }
            
            # Instrucciones específicas para IA
            if table_doc.ai_usage:
                if "prediction_input" in table_doc.ai_usage:
                    enhanced_context["ai_enhancement_instructions"].append(
                        f"Campos clave para predicción: {table_doc.ai_usage['prediction_input']}"
                    )
                if "kb_value" in table_doc.ai_usage:
                    enhanced_context["ai_enhancement_instructions"].append(
                        f"Valor para KB: {table_doc.ai_usage['kb_value']}"
                    )
        
        # Inteligencia de negocio específica
        enhanced_context["business_intelligence"] = self._extract_business_intelligence(
            db_doc, table_doc, table_meta
        )
        
        return enhanced_context
    
    def _extract_business_intelligence(self, db_doc: Optional[DatabaseDocumentation], 
                                     table_doc: Optional[TableDocumentation], 
                                     table_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Extraer inteligencia de negocio específica para IA"""
        
        intelligence = {
            "priority_score": 5,  # Default medium priority
            "ai_value_indicators": [],
            "transformation_hints": [],
            "quality_expectations": []
        }
        
        if table_doc:
            # Calcular prioridad basada en tags y propósito
            if "high_priority" in table_doc.tags or "ai_training" in table_doc.tags:
                intelligence["priority_score"] = 9
            elif "technical_content" in table_doc.tags:
                intelligence["priority_score"] = 8
            elif "master_data" in table_doc.tags:
                intelligence["priority_score"] = 7
            
            # Indicadores de valor para IA
            if table_doc.critical_fields:
                intelligence["ai_value_indicators"].append(
                    f"Contiene {len(table_doc.critical_fields)} campos críticos documentados"
                )
            
            if any("CRÍTICO" in desc for desc in table_doc.critical_fields.values()):
                intelligence["ai_value_indicators"].append("Campos marcados como CRÍTICOS para IA")
            
            # Hints de transformación
            if "resolution" in table_doc.critical_fields:
                intelligence["transformation_hints"].append(
                    "Incluir pasos de resolución en narrativa técnica"
                )
            
            if "parts_used" in table_doc.critical_fields:
                intelligence["transformation_hints"].append(
                    "Extraer repuestos como entidades separadas"
                )
        
        return intelligence


# ================================================================
# EJEMPLO DE DOCUMENTACIÓN
# ================================================================

if __name__ == "__main__":
    # Ejemplo de uso
    loader = DatabaseDocumentationLoader("docs/database")
    
    # Crear plantilla
    template_path = loader.create_documentation_template("production_db")
    print(f"Plantilla creada en: {template_path}")
    
    # Cargar documentación
    db_doc = loader.load_documentation("production_db") 
    if db_doc:
        print(f"BD documentada: {db_doc.database_name}")
        print(f"Dominio: {db_doc.business_domain}")
        print(f"Tablas: {list(db_doc.tables.keys())}")
    
    # Validar documentación
    validation = loader.validate_documentation("production_db")
    print(f"Validación: {validation}")
