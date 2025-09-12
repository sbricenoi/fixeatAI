# 🔄 ETL Service - Módulo Independiente

## 🎯 **Visión General**

**ETL Service** es un microservicio **completamente independiente** que extrae datos de bases de datos MySQL y los transforma inteligentemente usando IA para alimentar Knowledge Bases. Puede ejecutarse en cualquier infraestructura, separado de otros servicios FixeatAI.

## 🏗️ **Arquitectura Modular**

```
ETL-SERVICE (Puerto 9000)
├── 🔍 Context Discovery     # Auto-documentación BD
├── 🤖 AI Schema Analyzer    # Evaluación inteligente  
├── ⚙️ Config Generator      # Configuración automática
├── 🔄 ETL Pipeline          # Extracción + Transformación
├── 📊 Quality Monitor       # Métricas y alertas
└── 🕐 Scheduler             # Ejecución programada
```

## ✅ **Características de Independencia**

### **🔧 Configuración Autónoma**
- **Variables propias**: `ETL_*` namespace exclusivo
- **Sin dependencias**: No requiere otros servicios FixeatAI
- **Multi-BD**: Soporte para múltiples bases de datos
- **Flexible**: Puede conectarse a cualquier KB remoto

### **🚀 Despliegue Independiente**
- **Docker standalone**: Su propio `Dockerfile` y `docker-compose`
- **Escalable**: Múltiples instancias independientes
- **Portable**: Puede ejecutarse en cualquier infraestructura
- **Configurable**: Diferentes entornos sin conflicts

### **📡 Integración por API**
- **RESTful**: Endpoints estándar para integración
- **Webhooks**: Notificaciones de progreso
- **Health checks**: Monitoreo independiente
- **Logging**: Sistema de logs propio

## 🚀 **Quick Start Independiente**

### **1. Configuración**
```bash
# Solo las variables que necesita ETL Service
ETL_SERVICE_PORT=9000
ETL_DB_HOST=mysql-server.com
ETL_DB_USER=readonly_user
ETL_DB_PASSWORD=secret
ETL_DB_DATABASE=production_db

# IA para transformación (opcional: local LLM)
ETL_LLM_PROVIDER=openai  # o 'ollama' para local
ETL_LLM_API_KEY=sk-your-key
ETL_LLM_MODEL=gpt-4o-mini

# KB de destino (puede ser cualquier KB remoto)
ETL_KB_URL=http://otro-servidor:7070/tools/kb_ingest
ETL_KB_AUTH_TOKEN=optional-auth-token
```

### **2. Ejecutar Standalone**
```bash
# Docker independiente
docker run -p 9000:9000 \
  -e ETL_DB_HOST=mysql.com \
  -e ETL_LLM_API_KEY=sk-key \
  fixeatai-etl:latest

# O local
cd services/etl-service
python -m uvicorn main:app --port 9000
```

### **3. Verificar Independencia**
```bash
# Health check independiente
curl http://localhost:9000/health

# Descubrir BD sin otros servicios
curl -X POST "http://localhost:9000/api/v1/discover-schema"

# ETL completo autónomo
curl -X POST "http://localhost:9000/api/v1/etl/sync-all"
```

## 📋 **Casos de Uso Independientes**

### **🏢 Escenario 1: ETL en Servidor Separado**
```yaml
# docker-compose.etl.yml
version: "3.9"
services:
  etl-service:
    image: fixeatai-etl:latest
    ports:
      - "9000:9000"
    environment:
      - ETL_DB_HOST=production-mysql.amazonaws.com
      - ETL_KB_URL=http://kb-server:7070/tools/kb_ingest
    volumes:
      - etl-configs:/app/configs
      - etl-logs:/app/logs
```

### **🔄 Escenario 2: Múltiples ETL para Diferentes BDs**
```bash
# ETL para BD de Servicios
docker run -p 9001:9000 \
  -e ETL_SERVICE_NAME=services-etl \
  -e ETL_DB_DATABASE=services_db \
  fixeatai-etl:latest

# ETL para BD de Inventarios  
docker run -p 9002:9000 \
  -e ETL_SERVICE_NAME=inventory-etl \
  -e ETL_DB_DATABASE=inventory_db \
  fixeatai-etl:latest
```

### **🌐 Escenario 3: ETL Distribuido Multi-Región**
```bash
# Región US-East
docker run -p 9000:9000 \
  -e ETL_REGION=us-east \
  -e ETL_DB_HOST=us-east-mysql.com \
  -e ETL_KB_URL=http://us-east-kb:7070 \
  fixeatai-etl:latest

# Región EU-West  
docker run -p 9000:9000 \
  -e ETL_REGION=eu-west \
  -e ETL_DB_HOST=eu-west-mysql.com \
  -e ETL_KB_URL=http://eu-west-kb:7070 \
  fixeatai-etl:latest
```

## 🔧 **Variables de Entorno Completas**

### **🗄️ Base de Datos**
```bash
# Conexión principal
ETL_DB_HOST=mysql-server.com
ETL_DB_PORT=3306
ETL_DB_USER=readonly_user
ETL_DB_PASSWORD=secret_password
ETL_DB_DATABASE=main_database

# Múltiples BDs (opcional)
ETL_DB_INVENTORY_HOST=inventory-mysql.com
ETL_DB_INVENTORY_DATABASE=inventory_db
ETL_DB_INVENTORY_USER=inv_readonly
```

### **🤖 Inteligencia Artificial**
```bash
# Proveedor LLM
ETL_LLM_PROVIDER=openai  # openai, ollama, anthropic, azure
ETL_LLM_API_KEY=sk-your-openai-key
ETL_LLM_MODEL=gpt-4o-mini
ETL_LLM_TEMPERATURE=0.1
ETL_LLM_MAX_TOKENS=1000

# LLM Local (Ollama)
ETL_LLM_BASE_URL=http://ollama-server:11434/v1
ETL_LLM_LOCAL_MODEL=llama3.1:8b
```

### **📡 Knowledge Base de Destino**
```bash
# KB Remoto
ETL_KB_URL=http://kb-server:7070/tools/kb_ingest
ETL_KB_SEARCH_URL=http://kb-server:7070/tools/kb_search
ETL_KB_AUTH_TOKEN=optional-bearer-token
ETL_KB_TIMEOUT=30

# KB Local (si está en la misma máquina)
ETL_KB_LOCAL_PATH=/data/chroma_etl
```

### **⚙️ Configuración ETL**
```bash
# Servicio
ETL_SERVICE_PORT=9000
ETL_SERVICE_NAME=etl-production
ETL_LOG_LEVEL=info

# Pipeline
ETL_ENABLED=true
ETL_BATCH_SIZE=500
ETL_INCREMENTAL_HOURS=2
ETL_FULL_SYNC_TIME=02:00
ETL_RETRY_ATTEMPTS=3
ETL_TIMEOUT_SECONDS=300

# Calidad
ETL_QUALITY_THRESHOLD=0.8
ETL_MIN_TEXT_LENGTH=50
ETL_MAX_DOCS_PER_BATCH=100
```

### **📊 Monitoreo y Alertas**
```bash
# Logging
ETL_LOG_FILE=/app/logs/etl.log
ETL_LOG_ROTATION=daily
ETL_LOG_RETENTION_DAYS=30

# Métricas
ETL_METRICS_ENABLED=true
ETL_METRICS_PORT=9001
ETL_PROMETHEUS_ENDPOINT=/metrics

# Alertas
ETL_ALERT_WEBHOOK=https://hooks.slack.com/your-webhook
ETL_ALERT_EMAIL=admin@company.com
ETL_ALERT_ON_ERROR=true
ETL_ALERT_ON_LOW_QUALITY=true
```

### **🔐 Seguridad**
```bash
# Autenticación
ETL_API_KEY=your-api-key-for-etl-endpoints
ETL_CORS_ORIGINS=http://localhost:3000,https://admin.company.com

# Encriptación
ETL_ENCRYPT_SENSITIVE_DATA=true
ETL_ENCRYPTION_KEY=your-32-char-encryption-key
```

## 🌟 **Ventajas de la Independencia**

### **🚀 Escalabilidad**
- **Horizontal**: Múltiples instancias ETL
- **Vertical**: Recursos dedicados por ETL
- **Regional**: ETL distribuido geográficamente

### **🔧 Mantenimiento**
- **Actualizaciones**: Sin afectar otros servicios
- **Debugging**: Logs y métricas independientes
- **Testing**: Entorno aislado de pruebas

### **🏢 Organizacional**
- **Equipos**: Diferentes equipos pueden gestionar diferentes ETLs
- **Responsabilidades**: Ownership claro por BD/dominio
- **Presupuesto**: Costos separados por ETL

### **🔒 Seguridad**
- **Aislamiento**: Falla de un ETL no afecta otros
- **Permisos**: Acceso granular por BD
- **Auditoria**: Logs independientes por ETL

## 📚 **Documentación Adicional**

- [Instalación y Configuración](./docs/installation.md)
- [API Reference](./docs/api-reference.md)
- [Troubleshooting](./docs/troubleshooting.md)
- [Performance Tuning](./docs/performance.md)
- [Security Best Practices](./docs/security.md)
- [Multi-Database Setup](./docs/multi-database.md)
- [Integration Examples](./docs/integration-examples.md)

**¡ETL Service: Completamente independiente, altamente escalable!** 🚀🔄
