"""
Configuración independiente del ETL Service
Todas las variables de entorno tienen prefijo ETL_ para evitar conflictos
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


class SyncType(str, Enum):
    INCREMENTAL = "incremental"
    FULL = "full"
    TABLES_ONLY = "tables_only"


@dataclass
class DatabaseConfig:
    """Configuración de una base de datos"""
    name: str
    host: str
    port: int = 3306
    user: str = ""
    password: str = ""
    database: str = ""
    ssl_enabled: bool = False
    ssl_ca_path: Optional[str] = None
    connection_timeout: int = 30
    read_timeout: int = 60
    enabled: bool = True
    
    @classmethod
    def from_env(cls, name: str = "default") -> 'DatabaseConfig':
        """Crear configuración desde variables de entorno"""
        prefix = f"ETL_DB_{name.upper()}_" if name != "default" else "ETL_DB_"
        
        return cls(
            name=name,
            host=os.getenv(f"{prefix}HOST", "localhost"),
            port=int(os.getenv(f"{prefix}PORT", "3306")),
            user=os.getenv(f"{prefix}USER", ""),
            password=os.getenv(f"{prefix}PASSWORD", ""),
            database=os.getenv(f"{prefix}DATABASE", ""),
            ssl_enabled=os.getenv(f"{prefix}SSL", "false").lower() == "true",
            ssl_ca_path=os.getenv(f"{prefix}SSL_CA"),
            connection_timeout=int(os.getenv(f"{prefix}TIMEOUT", "30")),
            read_timeout=int(os.getenv(f"{prefix}READ_TIMEOUT", "60")),
            enabled=os.getenv(f"{prefix}ENABLED", "true").lower() == "true"
        )


@dataclass
class LLMConfig:
    """Configuración del LLM para análisis AI"""
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 1000
    timeout: int = 30
    retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Crear configuración LLM desde variables de entorno"""
        provider = LLMProvider(os.getenv("ETL_LLM_PROVIDER", "openai"))
        
        return cls(
            provider=provider,
            api_key=os.getenv("ETL_LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("ETL_LLM_BASE_URL"),
            model=os.getenv("ETL_LLM_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("ETL_LLM_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("ETL_LLM_MAX_TOKENS", "1000")),
            timeout=int(os.getenv("ETL_LLM_TIMEOUT", "30")),
            retries=int(os.getenv("ETL_LLM_RETRIES", "3"))
        )


@dataclass
class KnowledgeBaseConfig:
    """Configuración del Knowledge Base de destino"""
    url: Optional[str] = None
    search_url: Optional[str] = None
    auth_token: Optional[str] = None
    timeout: int = 30
    local_path: Optional[str] = None
    batch_size: int = 50
    
    @classmethod
    def from_env(cls) -> 'KnowledgeBaseConfig':
        """Crear configuración KB desde variables de entorno"""
        return cls(
            url=os.getenv("ETL_KB_URL"),
            search_url=os.getenv("ETL_KB_SEARCH_URL"),
            auth_token=os.getenv("ETL_KB_AUTH_TOKEN"),
            timeout=int(os.getenv("ETL_KB_TIMEOUT", "30")),
            local_path=os.getenv("ETL_KB_LOCAL_PATH"),
            batch_size=int(os.getenv("ETL_KB_BATCH_SIZE", "50"))
        )


@dataclass
class ETLConfig:
    """Configuración principal del ETL Service"""
    
    # Servicio
    service_name: str = field(default_factory=lambda: os.getenv("ETL_SERVICE_NAME", "etl-service"))
    service_port: int = field(default_factory=lambda: int(os.getenv("ETL_SERVICE_PORT", "9000")))
    env: str = field(default_factory=lambda: os.getenv("ETL_ENV", "production"))
    log_level: str = field(default_factory=lambda: os.getenv("ETL_LOG_LEVEL", "INFO"))
    
    # ETL Pipeline
    etl_enabled: bool = field(default_factory=lambda: os.getenv("ETL_ENABLED", "true").lower() == "true")
    batch_size: int = field(default_factory=lambda: int(os.getenv("ETL_BATCH_SIZE", "500")))
    incremental_hours: int = field(default_factory=lambda: int(os.getenv("ETL_INCREMENTAL_HOURS", "2")))
    full_sync_time: str = field(default_factory=lambda: os.getenv("ETL_FULL_SYNC_TIME", "02:00"))
    retry_attempts: int = field(default_factory=lambda: int(os.getenv("ETL_RETRY_ATTEMPTS", "3")))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("ETL_TIMEOUT_SECONDS", "300")))
    
    # Calidad
    quality_threshold: float = field(default_factory=lambda: float(os.getenv("ETL_QUALITY_THRESHOLD", "0.8")))
    min_text_length: int = field(default_factory=lambda: int(os.getenv("ETL_MIN_TEXT_LENGTH", "50")))
    max_docs_per_batch: int = field(default_factory=lambda: int(os.getenv("ETL_MAX_DOCS_PER_BATCH", "100")))
    
    # Seguridad
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("ETL_API_KEY"))
    cors_origins: List[str] = field(default_factory=lambda: _parse_cors_origins())
    encrypt_sensitive: bool = field(default_factory=lambda: os.getenv("ETL_ENCRYPT_SENSITIVE_DATA", "false").lower() == "true")
    
    # Logging y Monitoreo
    log_file: str = field(default_factory=lambda: os.getenv("ETL_LOG_FILE", "logs/etl-service.log"))
    metrics_enabled: bool = field(default_factory=lambda: os.getenv("ETL_METRICS_ENABLED", "true").lower() == "true")
    metrics_port: int = field(default_factory=lambda: int(os.getenv("ETL_METRICS_PORT", "9001")))
    
    # Alertas
    alert_webhook: Optional[str] = field(default_factory=lambda: os.getenv("ETL_ALERT_WEBHOOK"))
    alert_email: Optional[str] = field(default_factory=lambda: os.getenv("ETL_ALERT_EMAIL"))
    alert_on_error: bool = field(default_factory=lambda: os.getenv("ETL_ALERT_ON_ERROR", "true").lower() == "true")
    
    # Configuraciones de componentes
    databases: Dict[str, DatabaseConfig] = field(default_factory=dict)
    llm_config: LLMConfig = field(default_factory=LLMConfig.from_env)
    kb_config: KnowledgeBaseConfig = field(default_factory=KnowledgeBaseConfig.from_env)
    
    def __post_init__(self):
        """Inicialización post-creación"""
        self._load_database_configs()
        self._validate_config()
    
    def _load_database_configs(self):
        """Cargar configuraciones de todas las bases de datos desde env"""
        
        # BD principal (sin sufijo)
        if os.getenv("ETL_DB_HOST"):
            self.databases["default"] = DatabaseConfig.from_env("default")
        
        # BDs adicionales (buscar patrones ETL_DB_NAME_HOST)
        for key in os.environ:
            if key.startswith("ETL_DB_") and key.endswith("_HOST"):
                # Extraer nombre de BD: ETL_DB_INVENTORY_HOST -> inventory
                db_name = key[7:-5].lower()  # Remover ETL_DB_ y _HOST
                if db_name != "default" and db_name:
                    self.databases[db_name] = DatabaseConfig.from_env(db_name)
    
    def _validate_config(self):
        """Validar configuración"""
        
        if not self.databases:
            raise ValueError("No se encontraron configuraciones de BD. Configurar ETL_DB_HOST mínimo.")
        
        # Validar que al menos una BD esté habilitada
        enabled_dbs = [db for db in self.databases.values() if db.enabled]
        if not enabled_dbs:
            raise ValueError("Al menos una base de datos debe estar habilitada.")
        
        # Validar configuración LLM
        if not self.llm_config.api_key and self.llm_config.provider != LLMProvider.LOCAL:
            raise ValueError(f"API key requerida para proveedor LLM: {self.llm_config.provider}")
        
        # Validar puerto disponible
        if not (1024 <= self.service_port <= 65535):
            raise ValueError(f"Puerto inválido: {self.service_port}")
    
    def get_database_config(self, name: str = "default") -> DatabaseConfig:
        """Obtener configuración de BD específica"""
        if name not in self.databases:
            raise ValueError(f"Base de datos '{name}' no configurada")
        return self.databases[name]
    
    def get_enabled_databases(self) -> List[str]:
        """Obtener lista de BDs habilitadas"""
        return [name for name, config in self.databases.items() if config.enabled]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario (para logs/debug)"""
        return {
            "service": {
                "name": self.service_name,
                "port": self.service_port,
                "env": self.env,
                "log_level": self.log_level
            },
            "etl": {
                "enabled": self.etl_enabled,
                "batch_size": self.batch_size,
                "incremental_hours": self.incremental_hours,
                "quality_threshold": self.quality_threshold
            },
            "databases": {
                name: {
                    "host": config.host,
                    "database": config.database,
                    "enabled": config.enabled
                }
                for name, config in self.databases.items()
            },
            "llm": {
                "provider": self.llm_config.provider,
                "model": self.llm_config.model,
                "has_api_key": bool(self.llm_config.api_key)
            },
            "kb": {
                "url": self.kb_config.url,
                "local_path": self.kb_config.local_path
            }
        }


def _parse_cors_origins() -> List[str]:
    """Parsear CORS origins desde variable de entorno"""
    cors_env = os.getenv("ETL_CORS_ORIGINS", "*")
    if cors_env == "*":
        return ["*"]
    return [origin.strip() for origin in cors_env.split(",") if origin.strip()]


# Configuración global singleton
_config_instance: Optional[ETLConfig] = None


def get_config() -> ETLConfig:
    """Obtener instancia singleton de configuración"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ETLConfig()
    return _config_instance


def reload_config() -> ETLConfig:
    """Recargar configuración desde variables de entorno"""
    global _config_instance
    _config_instance = ETLConfig()
    return _config_instance


# Ejemplo de uso y testing
if __name__ == "__main__":
    # Configuración de ejemplo
    os.environ.update({
        "ETL_SERVICE_NAME": "etl-production",
        "ETL_SERVICE_PORT": "9000",
        "ETL_DB_HOST": "mysql.prod.com",
        "ETL_DB_USER": "readonly",
        "ETL_DB_DATABASE": "production",
        "ETL_DB_INVENTORY_HOST": "inventory.prod.com",
        "ETL_DB_INVENTORY_DATABASE": "inventory",
        "ETL_LLM_PROVIDER": "openai",
        "ETL_LLM_API_KEY": "sk-test",
        "ETL_KB_URL": "http://kb-server:7070/tools/kb_ingest"
    })
    
    config = ETLConfig()
    print(json.dumps(config.to_dict(), indent=2))
