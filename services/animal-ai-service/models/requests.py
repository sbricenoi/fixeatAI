"""
Modelos de request para Animal-AI Service
Definición de esquemas de entrada para todos los endpoints
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class VideoAnalysisRequest(BaseModel):
    """Request para iniciar análisis de video"""
    source: str = Field(..., description="URL o path del video/stream a analizar")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    analysis_config: Optional[Dict[str, Any]] = Field(None, description="Configuración específica de análisis")
    
    @validator('source')
    def validate_source(cls, v):
        if not v or not v.strip():
            raise ValueError("Source no puede estar vacío")
        return v.strip()


class LabelMovementRequest(BaseModel):
    """Request para etiquetar un movimiento manualmente"""
    movement_id: str = Field(..., description="ID del movimiento a etiquetar")
    label: str = Field(..., description="Etiqueta del movimiento")
    admin_id: str = Field(..., description="ID del administrador que etiqueta")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confianza en la etiqueta")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    
    @validator('label')
    def validate_label(cls, v):
        if not v or not v.strip():
            raise ValueError("Label no puede estar vacío")
        return v.strip().lower()
    
    @validator('movement_id')
    def validate_movement_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Movement ID no puede estar vacío")
        return v.strip()


class AnimalIdentificationRequest(BaseModel):
    """Request para identificar un animal específico"""
    image_data: str = Field(..., description="Imagen en base64")
    animal_id: Optional[str] = Field(None, description="ID del animal si se conoce")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")


class BehaviorSearchRequest(BaseModel):
    """Request para buscar comportamientos en el KB"""
    query: str = Field(..., description="Consulta de búsqueda")
    animal_id: Optional[str] = Field(None, description="Filtrar por animal específico")
    behavior_type: Optional[str] = Field(None, description="Filtrar por tipo de comportamiento")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    limit: int = Field(10, ge=1, le=100, description="Límite de resultados")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")


class StreamConfigRequest(BaseModel):
    """Request para configurar un stream de video"""
    stream_id: str = Field(..., description="ID del stream")
    source: str = Field(..., description="Fuente del video")
    resolution: Optional[str] = Field("1920x1080", description="Resolución del video")
    fps: Optional[int] = Field(30, ge=1, le=60, description="Frames por segundo")
    analysis_enabled: bool = Field(True, description="Habilitar análisis automático")
    recording_enabled: bool = Field(False, description="Habilitar grabación")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")


class RetrainModelRequest(BaseModel):
    """Request para reentrenar modelos"""
    model_type: str = Field(..., description="Tipo de modelo a reentrenar")
    use_recent_data: bool = Field(True, description="Usar datos recientes")
    days_back: int = Field(30, ge=1, le=365, description="Días hacia atrás para datos")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    
    @validator('model_type')
    def validate_model_type(cls, v):
        allowed_types = ['movement_classifier', 'behavior_classifier', 'individual_tracker', 'all']
        if v not in allowed_types:
            raise ValueError(f"Model type debe ser uno de: {allowed_types}")
        return v


class MovementFilterRequest(BaseModel):
    """Request para filtrar movimientos"""
    animal_id: Optional[str] = Field(None, description="ID del animal")
    movement_type: Optional[str] = Field(None, description="Tipo de movimiento")
    confidence_min: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confianza mínima")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    is_labeled: Optional[bool] = Field(None, description="Filtrar por etiquetados/no etiquetados")
    limit: int = Field(50, ge=1, le=500, description="Límite de resultados")
    offset: int = Field(0, ge=0, description="Offset para paginación")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")


class AlertConfigRequest(BaseModel):
    """Request para configurar alertas"""
    alert_type: str = Field(..., description="Tipo de alerta")
    enabled: bool = Field(True, description="Habilitar alerta")
    threshold: Optional[float] = Field(None, description="Umbral para la alerta")
    webhook_url: Optional[str] = Field(None, description="URL del webhook")
    email: Optional[str] = Field(None, description="Email para notificaciones")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    
    @validator('alert_type')
    def validate_alert_type(cls, v):
        allowed_types = ['unusual_behavior', 'system_error', 'low_confidence', 'new_animal']
        if v not in allowed_types:
            raise ValueError(f"Alert type debe ser uno de: {allowed_types}")
        return v


class KBIngestRequest(BaseModel):
    """Request para ingerir datos en el KB"""
    content: str = Field(..., description="Contenido a ingerir")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del contenido")
    source_type: str = Field("animal_behavior", description="Tipo de fuente")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content no puede estar vacío")
        if len(v.strip()) < 10:
            raise ValueError("Content debe tener al menos 10 caracteres")
        return v.strip()


class AnimalRegistrationRequest(BaseModel):
    """Request para registrar un nuevo animal"""
    animal_id: Optional[str] = Field(None, description="ID del animal (se genera si no se proporciona)")
    species: str = Field(..., description="Especie del animal")
    individual_markers: List[str] = Field(..., description="Características únicas del animal")
    initial_image: Optional[str] = Field(None, description="Imagen inicial en base64")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    
    @validator('species')
    def validate_species(cls, v):
        if not v or not v.strip():
            raise ValueError("Species no puede estar vacío")
        return v.strip().lower()
    
    @validator('individual_markers')
    def validate_markers(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Individual markers no puede estar vacío")
        return [marker.strip() for marker in v if marker.strip()]


class BehaviorAnalysisRequest(BaseModel):
    """Request para análisis de comportamiento específico"""
    animal_id: str = Field(..., description="ID del animal")
    time_window_hours: int = Field(24, ge=1, le=168, description="Ventana de tiempo en horas")
    analysis_type: str = Field("general", description="Tipo de análisis")
    include_predictions: bool = Field(True, description="Incluir predicciones")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed_types = ['general', 'feeding', 'social', 'movement', 'health']
        if v not in allowed_types:
            raise ValueError(f"Analysis type debe ser uno de: {allowed_types}")
        return v


class SystemConfigRequest(BaseModel):
    """Request para configurar el sistema"""
    config_section: str = Field(..., description="Sección de configuración")
    config_data: Dict[str, Any] = Field(..., description="Datos de configuración")
    apply_immediately: bool = Field(False, description="Aplicar inmediatamente")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad")
    
    @validator('config_section')
    def validate_config_section(cls, v):
        allowed_sections = ['video', 'analysis', 'kb', 'monitoring', 'security']
        if v not in allowed_sections:
            raise ValueError(f"Config section debe ser uno de: {allowed_sections}")
        return v

