"""
Configuración independiente del Animal-AI Service
Todas las variables de entorno tienen prefijo ANIMAL_ para evitar conflictos
"""

from __future__ import annotations

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class LLMProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    LOCAL = "local"


class AnalysisMode(str, Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    RESEARCH = "research"


class MovementSensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class VideoConfig:
    """Configuración de captura de video"""
    source: str
    backup_source: Optional[str] = None
    resolution: str = "1920x1080"
    fps: int = 30
    buffer_size: int = 100
    
    @classmethod
    def from_env(cls) -> 'VideoConfig':
        """Crear configuración desde variables de entorno"""
        return cls(
            source=os.getenv("ANIMAL_VIDEO_SOURCE", ""),
            backup_source=os.getenv("ANIMAL_VIDEO_BACKUP_SOURCE"),
            resolution=os.getenv("ANIMAL_VIDEO_RESOLUTION", "1920x1080"),
            fps=int(os.getenv("ANIMAL_VIDEO_FPS", "30")),
            buffer_size=int(os.getenv("ANIMAL_VIDEO_BUFFER_SIZE", "100"))
        )


@dataclass
class StorageConfig:
    """Configuración de almacenamiento"""
    path: str
    retention_days: int = 30
    max_size_gb: int = 500
    
    @classmethod
    def from_env(cls) -> 'StorageConfig':
        """Crear configuración desde variables de entorno"""
        return cls(
            path=os.getenv("ANIMAL_STORAGE_PATH", "/data/animal-videos"),
            retention_days=int(os.getenv("ANIMAL_STORAGE_RETENTION_DAYS", "30")),
            max_size_gb=int(os.getenv("ANIMAL_STORAGE_MAX_SIZE_GB", "500"))
        )


@dataclass
class LLMConfig:
    """Configuración del LLM para análisis"""
    provider: LLMProvider
    api_key: str
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 1000
    base_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Crear configuración desde variables de entorno"""
        provider = LLMProvider(os.getenv("ANIMAL_LLM_PROVIDER", "openai"))
        
        return cls(
            provider=provider,
            api_key=os.getenv("ANIMAL_LLM_API_KEY", ""),
            model=os.getenv("ANIMAL_LLM_MODEL", "gpt-4o"),
            temperature=float(os.getenv("ANIMAL_LLM_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("ANIMAL_LLM_MAX_TOKENS", "1000")),
            base_url=os.getenv("ANIMAL_LLM_BASE_URL")
        )


@dataclass
class CVModelsConfig:
    """Configuración de modelos de Computer Vision"""
    yolo_model: str = "yolov8n.pt"
    tracking_model: str = "deepsort"
    pose_model: str = "mediapipe"
    confidence_threshold: float = 0.7
    
    @classmethod
    def from_env(cls) -> 'CVModelsConfig':
        """Crear configuración desde variables de entorno"""
        return cls(
            yolo_model=os.getenv("ANIMAL_YOLO_MODEL", "yolov8n.pt"),
            tracking_model=os.getenv("ANIMAL_TRACKING_MODEL", "deepsort"),
            pose_model=os.getenv("ANIMAL_POSE_MODEL", "mediapipe"),
            confidence_threshold=float(os.getenv("ANIMAL_CONFIDENCE_THRESHOLD", "0.7"))
        )


@dataclass
class KBConfig:
    """Configuración de Knowledge Base"""
    url: str
    search_url: str
    auth_token: Optional[str] = None
    timeout: int = 30
    source_type: str = "animal_behavior"
    quality_threshold: float = 0.8
    
    @classmethod
    def from_env(cls) -> 'KBConfig':
        """Crear configuración desde variables de entorno"""
        return cls(
            url=os.getenv("ANIMAL_KB_URL", ""),
            search_url=os.getenv("ANIMAL_KB_SEARCH_URL", ""),
            auth_token=os.getenv("ANIMAL_KB_AUTH_TOKEN"),
            timeout=int(os.getenv("ANIMAL_KB_TIMEOUT", "30")),
            source_type=os.getenv("ANIMAL_KB_SOURCE_TYPE", "animal_behavior"),
            quality_threshold=float(os.getenv("ANIMAL_KB_QUALITY_THRESHOLD", "0.8"))
        )


@dataclass
class AnalysisConfig:
    """Configuración de análisis"""
    enabled: bool = True
    interval_seconds: int = 1
    movement_sensitivity: MovementSensitivity = MovementSensitivity.MEDIUM
    individual_tracking: bool = True
    behavior_learning: bool = True
    min_movement_duration: int = 2
    max_animals_per_frame: int = 10
    tracking_confidence: float = 0.8
    
    @classmethod
    def from_env(cls) -> 'AnalysisConfig':
        """Crear configuración desde variables de entorno"""
        return cls(
            enabled=os.getenv("ANIMAL_ANALYSIS_ENABLED", "true").lower() == "true",
            interval_seconds=int(os.getenv("ANIMAL_ANALYSIS_INTERVAL_SECONDS", "1")),
            movement_sensitivity=MovementSensitivity(os.getenv("ANIMAL_MOVEMENT_SENSITIVITY", "medium")),
            individual_tracking=os.getenv("ANIMAL_INDIVIDUAL_TRACKING", "true").lower() == "true",
            behavior_learning=os.getenv("ANIMAL_BEHAVIOR_LEARNING", "true").lower() == "true",
            min_movement_duration=int(os.getenv("ANIMAL_MIN_MOVEMENT_DURATION", "2")),
            max_animals_per_frame=int(os.getenv("ANIMAL_MAX_ANIMALS_PER_FRAME", "10")),
            tracking_confidence=float(os.getenv("ANIMAL_TRACKING_CONFIDENCE", "0.8"))
        )


@dataclass
class MonitoringConfig:
    """Configuración de monitoreo"""
    log_file: str
    log_rotation: str = "daily"
    log_retention_days: int = 30
    metrics_enabled: bool = True
    metrics_port: int = 8081
    prometheus_endpoint: str = "/metrics"
    alert_webhook: Optional[str] = None
    alert_email: Optional[str] = None
    alert_on_unusual_behavior: bool = True
    alert_on_system_error: bool = True
    
    @classmethod
    def from_env(cls) -> 'MonitoringConfig':
        """Crear configuración desde variables de entorno"""
        return cls(
            log_file=os.getenv("ANIMAL_LOG_FILE", "/app/logs/animal-ai.log"),
            log_rotation=os.getenv("ANIMAL_LOG_ROTATION", "daily"),
            log_retention_days=int(os.getenv("ANIMAL_LOG_RETENTION_DAYS", "30")),
            metrics_enabled=os.getenv("ANIMAL_METRICS_ENABLED", "true").lower() == "true",
            metrics_port=int(os.getenv("ANIMAL_METRICS_PORT", "8081")),
            prometheus_endpoint=os.getenv("ANIMAL_PROMETHEUS_ENDPOINT", "/metrics"),
            alert_webhook=os.getenv("ANIMAL_ALERT_WEBHOOK"),
            alert_email=os.getenv("ANIMAL_ALERT_EMAIL"),
            alert_on_unusual_behavior=os.getenv("ANIMAL_ALERT_ON_UNUSUAL_BEHAVIOR", "true").lower() == "true",
            alert_on_system_error=os.getenv("ANIMAL_ALERT_ON_SYSTEM_ERROR", "true").lower() == "true"
        )


@dataclass
class SecurityConfig:
    """Configuración de seguridad"""
    api_key: Optional[str] = None
    cors_origins: List[str] = field(default_factory=list)
    anonymize_data: bool = False
    encrypt_videos: bool = True
    encryption_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Crear configuración desde variables de entorno"""
        cors_origins_str = os.getenv("ANIMAL_CORS_ORIGINS", "")
        cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
        
        return cls(
            api_key=os.getenv("ANIMAL_API_KEY"),
            cors_origins=cors_origins,
            anonymize_data=os.getenv("ANIMAL_ANONYMIZE_DATA", "false").lower() == "true",
            encrypt_videos=os.getenv("ANIMAL_ENCRYPT_VIDEOS", "true").lower() == "true",
            encryption_key=os.getenv("ANIMAL_ENCRYPTION_KEY")
        )


@dataclass
class AnimalAIConfig:
    """Configuración principal del Animal-AI Service"""
    
    # Configuración del servicio
    service_port: int = 8080
    service_name: str = "animal-ai-service"
    log_level: str = "INFO"
    debug_mode: bool = False
    
    # Configuraciones específicas
    video: VideoConfig = field(default_factory=VideoConfig.from_env)
    storage: StorageConfig = field(default_factory=StorageConfig.from_env)
    llm: LLMConfig = field(default_factory=LLMConfig.from_env)
    cv_models: CVModelsConfig = field(default_factory=CVModelsConfig.from_env)
    kb: KBConfig = field(default_factory=KBConfig.from_env)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig.from_env)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig.from_env)
    security: SecurityConfig = field(default_factory=SecurityConfig.from_env)
    
    def __post_init__(self):
        """Inicialización posterior"""
        # Configuración del servicio desde variables de entorno
        self.service_port = int(os.getenv("ANIMAL_SERVICE_PORT", "8080"))
        self.service_name = os.getenv("ANIMAL_SERVICE_NAME", "animal-ai-service")
        self.log_level = os.getenv("ANIMAL_LOG_LEVEL", "INFO").upper()
        self.debug_mode = os.getenv("ANIMAL_DEBUG_MODE", "false").lower() == "true"
        
        # Validaciones
        self._validate_config()
    
    def _validate_config(self):
        """Validar configuración"""
        errors = []
        
        # Validar LLM
        if not self.llm.api_key and self.llm.provider == LLMProvider.OPENAI:
            errors.append("ANIMAL_LLM_API_KEY es requerido para OpenAI")
        
        # Validar KB
        if not self.kb.url:
            errors.append("ANIMAL_KB_URL es requerido")
        
        # Validar video source
        if not self.video.source:
            errors.append("ANIMAL_VIDEO_SOURCE es requerido")
        
        if errors:
            raise ValueError(f"Errores de configuración: {', '.join(errors)}")
    
    @property
    def cors_origins(self) -> List[str]:
        """Obtener orígenes CORS permitidos"""
        return self.security.cors_origins or ["*"]
    
    @property
    def metrics_enabled(self) -> bool:
        """Verificar si las métricas están habilitadas"""
        return self.monitoring.metrics_enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return {
            "service": {
                "port": self.service_port,
                "name": self.service_name,
                "log_level": self.log_level,
                "debug_mode": self.debug_mode
            },
            "video": {
                "source": self.video.source,
                "resolution": self.video.resolution,
                "fps": self.video.fps
            },
            "llm": {
                "provider": self.llm.provider.value,
                "model": self.llm.model,
                "temperature": self.llm.temperature
            },
            "analysis": {
                "enabled": self.analysis.enabled,
                "movement_sensitivity": self.analysis.movement_sensitivity.value,
                "individual_tracking": self.analysis.individual_tracking,
                "behavior_learning": self.analysis.behavior_learning
            },
            "kb": {
                "url": self.kb.url,
                "source_type": self.kb.source_type,
                "quality_threshold": self.kb.quality_threshold
            }
        }
    
    def get_env_template(self) -> str:
        """Generar template de variables de entorno"""
        return """
# ==================== ANIMAL-AI SERVICE CONFIGURATION ====================

# Servicio
ANIMAL_SERVICE_PORT=8080
ANIMAL_SERVICE_NAME=animal-ai-production
ANIMAL_LOG_LEVEL=info
ANIMAL_DEBUG_MODE=false

# Video
ANIMAL_VIDEO_SOURCE=rtsp://camera.local/stream
ANIMAL_VIDEO_BACKUP_SOURCE=rtsp://backup-camera.local/stream
ANIMAL_VIDEO_RESOLUTION=1920x1080
ANIMAL_VIDEO_FPS=30
ANIMAL_VIDEO_BUFFER_SIZE=100

# Almacenamiento
ANIMAL_STORAGE_PATH=/data/animal-videos
ANIMAL_STORAGE_RETENTION_DAYS=30
ANIMAL_STORAGE_MAX_SIZE_GB=500

# LLM
ANIMAL_LLM_PROVIDER=openai
ANIMAL_LLM_API_KEY=sk-your-openai-key
ANIMAL_LLM_MODEL=gpt-4o
ANIMAL_LLM_TEMPERATURE=0.1
ANIMAL_LLM_MAX_TOKENS=1000

# Computer Vision
ANIMAL_YOLO_MODEL=yolov8n.pt
ANIMAL_TRACKING_MODEL=deepsort
ANIMAL_POSE_MODEL=mediapipe
ANIMAL_CONFIDENCE_THRESHOLD=0.7

# Knowledge Base
ANIMAL_KB_URL=http://kb-server:7070/tools/kb_ingest
ANIMAL_KB_SEARCH_URL=http://kb-server:7070/tools/kb_search
ANIMAL_KB_AUTH_TOKEN=optional-bearer-token
ANIMAL_KB_TIMEOUT=30
ANIMAL_KB_SOURCE_TYPE=animal_behavior
ANIMAL_KB_QUALITY_THRESHOLD=0.8

# Análisis
ANIMAL_ANALYSIS_ENABLED=true
ANIMAL_ANALYSIS_INTERVAL_SECONDS=1
ANIMAL_MOVEMENT_SENSITIVITY=medium
ANIMAL_INDIVIDUAL_TRACKING=true
ANIMAL_BEHAVIOR_LEARNING=true
ANIMAL_MIN_MOVEMENT_DURATION=2
ANIMAL_MAX_ANIMALS_PER_FRAME=10
ANIMAL_TRACKING_CONFIDENCE=0.8

# Monitoreo
ANIMAL_LOG_FILE=/app/logs/animal-ai.log
ANIMAL_LOG_ROTATION=daily
ANIMAL_LOG_RETENTION_DAYS=30
ANIMAL_METRICS_ENABLED=true
ANIMAL_METRICS_PORT=8081
ANIMAL_PROMETHEUS_ENDPOINT=/metrics
ANIMAL_ALERT_WEBHOOK=https://hooks.slack.com/your-webhook
ANIMAL_ALERT_EMAIL=admin@farm.com
ANIMAL_ALERT_ON_UNUSUAL_BEHAVIOR=true
ANIMAL_ALERT_ON_SYSTEM_ERROR=true

# Seguridad
ANIMAL_API_KEY=your-api-key-for-animal-endpoints
ANIMAL_CORS_ORIGINS=http://localhost:3000,https://admin.farm.com
ANIMAL_ANONYMIZE_DATA=false
ANIMAL_ENCRYPT_VIDEOS=true
ANIMAL_ENCRYPTION_KEY=your-32-char-encryption-key
"""

