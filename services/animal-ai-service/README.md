# 🐾 Animal-AI Service - Análisis de Comportamiento Animal

## 🎯 **Visión General**

**Animal-AI Service** es un microservicio **completamente independiente** que analiza comportamientos y movimientos de animales usando visión computacional y GPT-4o. Identifica individuos, clasifica movimientos y aprende continuamente mediante etiquetado manual.

## 🏗️ **Arquitectura Modular**

```
ANIMAL-AI-SERVICE (Puerto 8080)
├── 📹 Video Processor        # Captura y extracción de frames
├── 🧠 Movement Analyzer      # Análisis con OpenCV + YOLO
├── 👁️ Individual Tracker     # Identificación y seguimiento
├── 🏷️ Behavior Classifier    # Clasificación de comportamientos
├── 🖥️ Admin Interface        # Interfaz de etiquetado
├── 📊 Learning Engine        # Aprendizaje continuo
└── 🔗 KB Integration         # Conexión con Knowledge Base
```

## ✅ **Características de Independencia**

### **🔧 Configuración Autónoma**
- **Variables propias**: `ANIMAL_*` namespace exclusivo
- **Sin dependencias**: No requiere otros servicios FixeatAI
- **Multi-cámara**: Soporte para múltiples fuentes de video
- **Flexible**: Puede conectarse a cualquier KB remoto

### **🚀 Despliegue Independiente**
- **Docker standalone**: Su propio `Dockerfile` y `docker-compose`
- **Escalable**: Múltiples instancias independientes
- **Portable**: Puede ejecutarse en cualquier infraestructura
- **Configurable**: Diferentes entornos sin conflictos

### **📡 Integración por API**
- **RESTful**: Endpoints estándar para integración
- **WebSockets**: Stream en tiempo real
- **Health checks**: Monitoreo independiente
- **Logging**: Sistema de logs propio

## 🚀 **Quick Start Independiente**

### **1. Configuración**
```bash
# Solo las variables que necesita Animal-AI Service
ANIMAL_SERVICE_PORT=8080
ANIMAL_VIDEO_SOURCE=rtsp://camera1.local/stream
ANIMAL_STORAGE_PATH=/data/animal-videos

# IA para análisis (GPT-4o Vision)
ANIMAL_LLM_PROVIDER=openai
ANIMAL_LLM_API_KEY=sk-your-key
ANIMAL_LLM_MODEL=gpt-4o

# KB de destino (puede ser cualquier KB remoto)
ANIMAL_KB_URL=http://kb-server:7070/tools/kb_ingest
ANIMAL_KB_AUTH_TOKEN=optional-auth-token
```

### **2. Ejecutar Standalone**
```bash
# Docker independiente
docker run -p 8080:8080 \
  -e ANIMAL_VIDEO_SOURCE=rtsp://camera.local \
  -e ANIMAL_LLM_API_KEY=sk-key \
  fixeatai-animal-ai:latest

# O local
cd services/animal-ai-service
python -m uvicorn main:app --port 8080
```

### **3. Verificar Independencia**
```bash
# Health check independiente
curl http://localhost:8080/health

# Iniciar análisis de video
curl -X POST "http://localhost:8080/api/v1/video/analyze" \
  -H "Content-Type: application/json" \
  -d '{"source": "rtsp://camera.local/stream"}'

# Ver movimientos detectados
curl "http://localhost:8080/api/v1/movements/recent"
```

## 📋 **Casos de Uso Independientes**

### **🏢 Escenario 1: Granja con Múltiples Cámaras**
```yaml
# docker-compose.animal-farm.yml
version: "3.9"
services:
  animal-ai-barn1:
    image: fixeatai-animal-ai:latest
    ports:
      - "8081:8080"
    environment:
      - ANIMAL_SERVICE_NAME=barn1-monitor
      - ANIMAL_VIDEO_SOURCE=rtsp://barn1-camera.local/stream
      - ANIMAL_KB_URL=http://farm-kb:7070/tools/kb_ingest
    volumes:
      - barn1-videos:/app/videos
      - barn1-models:/app/models

  animal-ai-barn2:
    image: fixeatai-animal-ai:latest
    ports:
      - "8082:8080"
    environment:
      - ANIMAL_SERVICE_NAME=barn2-monitor
      - ANIMAL_VIDEO_SOURCE=rtsp://barn2-camera.local/stream
      - ANIMAL_KB_URL=http://farm-kb:7070/tools/kb_ingest
    volumes:
      - barn2-videos:/app/videos
      - barn2-models:/app/models
```

### **🔄 Escenario 2: Laboratorio de Investigación**
```bash
# Animal-AI para estudios de comportamiento
docker run -p 8080:8080 \
  -e ANIMAL_SERVICE_NAME=research-lab \
  -e ANIMAL_SPECIES=laboratory_mice \
  -e ANIMAL_ANALYSIS_MODE=detailed \
  -e ANIMAL_RECORDING_DURATION=24h \
  fixeatai-animal-ai:latest
```

### **🌐 Escenario 3: Zoo Distribuido**
```bash
# Zona de Mamíferos
docker run -p 8080:8080 \
  -e ANIMAL_ZONE=mammals \
  -e ANIMAL_VIDEO_SOURCE=rtsp://mammals-cam.zoo.local \
  -e ANIMAL_KB_URL=http://zoo-central-kb:7070 \
  fixeatai-animal-ai:latest

# Zona de Aves
docker run -p 8081:8080 \
  -e ANIMAL_ZONE=birds \
  -e ANIMAL_VIDEO_SOURCE=rtsp://birds-cam.zoo.local \
  -e ANIMAL_KB_URL=http://zoo-central-kb:7070 \
  fixeatai-animal-ai:latest
```

## 🔧 **Variables de Entorno Completas**

### **📹 Captura de Video**
```bash
# Fuentes de video
ANIMAL_VIDEO_SOURCE=rtsp://camera.local/stream
ANIMAL_VIDEO_BACKUP_SOURCE=rtsp://backup-camera.local/stream
ANIMAL_VIDEO_RESOLUTION=1920x1080
ANIMAL_VIDEO_FPS=30
ANIMAL_VIDEO_BUFFER_SIZE=100

# Almacenamiento
ANIMAL_STORAGE_PATH=/data/animal-videos
ANIMAL_STORAGE_RETENTION_DAYS=30
ANIMAL_STORAGE_MAX_SIZE_GB=500
```

### **🤖 Inteligencia Artificial**
```bash
# Proveedor LLM
ANIMAL_LLM_PROVIDER=openai
ANIMAL_LLM_API_KEY=sk-your-openai-key
ANIMAL_LLM_MODEL=gpt-4o
ANIMAL_LLM_TEMPERATURE=0.1
ANIMAL_LLM_MAX_TOKENS=1000

# Modelos de Computer Vision
ANIMAL_YOLO_MODEL=yolov8n.pt
ANIMAL_TRACKING_MODEL=deepsort
ANIMAL_POSE_MODEL=mediapipe
ANIMAL_CONFIDENCE_THRESHOLD=0.7
```

### **📡 Knowledge Base de Destino**
```bash
# KB Remoto
ANIMAL_KB_URL=http://kb-server:7070/tools/kb_ingest
ANIMAL_KB_SEARCH_URL=http://kb-server:7070/tools/kb_search
ANIMAL_KB_AUTH_TOKEN=optional-bearer-token
ANIMAL_KB_TIMEOUT=30

# Metadatos
ANIMAL_KB_SOURCE_TYPE=animal_behavior
ANIMAL_KB_QUALITY_THRESHOLD=0.8
```

### **⚙️ Configuración del Servicio**
```bash
# Servicio
ANIMAL_SERVICE_PORT=8080
ANIMAL_SERVICE_NAME=animal-ai-production
ANIMAL_LOG_LEVEL=info

# Análisis
ANIMAL_ANALYSIS_ENABLED=true
ANIMAL_ANALYSIS_INTERVAL_SECONDS=1
ANIMAL_MOVEMENT_SENSITIVITY=medium
ANIMAL_INDIVIDUAL_TRACKING=true
ANIMAL_BEHAVIOR_LEARNING=true

# Calidad
ANIMAL_MIN_MOVEMENT_DURATION=2
ANIMAL_MAX_ANIMALS_PER_FRAME=10
ANIMAL_TRACKING_CONFIDENCE=0.8
```

### **📊 Monitoreo y Alertas**
```bash
# Logging
ANIMAL_LOG_FILE=/app/logs/animal-ai.log
ANIMAL_LOG_ROTATION=daily
ANIMAL_LOG_RETENTION_DAYS=30

# Métricas
ANIMAL_METRICS_ENABLED=true
ANIMAL_METRICS_PORT=8081
ANIMAL_PROMETHEUS_ENDPOINT=/metrics

# Alertas
ANIMAL_ALERT_WEBHOOK=https://hooks.slack.com/your-webhook
ANIMAL_ALERT_EMAIL=admin@farm.com
ANIMAL_ALERT_ON_UNUSUAL_BEHAVIOR=true
ANIMAL_ALERT_ON_SYSTEM_ERROR=true
```

### **🔐 Seguridad**
```bash
# Autenticación
ANIMAL_API_KEY=your-api-key-for-animal-endpoints
ANIMAL_CORS_ORIGINS=http://localhost:3000,https://admin.farm.com

# Privacidad
ANIMAL_ANONYMIZE_DATA=false
ANIMAL_ENCRYPT_VIDEOS=true
ANIMAL_ENCRYPTION_KEY=your-32-char-encryption-key
```

## 🌟 **Ventajas de la Independencia**

### **🚀 Escalabilidad**
- **Horizontal**: Múltiples instancias Animal-AI
- **Vertical**: Recursos dedicados por cámara/zona
- **Geográfica**: Animal-AI distribuido por ubicaciones

### **🔧 Mantenimiento**
- **Actualizaciones**: Sin afectar otros servicios
- **Debugging**: Logs y métricas independientes
- **Testing**: Entorno aislado de pruebas

### **🏢 Organizacional**
- **Equipos**: Diferentes equipos pueden gestionar diferentes zonas
- **Responsabilidades**: Ownership claro por área/especie
- **Presupuesto**: Costos separados por instalación

### **🔒 Seguridad**
- **Aislamiento**: Falla de un Animal-AI no afecta otros
- **Permisos**: Acceso granular por zona/cámara
- **Auditoria**: Logs independientes por instalación

## 📚 **Documentación Adicional**

- [Instalación y Configuración](./docs/installation.md)
- [API Reference](./docs/api-reference.md)
- [Computer Vision Models](./docs/cv-models.md)
- [Behavior Classification](./docs/behavior-classification.md)
- [Admin Interface Guide](./docs/admin-interface.md)
- [Integration Examples](./docs/integration-examples.md)
- [Troubleshooting](./docs/troubleshooting.md)

**¡Animal-AI Service: Completamente independiente, altamente inteligente!** 🐾🤖

