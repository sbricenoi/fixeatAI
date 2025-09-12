"""
Modelos de response para ETL Service
Definiciones Pydantic para respuestas estándar
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


# ================================================================
# RESPUESTAS BÁSICAS
# ================================================================

class BaseResponse(BaseModel):
    """Respuesta base estándar"""
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: HealthStatus
    message: str = "Service health check"
    service: str = "etl-service"
    version: str = "1.0.0"
    uptime_seconds: int
    checks: Dict[str, bool] = Field(description="Estado de componentes individuales")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ServiceStatusResponse(BaseModel):
    """Estado detallado del servicio"""
    status: str = "success"
    message: str = "Service status retrieved"
    service_info: Dict[str, Any]
    active_jobs: Dict[str, Any]
    statistics: Dict[str, Any]
    scheduler_status: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ================================================================
# DESCUBRIMIENTO Y ANÁLISIS
# ================================================================

class TableAnalysis(BaseModel):
    """Análisis de una tabla específica"""
    table_name: str
    business_purpose: Optional[str] = None
    ai_relevance: float = Field(ge=0, le=10, description="Relevancia para IA (0-10)")
    data_quality: float = Field(ge=0, le=10, description="Calidad de datos (0-10)")
    estimated_rows: Optional[int] = None
    text_columns: List[str] = Field(default_factory=list)
    key_fields: List[str] = Field(default_factory=list)
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    recommended_strategy: Optional[str] = None
    sample_data: Optional[List[Dict[str, Any]]] = None


class DatabaseAnalysis(BaseModel):
    """Análisis completo de una base de datos"""
    database_name: str
    total_tables: int
    analyzed_tables: int
    business_context: Dict[str, Any]
    table_analyses: Dict[str, TableAnalysis]
    recommendations: List[Dict[str, Any]]
    summary: Dict[str, Any]


class SchemaDiscoveryResponse(BaseModel):
    """Respuesta de descubrimiento de esquema"""
    status: str = "success"
    message: str = "Schema discovery completed"
    job_id: str
    databases_analyzed: List[str]
    total_tables: int
    relevant_tables: int
    discovery_results: Dict[str, DatabaseAnalysis]
    summary: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SchemaAnalysisResponse(BaseResponse):
    """Respuesta de análisis de esquema específico"""
    job_id: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Dict[str, Any]
    error: Optional[str] = None


# ================================================================
# CONFIGURACIÓN ETL
# ================================================================

class TableConfig(BaseModel):
    """Configuración de tabla para ETL"""
    enabled: bool
    priority: str
    strategy: str
    extraction_config: Dict[str, Any]
    transformation_config: Dict[str, Any]
    metadata_config: Dict[str, Any]
    estimated_docs: Optional[int] = None


class ETLConfigResponse(BaseResponse):
    """Respuesta de configuración ETL generada"""
    config_id: Optional[str] = None
    generated_config: Dict[str, TableConfig]
    summary: Dict[str, Any]


# ================================================================
# EJECUCIÓN ETL
# ================================================================

class ETLJobResponse(BaseResponse):
    """Respuesta de job ETL iniciado"""
    job_id: str
    started_at: datetime
    estimated_duration: Optional[int] = Field(None, description="Duración estimada en segundos")


class ETLJobProgress(BaseModel):
    """Progreso de job ETL"""
    current_table: Optional[str] = None
    tables_completed: int = 0
    tables_total: int = 0
    records_processed: int = 0
    records_total: Optional[int] = None
    percentage: float = Field(ge=0, le=100)
    current_operation: Optional[str] = None


class ETLJobResult(BaseModel):
    """Resultado de ETL por tabla"""
    table_name: str
    status: JobStatus
    extracted_records: int = 0
    transformed_docs: int = 0
    ingested_docs: int = 0
    quality_score: Optional[float] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    duration_seconds: Optional[float] = None


class ETLJobStatusResponse(BaseResponse):
    """Estado detallado de job ETL"""
    job_id: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress: Optional[ETLJobProgress] = None
    results: Dict[str, ETLJobResult] = Field(default_factory=dict)
    error: Optional[str] = None
    total_duration: Optional[float] = None


# ================================================================
# MÉTRICAS Y MONITOREO
# ================================================================

class ServiceMetrics(BaseModel):
    """Métricas del servicio"""
    uptime_hours: float
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    success_rate: float
    avg_job_duration: Optional[float] = None


class DatabaseMetrics(BaseModel):
    """Métricas por base de datos"""
    database_name: str
    connection_status: str
    total_tables: int
    active_tables: int
    last_sync: Optional[datetime] = None
    avg_sync_duration: Optional[float] = None
    total_records_processed: int = 0


class PipelineMetrics(BaseModel):
    """Métricas del pipeline ETL"""
    total_extractions: int = 0
    total_transformations: int = 0
    total_ingestions: int = 0
    avg_extraction_time: Optional[float] = None
    avg_transformation_time: Optional[float] = None
    avg_ingestion_time: Optional[float] = None


class QualityMetrics(BaseModel):
    """Métricas de calidad"""
    overall_quality_score: float
    documents_below_threshold: int = 0
    common_quality_issues: List[str] = Field(default_factory=list)
    quality_trend: Optional[str] = None


class PerformanceMetrics(BaseModel):
    """Métricas de rendimiento"""
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    network_io_mb: Optional[float] = None
    active_connections: int = 0


class ETLMetricsResponse(BaseResponse):
    """Respuesta completa de métricas"""
    service_metrics: ServiceMetrics
    database_metrics: List[DatabaseMetrics]
    pipeline_metrics: PipelineMetrics
    quality_metrics: QualityMetrics
    performance_metrics: PerformanceMetrics


# ================================================================
# CALIDAD Y REPORTES
# ================================================================

class QualityIssue(BaseModel):
    """Issue de calidad detectado"""
    issue_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_tables: List[str]
    recommendation: Optional[str] = None
    count: int = 1


class QualityTrend(BaseModel):
    """Tendencia de calidad en el tiempo"""
    date: datetime
    quality_score: float
    documents_processed: int
    issues_detected: int


class QualityReportResponse(BaseResponse):
    """Reporte detallado de calidad"""
    overall_score: float
    table_scores: Dict[str, float]
    quality_issues: List[QualityIssue]
    recommendations: List[str]
    trends: List[QualityTrend]


# ================================================================
# ADMINISTRACIÓN
# ================================================================

class JobListResponse(BaseResponse):
    """Lista de jobs con paginación"""
    jobs: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    has_next: bool


class ConfigExportResponse(BaseResponse):
    """Respuesta de exportación de configuración"""
    config_data: Dict[str, Any]
    export_format: str
    file_size_bytes: Optional[int] = None
    download_url: Optional[str] = None


class ConfigImportResponse(BaseResponse):
    """Respuesta de importación de configuración"""
    imported_items: int
    skipped_items: int
    validation_errors: List[str] = Field(default_factory=list)
    backup_created: bool = False
    backup_id: Optional[str] = None


# ================================================================
# BÚSQUEDAS Y FILTROS
# ================================================================

class SearchResult(BaseModel):
    """Resultado de búsqueda genérico"""
    item_id: str
    item_type: str
    title: str
    description: Optional[str] = None
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseResponse):
    """Respuesta de búsqueda"""
    results: List[SearchResult]
    total_found: int
    search_time_ms: float
    query: str
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


# ================================================================
# ERRORES Y EXCEPCIONES
# ================================================================

class ErrorDetail(BaseModel):
    """Detalle de error"""
    error_code: str
    error_message: str
    component: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseResponse):
    """Respuesta de error estándar"""
    error_details: List[ErrorDetail]
    request_id: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)


# ================================================================
# WEBHOOK Y NOTIFICACIONES
# ================================================================

class NotificationEvent(BaseModel):
    """Evento de notificación"""
    event_type: str
    event_data: Dict[str, Any]
    severity: str = "info"  # info, warning, error, critical
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "etl-service"


class WebhookResponse(BaseModel):
    """Respuesta de webhook"""
    webhook_id: str
    delivered: bool
    delivery_time_ms: Optional[float] = None
    response_code: Optional[int] = None
    error_message: Optional[str] = None


# ================================================================
# UTILIDADES Y HELPERS
# ================================================================

def create_success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Helper para crear respuesta de éxito estándar"""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": trace_id
    }


def create_error_response(
    error: str,
    details: Optional[Dict[str, Any]] = None,
    suggestions: Optional[List[str]] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Helper para crear respuesta de error estándar"""
    return {
        "status": "error",
        "message": error,
        "error_details": details or {},
        "suggestions": suggestions or [],
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": trace_id
    }


# ================================================================
# EJEMPLO DE USO
# ================================================================

if __name__ == "__main__":
    # Ejemplo de respuesta de job ETL
    job_response = ETLJobStatusResponse(
        status="success",
        message="ETL job completed",
        job_id="etl_20231210_143022",
        job_status=JobStatus.COMPLETED,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        results={
            "services": ETLJobResult(
                table_name="services",
                status=JobStatus.COMPLETED,
                extracted_records=1500,
                transformed_docs=1450,
                ingested_docs=1450,
                quality_score=0.92,
                duration_seconds=45.2
            )
        }
    )
    
    print(job_response.model_dump_json(indent=2))
