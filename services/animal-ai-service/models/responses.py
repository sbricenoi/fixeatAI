"""
Modelos de response para Animal-AI Service
Definición de esquemas de salida para todos los endpoints
Siguiendo el estándar: traceId, code, message, data
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class AnimalAIResponse(BaseModel):
    """Response base para todos los endpoints del Animal-AI Service"""
    traceId: str = Field(..., description="ID de trazabilidad de la request")
    code: str = Field(..., description="Código de estado (OK, ERROR, WARNING)")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")


class Animal(BaseModel):
    """Modelo de un animal detectado"""
    id: str = Field(..., description="ID único del animal")
    species: str = Field(..., description="Especie del animal")
    individual_markers: List[str] = Field(..., description="Características únicas identificatorias")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confianza en la identificación")
    first_detected: datetime = Field(..., description="Primera vez detectado")
    last_seen: datetime = Field(..., description="Última vez visto")
    total_detections: int = Field(..., ge=0, description="Total de detecciones")
    status: str = Field(..., description="Estado actual del animal")


class Movement(BaseModel):
    """Modelo de un movimiento detectado"""
    id: str = Field(..., description="ID único del movimiento")
    animal_id: str = Field(..., description="ID del animal que realizó el movimiento")
    timestamp: datetime = Field(..., description="Timestamp del movimiento")
    movement_type: Optional[str] = Field(None, description="Tipo de movimiento (None si no está etiquetado)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza en la detección")
    duration_seconds: float = Field(..., ge=0.0, description="Duración del movimiento en segundos")
    coordinates: List[Dict[str, float]] = Field(..., description="Secuencia de coordenadas x,y")
    frame_sequence: List[str] = Field(..., description="IDs de frames donde ocurre el movimiento")
    is_labeled: bool = Field(..., description="Si el movimiento ha sido etiquetado manualmente")
    labeled_by: Optional[str] = Field(None, description="ID del admin que etiquetó")
    labeled_at: Optional[datetime] = Field(None, description="Timestamp del etiquetado")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")


class BehaviorPattern(BaseModel):
    """Modelo de un patrón de comportamiento aprendido"""
    pattern_id: str = Field(..., description="ID único del patrón")
    animal_id: str = Field(..., description="ID del animal")
    behavior_name: str = Field(..., description="Nombre del comportamiento")
    movement_sequence: List[str] = Field(..., description="Secuencia de tipos de movimiento")
    frequency: int = Field(..., ge=0, description="Frecuencia de ocurrencia")
    context: Dict[str, Any] = Field(..., description="Contexto del comportamiento (hora, condiciones, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza en el patrón")
    learned_from_examples: int = Field(..., ge=1, description="Número de ejemplos usados para aprender")
    last_updated: datetime = Field(..., description="Última actualización del patrón")


class VideoStream(BaseModel):
    """Modelo de un stream de video activo"""
    stream_id: str = Field(..., description="ID único del stream")
    source: str = Field(..., description="Fuente del video")
    status: str = Field(..., description="Estado del stream (starting, processing, error, stopped)")
    start_time: datetime = Field(..., description="Tiempo de inicio")
    resolution: str = Field(..., description="Resolución del video")
    fps: int = Field(..., description="Frames por segundo")
    total_frames_processed: int = Field(..., ge=0, description="Total de frames procesados")
    animals_detected: int = Field(..., ge=0, description="Animales detectados en este stream")
    movements_detected: int = Field(..., ge=0, description="Movimientos detectados")
    last_activity: datetime = Field(..., description="Última actividad detectada")


class AnalysisResult(BaseModel):
    """Resultado de análisis de comportamiento"""
    animal_id: str = Field(..., description="ID del animal analizado")
    analysis_type: str = Field(..., description="Tipo de análisis realizado")
    time_window_hours: int = Field(..., description="Ventana de tiempo analizada")
    total_movements: int = Field(..., ge=0, description="Total de movimientos en el período")
    behavior_summary: Dict[str, int] = Field(..., description="Resumen de comportamientos")
    patterns_detected: List[BehaviorPattern] = Field(..., description="Patrones detectados")
    anomalies: List[Dict[str, Any]] = Field(..., description="Anomalías detectadas")
    health_indicators: Dict[str, Any] = Field(..., description="Indicadores de salud")
    predictions: Optional[Dict[str, Any]] = Field(None, description="Predicciones futuras")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confianza general del análisis")


class KBSearchResult(BaseModel):
    """Resultado de búsqueda en el Knowledge Base"""
    doc_id: str = Field(..., description="ID del documento")
    score: float = Field(..., description="Score de relevancia")
    snippet: str = Field(..., description="Fragmento relevante")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del documento")


class SystemStatus(BaseModel):
    """Estado del sistema Animal-AI"""
    status: str = Field(..., description="Estado general del sistema")
    uptime_seconds: float = Field(..., description="Tiempo activo en segundos")
    active_streams: int = Field(..., ge=0, description="Streams activos")
    total_animals_detected: int = Field(..., ge=0, description="Total de animales detectados")
    total_movements_classified: int = Field(..., ge=0, description="Total de movimientos clasificados")
    total_behaviors_learned: int = Field(..., ge=0, description="Total de comportamientos aprendidos")
    memory_usage_mb: float = Field(..., description="Uso de memoria en MB")
    cpu_usage_percent: float = Field(..., description="Uso de CPU en porcentaje")
    disk_usage_percent: float = Field(..., description="Uso de disco en porcentaje")
    last_error: Optional[str] = Field(None, description="Último error registrado")


class DashboardData(BaseModel):
    """Datos para el dashboard de administración"""
    system_status: SystemStatus = Field(..., description="Estado del sistema")
    recent_animals: List[Animal] = Field(..., description="Animales detectados recientemente")
    recent_movements: List[Movement] = Field(..., description="Movimientos recientes")
    unlabeled_count: int = Field(..., ge=0, description="Movimientos sin etiquetar")
    active_streams: List[VideoStream] = Field(..., description="Streams activos")
    daily_stats: Dict[str, int] = Field(..., description="Estadísticas del día")
    alerts: List[Dict[str, Any]] = Field(..., description="Alertas activas")


class LabelingResult(BaseModel):
    """Resultado de etiquetado de movimiento"""
    movement_id: str = Field(..., description="ID del movimiento etiquetado")
    label: str = Field(..., description="Etiqueta asignada")
    previous_label: Optional[str] = Field(None, description="Etiqueta anterior si existía")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza en la etiqueta")
    admin_id: str = Field(..., description="ID del administrador")
    timestamp: datetime = Field(..., description="Timestamp del etiquetado")
    kb_updated: bool = Field(..., description="Si se actualizó el KB")
    learning_triggered: bool = Field(..., description="Si se activó el aprendizaje")


class TrainingResult(BaseModel):
    """Resultado de entrenamiento de modelos"""
    model_type: str = Field(..., description="Tipo de modelo entrenado")
    training_duration_seconds: float = Field(..., description="Duración del entrenamiento")
    samples_used: int = Field(..., ge=0, description="Muestras usadas para entrenamiento")
    accuracy_improvement: float = Field(..., description="Mejora en precisión")
    previous_accuracy: float = Field(..., ge=0.0, le=1.0, description="Precisión anterior")
    new_accuracy: float = Field(..., ge=0.0, le=1.0, description="Nueva precisión")
    model_version: str = Field(..., description="Versión del modelo")
    deployment_status: str = Field(..., description="Estado del despliegue")


class AnimalHistory(BaseModel):
    """Historial de un animal específico"""
    animal_id: str = Field(..., description="ID del animal")
    period_days: int = Field(..., description="Período del historial en días")
    total_movements: int = Field(..., ge=0, description="Total de movimientos")
    movement_timeline: List[Movement] = Field(..., description="Timeline de movimientos")
    behavior_patterns: List[BehaviorPattern] = Field(..., description="Patrones de comportamiento")
    activity_by_hour: Dict[str, int] = Field(..., description="Actividad por hora del día")
    location_heatmap: List[Dict[str, Any]] = Field(..., description="Mapa de calor de ubicaciones")
    health_trends: Dict[str, Any] = Field(..., description="Tendencias de salud")
    social_interactions: List[Dict[str, Any]] = Field(..., description="Interacciones sociales")


class ConfigurationStatus(BaseModel):
    """Estado de configuración del sistema"""
    section: str = Field(..., description="Sección de configuración")
    current_config: Dict[str, Any] = Field(..., description="Configuración actual")
    applied_at: datetime = Field(..., description="Timestamp de aplicación")
    applied_by: str = Field(..., description="Usuario que aplicó la configuración")
    validation_status: str = Field(..., description="Estado de validación")
    validation_errors: List[str] = Field(..., description="Errores de validación")


class AlertStatus(BaseModel):
    """Estado de una alerta"""
    alert_id: str = Field(..., description="ID de la alerta")
    alert_type: str = Field(..., description="Tipo de alerta")
    status: str = Field(..., description="Estado de la alerta")
    triggered_at: datetime = Field(..., description="Timestamp de activación")
    message: str = Field(..., description="Mensaje de la alerta")
    severity: str = Field(..., description="Severidad de la alerta")
    acknowledged: bool = Field(..., description="Si la alerta fue reconocida")
    acknowledged_by: Optional[str] = Field(None, description="Usuario que reconoció")
    resolved_at: Optional[datetime] = Field(None, description="Timestamp de resolución")


class MetricsData(BaseModel):
    """Datos de métricas del sistema"""
    timestamp: datetime = Field(..., description="Timestamp de las métricas")
    system_metrics: Dict[str, float] = Field(..., description="Métricas del sistema")
    analysis_metrics: Dict[str, int] = Field(..., description="Métricas de análisis")
    performance_metrics: Dict[str, float] = Field(..., description="Métricas de rendimiento")
    error_metrics: Dict[str, int] = Field(..., description="Métricas de errores")


# Responses específicas para endpoints

class VideoAnalysisResponse(AnimalAIResponse):
    """Response específica para análisis de video"""
    pass


class MovementLabelingResponse(AnimalAIResponse):
    """Response específica para etiquetado de movimientos"""
    pass


class AnimalListResponse(AnimalAIResponse):
    """Response específica para lista de animales"""
    pass


class BehaviorSearchResponse(AnimalAIResponse):
    """Response específica para búsqueda de comportamientos"""
    pass


class SystemHealthResponse(AnimalAIResponse):
    """Response específica para health check"""
    pass


class DashboardResponse(AnimalAIResponse):
    """Response específica para dashboard"""
    pass


