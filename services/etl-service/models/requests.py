"""
Modelos de request para ETL Service
Definiciones Pydantic para validación de entrada
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SyncType(str, Enum):
    INCREMENTAL = "incremental"
    FULL = "full"
    TABLES_ONLY = "tables_only"


class PriorityLevel(str, Enum):
    CRITICAL = "CRÍTICA"
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAJA"


# ================================================================
# DESCUBRIMIENTO Y ANÁLISIS
# ================================================================

class SchemaDiscoveryRequest(BaseModel):
    """Request para descubrimiento de esquema"""
    databases: Optional[List[str]] = Field(
        None, 
        description="Bases de datos a analizar. Si no se especifica, analiza todas las configuradas"
    )
    deep_analysis: bool = Field(
        True, 
        description="Realizar análisis profundo con IA de cada tabla"
    )
    sample_data: bool = Field(
        True, 
        description="Incluir muestra de datos en el análisis"
    )
    max_sample_rows: int = Field(
        5, 
        description="Máximo número de filas de muestra por tabla"
    )


class GenerateConfigRequest(BaseModel):
    """Request para generar configuración ETL"""
    databases: List[str] = Field(
        description="Bases de datos para las que generar configuración"
    )
    analysis_job_id: Optional[str] = Field(
        None, 
        description="ID de job de análisis previo. Si no se proporciona, ejecuta análisis rápido"
    )
    priority_filter: Optional[List[PriorityLevel]] = Field(
        None, 
        description="Filtrar tablas por prioridad"
    )
    custom_rules: Optional[Dict[str, Any]] = Field(
        None, 
        description="Reglas personalizadas de configuración"
    )
    save_config: bool = Field(
        True, 
        description="Guardar configuración generada automáticamente"
    )


# ================================================================
# EJECUCIÓN ETL
# ================================================================

class ETLSyncRequest(BaseModel):
    """Request para ejecutar sincronización ETL"""
    databases: Optional[List[str]] = Field(
        None, 
        description="Bases de datos a sincronizar. Si no se especifica, usa todas las habilitadas"
    )
    tables: Optional[List[str]] = Field(
        None, 
        description="Tablas específicas a sincronizar. Si no se especifica, usa configuración"
    )
    sync_type: SyncType = Field(
        SyncType.INCREMENTAL, 
        description="Tipo de sincronización"
    )
    batch_size: Optional[int] = Field(
        None, 
        description="Tamaño de lote. Si no se especifica, usa configuración por defecto"
    )
    force_sync: bool = Field(
        False, 
        description="Forzar sincronización incluso si no hay cambios detectados"
    )
    dry_run: bool = Field(
        False, 
        description="Ejecutar sin realizar cambios reales (solo simulación)"
    )
    priority_filter: Optional[List[PriorityLevel]] = Field(
        None, 
        description="Solo sincronizar tablas con estas prioridades"
    )


class ETLTestRequest(BaseModel):
    """Request para testing de ETL"""
    database: str = Field(description="Base de datos a probar")
    table: str = Field(description="Tabla específica a probar")
    limit: int = Field(10, description="Límite de registros para prueba")
    dry_run: bool = Field(True, description="Ejecutar sin persistir datos")
    include_transformation: bool = Field(
        True, 
        description="Incluir transformación AI en la prueba"
    )


# ================================================================
# CONFIGURACIÓN
# ================================================================

class TableConfigRequest(BaseModel):
    """Request para configurar tabla específica"""
    enabled: bool = Field(True, description="Habilitar tabla para ETL")
    priority: PriorityLevel = Field(PriorityLevel.MEDIUM, description="Prioridad de la tabla")
    strategy: str = Field("incremental", description="Estrategia de extracción")
    where_clause: Optional[str] = Field(None, description="Filtro SQL personalizado")
    batch_size: Optional[int] = Field(None, description="Tamaño de lote específico")
    metadata_mapping: Optional[Dict[str, str]] = Field(
        None, 
        description="Mapeo de campos a metadata"
    )
    transformation_config: Optional[Dict[str, Any]] = Field(
        None, 
        description="Configuración específica de transformación"
    )


class DatabaseConfigRequest(BaseModel):
    """Request para configurar base de datos"""
    enabled: bool = Field(True, description="Habilitar base de datos")
    connection_config: Optional[Dict[str, Any]] = Field(
        None, 
        description="Configuración de conexión específica"
    )
    default_batch_size: Optional[int] = Field(None, description="Tamaño de lote por defecto")
    timeout_seconds: Optional[int] = Field(None, description="Timeout de conexión")


# ================================================================
# MONITOREO Y ADMINISTRACIÓN
# ================================================================

class SchedulerConfigRequest(BaseModel):
    """Request para configurar scheduler"""
    enabled: bool = Field(True, description="Habilitar scheduler automático")
    incremental_hours: int = Field(2, description="Horas entre sync incrementales")
    full_sync_time: str = Field("02:00", description="Hora para sync completo (formato HH:MM)")
    timezone: str = Field("UTC", description="Zona horaria para scheduling")
    max_concurrent_jobs: int = Field(1, description="Máximo jobs concurrentes")


class AlertConfigRequest(BaseModel):
    """Request para configurar alertas"""
    webhook_url: Optional[str] = Field(None, description="URL de webhook para alertas")
    email_recipients: Optional[List[str]] = Field(None, description="Emails para alertas")
    alert_on_error: bool = Field(True, description="Alertar en errores")
    alert_on_low_quality: bool = Field(True, description="Alertar en calidad baja")
    quality_threshold: float = Field(0.8, description="Umbral de calidad para alertas")


# ================================================================
# UTILIDADES
# ================================================================

class DatabaseTestRequest(BaseModel):
    """Request para probar conexión de BD"""
    database: str = Field(description="Nombre de la base de datos a probar")
    timeout_seconds: int = Field(10, description="Timeout para la prueba")


class JobActionRequest(BaseModel):
    """Request para acciones sobre jobs"""
    action: str = Field(description="Acción a realizar: cancel, retry, delete")
    reason: Optional[str] = Field(None, description="Razón de la acción")


class ExportConfigRequest(BaseModel):
    """Request para exportar configuración"""
    include_sensitive: bool = Field(
        False, 
        description="Incluir datos sensibles (passwords, keys) en la exportación"
    )
    format: str = Field("json", description="Formato de exportación: json, yaml")
    compress: bool = Field(False, description="Comprimir archivo de exportación")


class ImportConfigRequest(BaseModel):
    """Request para importar configuración"""
    config_data: Dict[str, Any] = Field(description="Datos de configuración a importar")
    merge_mode: str = Field(
        "replace", 
        description="Modo de importación: replace, merge, append"
    )
    validate_only: bool = Field(
        False, 
        description="Solo validar configuración sin aplicar cambios"
    )
    backup_current: bool = Field(
        True, 
        description="Crear backup de configuración actual antes de importar"
    )


# ================================================================
# BÚSQUEDA Y FILTROS
# ================================================================

class JobSearchRequest(BaseModel):
    """Request para buscar jobs"""
    status: Optional[List[str]] = Field(None, description="Filtrar por status")
    job_type: Optional[List[str]] = Field(None, description="Filtrar por tipo de job")
    database: Optional[str] = Field(None, description="Filtrar por base de datos")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    limit: int = Field(50, description="Límite de resultados")
    offset: int = Field(0, description="Offset para paginación")


class LogSearchRequest(BaseModel):
    """Request para buscar logs"""
    level: Optional[List[str]] = Field(None, description="Nivel de log: INFO, WARNING, ERROR")
    message_contains: Optional[str] = Field(None, description="Buscar en mensaje de log")
    component: Optional[str] = Field(None, description="Componente específico")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    limit: int = Field(100, description="Límite de resultados")


# ================================================================
# VALIDACIÓN PERSONALIZADA
# ================================================================

def validate_cron_expression(cron_expr: str) -> bool:
    """Validar expresión cron"""
    try:
        from croniter import croniter
        return croniter.is_valid(cron_expr)
    except:
        return False


def validate_sql_query(query: str) -> bool:
    """Validación básica de query SQL"""
    query_clean = query.strip().lower()
    
    # Solo permitir SELECT
    if not query_clean.startswith('select'):
        return False
    
    # Palabras prohibidas
    forbidden = ['delete', 'update', 'insert', 'drop', 'create', 'alter', 'truncate']
    return not any(word in query_clean for word in forbidden)


# ================================================================
# EJEMPLO DE USO
# ================================================================

if __name__ == "__main__":
    # Ejemplo de request de sincronización
    sync_request = ETLSyncRequest(
        databases=["production", "inventory"],
        sync_type=SyncType.INCREMENTAL,
        priority_filter=[PriorityLevel.HIGH, PriorityLevel.CRITICAL],
        batch_size=1000
    )
    
    print(sync_request.model_dump_json(indent=2))
