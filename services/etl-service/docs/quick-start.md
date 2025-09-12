# 🚀 ETL Service - Quick Start

## ⚡ Inicio Rápido (5 minutos)

### **1. Clonar y Configurar**

```bash
# Ir al directorio del ETL Service
cd services/etl-service

# Copiar configuración de ejemplo
cp env.example .env

# Editar configuración mínima
nano .env
```

**Configuración mínima requerida:**
```bash
# BD Principal
ETL_DB_HOST=tu-mysql-server.com
ETL_DB_USER=readonly_user
ETL_DB_PASSWORD=tu_password
ETL_DB_DATABASE=tu_database

# LLM para análisis
ETL_LLM_API_KEY=sk-tu-openai-key

# KB de destino (opcional: puede usar local)
ETL_KB_URL=http://tu-kb-server:7070/tools/kb_ingest
```

### **2. Ejecutar con Docker (Recomendado)**

```bash
# Construir y ejecutar
docker-compose up -d

# Verificar estado
curl http://localhost:9000/health
```

### **3. Ejecutar Local (Desarrollo)**

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servicio
python main.py
```

### **4. Primeros Pasos**

```bash
# 1. Descubrir esquema de BD
curl -X POST "http://localhost:9000/api/v1/discover-schema" | jq .

# 2. Ver análisis
curl "http://localhost:9000/api/v1/status" | jq .

# 3. Generar configuración automática
curl -X POST "http://localhost:9000/api/v1/generate-config" \
  -d '{"databases": ["default"]}' | jq .

# 4. Ejecutar ETL
curl -X POST "http://localhost:9000/api/v1/etl/sync" \
  -d '{"sync_type": "incremental"}' | jq .
```

## 🔧 **Configuraciones por Escenario**

### **📊 Escenario 1: BD Única + OpenAI + KB Remoto**

```bash
# .env
ETL_SERVICE_NAME=etl-production
ETL_SERVICE_PORT=9000

ETL_DB_HOST=mysql.prod.com
ETL_DB_USER=readonly
ETL_DB_PASSWORD=secure_pass
ETL_DB_DATABASE=production_db

ETL_LLM_PROVIDER=openai
ETL_LLM_API_KEY=sk-your-key
ETL_LLM_MODEL=gpt-4o-mini

ETL_KB_URL=http://kb-server:7070/tools/kb_ingest
```

### **🏢 Escenario 2: Múltiples BDs + LLM Local**

```bash
# .env
ETL_SERVICE_NAME=etl-multi-db

# BD Principal
ETL_DB_HOST=main-mysql.com
ETL_DB_DATABASE=main_db
ETL_DB_USER=readonly_main
ETL_DB_PASSWORD=main_pass

# BD Inventarios
ETL_DB_INVENTORY_HOST=inv-mysql.com
ETL_DB_INVENTORY_DATABASE=inventory_db
ETL_DB_INVENTORY_USER=readonly_inv
ETL_DB_INVENTORY_PASSWORD=inv_pass

# LLM Local (Ollama)
ETL_LLM_PROVIDER=ollama
ETL_LLM_BASE_URL=http://ollama-server:11434/v1
ETL_LLM_MODEL=llama3.1:8b

# KB Local
ETL_KB_LOCAL_PATH=/data/chroma_etl
```

### **☁️ Escenario 3: Cloud + Alta Disponibilidad**

```bash
# .env
ETL_SERVICE_NAME=etl-cloud-ha
ETL_SERVICE_PORT=9000

# BD Cloud
ETL_DB_HOST=rds.amazonaws.com
ETL_DB_SSL=true
ETL_DB_TIMEOUT=60

# LLM Cloud
ETL_LLM_PROVIDER=azure
ETL_LLM_API_KEY=azure-key
ETL_LLM_BASE_URL=https://your-azure-openai.com

# Monitoreo
ETL_METRICS_ENABLED=true
ETL_ALERT_WEBHOOK=https://hooks.slack.com/your-webhook
ETL_ALERT_EMAIL=ops@company.com
```

## 🐳 **Docker Compose por Escenario**

### **📦 Standalone Completo**

```yaml
# docker-compose.standalone.yml
version: "3.9"
services:
  etl-service:
    image: fixeatai-etl:latest
    ports:
      - "9000:9000"
    env_file: .env
    volumes:
      - etl-data:/app/data
      - etl-logs:/app/logs
    restart: unless-stopped

volumes:
  etl-data:
  etl-logs:
```

### **🔧 Desarrollo con BD Local**

```bash
# Ejecutar con BD y LLM local
docker-compose --profile dev up -d
```

### **🌐 Producción Multi-Región**

```yaml
# docker-compose.prod.yml
version: "3.9"
services:
  etl-service:
    image: fixeatai-etl:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    env_file: .env
    environment:
      - ETL_REGION=us-east-1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔍 **Verificación de Funcionamiento**

### **✅ Health Checks**

```bash
# Estado general
curl "http://localhost:9000/health" | jq .

# Estado detallado
curl "http://localhost:9000/status" | jq .

# Métricas
curl "http://localhost:9000/api/v1/metrics" | jq .
```

### **🧪 Testing Básico**

```bash
# Test conexión BD
curl -X POST "http://localhost:9000/api/v1/admin/test-connection" \
  -d '{"database": "default"}' | jq .

# Test configuración LLM
curl "http://localhost:9000/api/v1/llm/test" | jq .

# Test pipeline completo (dry run)
curl -X POST "http://localhost:9000/api/v1/etl/sync" \
  -d '{"dry_run": true, "tables": ["small_table"]}' | jq .
```

## 📊 **Monitoreo Inicial**

### **📈 Dashboard URLs**

```bash
# UI Principal
http://localhost:9000/docs

# Métricas Prometheus (si habilitado)
http://localhost:9001/metrics

# Logs en tiempo real
docker logs -f etl-service
```

### **📋 Comandos de Administración**

```bash
# Ver jobs activos
curl "http://localhost:9000/api/v1/jobs" | jq .

# Pausar ETL
curl -X POST "http://localhost:9000/api/v1/admin/pause"

# Reanudar ETL
curl -X POST "http://localhost:9000/api/v1/admin/resume"

# Limpiar jobs completados
curl -X POST "http://localhost:9000/api/v1/admin/clear-jobs"
```

## 🚨 **Troubleshooting Rápido**

### **❌ Error: Connection refused**

```bash
# Verificar puerto
netstat -tlnp | grep 9000

# Verificar logs
docker logs etl-service

# Verificar configuración
curl "http://localhost:9000/api/v1/config" | jq .
```

### **❌ Error: BD no conecta**

```bash
# Test manual de conexión
mysql -h $ETL_DB_HOST -u $ETL_DB_USER -p$ETL_DB_PASSWORD $ETL_DB_DATABASE

# Ver logs específicos
docker logs etl-service | grep -i mysql

# Test desde contenedor
docker exec etl-service curl "http://localhost:9000/api/v1/admin/test-connection"
```

### **❌ Error: LLM timeout**

```bash
# Verificar API key
echo $ETL_LLM_API_KEY

# Test manual
curl -H "Authorization: Bearer $ETL_LLM_API_KEY" \
  https://api.openai.com/v1/models

# Ajustar timeout
ETL_LLM_TIMEOUT=60
```

## 🎯 **Próximos Pasos**

### **🔧 Configuración Avanzada**

1. **Múltiples BDs**: Agregar `ETL_DB_NOMBRE_HOST` variables
2. **Scheduling**: Configurar `ETL_INCREMENTAL_HOURS` y `ETL_FULL_SYNC_TIME`  
3. **Alertas**: Configurar `ETL_ALERT_WEBHOOK` y `ETL_ALERT_EMAIL`
4. **Métricas**: Habilitar `ETL_METRICS_ENABLED=true`

### **📊 Optimización**

1. **Batch Size**: Ajustar `ETL_BATCH_SIZE` según recursos
2. **Calidad**: Configurar `ETL_QUALITY_THRESHOLD`
3. **Performance**: Monitorear métricas y ajustar recursos Docker

### **🔒 Seguridad**

1. **API Keys**: Usar secretos de AWS/Azure en producción
2. **Encriptación**: Habilitar `ETL_ENCRYPT_SENSITIVE_DATA=true`
3. **CORS**: Configurar `ETL_CORS_ORIGINS` restrictivamente

**¡ETL Service está listo para funcionar independientemente!** 🚀

Para configuraciones más avanzadas, consulta la [documentación completa](./README.md).
