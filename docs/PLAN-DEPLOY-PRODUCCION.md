# 🚀 Plan de Deployment a Producción - FixeatAI

**Fecha:** 26 de Enero, 2026  
**Estado:** Pendiente de datos de máquina

---

## 📋 **Checklist de Deployment**

### **Fase 1: Preparación (Local)** ✅
- [x] Sistema funcional en local
- [x] 67 PDFs ingresados en ChromaDB
- [x] Búsqueda híbrida implementada
- [x] Scoring de relevancia sin alucinaciones
- [x] API con 6 endpoints funcionales
- [x] Frontend de pruebas
- [x] Documentación completa

### **Fase 2: Configuración de Infraestructura** ⏳
- [ ] Obtener datos de instancia EC2
- [ ] Configurar Security Groups (puertos 22, 8080, 7070, 9000)
- [ ] Configurar EBS para persistencia (50 GB mínimo)
- [ ] Configurar Elastic IP (opcional pero recomendado)
- [ ] Configurar IAM Role para S3 (backups)

### **Fase 3: Preparación de Archivos** ⏳
- [ ] Crear `.env` de producción con credenciales reales
- [ ] Configurar docker-compose.prod.yml
- [ ] Preparar backup de ChromaDB local (67 PDFs)
- [ ] Comprimir código para subir a EC2

### **Fase 4: Instalación en Servidor** ⏳
- [ ] Conectar a EC2 via SSH
- [ ] Instalar Docker y Docker Compose
- [ ] Crear directorios de persistencia
- [ ] Subir código y configuración
- [ ] Subir backup de ChromaDB

### **Fase 5: Configuración de Servicios** ⏳
- [ ] Configurar variables de entorno
- [ ] Configurar volúmenes Docker
- [ ] Configurar reinicio automático
- [ ] Configurar logs persistentes

### **Fase 6: Deploy y Verificación** ⏳
- [ ] Build de imágenes Docker
- [ ] Levantar servicios
- [ ] Health checks de API, MCP, ETL
- [ ] Verificar conectividad a RDS
- [ ] Verificar persistencia de ChromaDB
- [ ] Probar búsqueda en KB
- [ ] Probar endpoints de API

### **Fase 7: Configuración de Backups** ⏳
- [ ] Script de backup de ChromaDB a S3
- [ ] Cron job para backups diarios
- [ ] Verificar backup exitoso
- [ ] Documentar proceso de restore

### **Fase 8: Monitoreo y Alertas** ⏳
- [ ] Configurar logs centralizados
- [ ] Configurar métricas (Prometheus opcional)
- [ ] Configurar alertas de salud
- [ ] Documentar URLs de acceso

---

## 🔧 **Configuración Específica**

### **1. Variables de Entorno de Producción**

Crear `/srv/fixeatAI/.env`:

```bash
# =================================================================
# CONFIGURACIÓN LLM
# =================================================================
OPENAI_API_KEY=sk-proj-XXXXX  # ⚠️ COMPLETAR
LLM_MODEL=gpt-4o-mini
USE_LLM=true

# =================================================================
# CONFIGURACIÓN MCP
# =================================================================
MCP_SERVER_URL=http://mcp:7000
CHROMA_PATH=/app/chroma_data

# =================================================================
# CONFIGURACIÓN API
# =================================================================
API_PORT=8080  # Cambiado de 8000 para evitar conflictos
CORS_ORIGINS=*  # ⚠️ Cambiar en producción a dominio específico

# =================================================================
# CONFIGURACIÓN ETL (Si se usa)
# =================================================================
ETL_DB_HOST=db-dev-requisition.cluster-cwrwuyokixuk.us-east-1.rds.amazonaws.com
ETL_DB_PORT=3306
ETL_DB_USER=admin
ETL_DB_PASSWORD=gXT5a1R2TWtDfR1p7Iwv  # ⚠️ Ya configurado
ETL_DB_DATABASE=requisicion_db
ETL_DB_SSL=true

# =================================================================
# CONFIGURACIÓN S3 (Backups)
# =================================================================
S3_BUCKET=desa-aibo-wp  # ⚠️ Ya existe
S3_REGION=us-east-1
S3_KB_PREFIX=fixeatAI/kb_backups

# =================================================================
# CONFIGURACIÓN DE LOGS
# =================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

### **2. Docker Compose para Producción**

Crear `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mcp:
    image: fixeatai:latest
    container_name: fixeatai-mcp-prod
    command: >
      sh -c "if [ \"$$SERVICE_TYPE\" = 'mcp' ]; then
               uvicorn mcp.server_demo:app --host 0.0.0.0 --port 7000;
             fi"
    environment:
      - SERVICE_TYPE=mcp
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LLM_MODEL=${LLM_MODEL:-gpt-4o-mini}
      - CHROMA_PATH=/app/chroma_data
    volumes:
      - /srv/fixeatAI/chroma_data:/app/chroma_data:rw
      - /srv/fixeatAI/logs:/app/logs:rw
    ports:
      - "7070:7000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - fixeatai-network

  api:
    image: fixeatai:latest
    container_name: fixeatai-api-prod
    command: >
      sh -c "if [ \"$$SERVICE_TYPE\" = 'api' ]; then
               uvicorn app.main:app --host 0.0.0.0 --port 8000;
             fi"
    environment:
      - SERVICE_TYPE=api
      - MCP_SERVER_URL=http://mcp:7000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - USE_LLM=${USE_LLM:-true}
      - CORS_ORIGINS=${CORS_ORIGINS:-*}
    ports:
      - "8080:8000"  # Externo:Interno
    depends_on:
      - mcp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - fixeatai-network

  etl-service:
    image: fixeatai-etl:latest
    container_name: fixeatai-etl-prod
    environment:
      - ETL_DB_HOST=${ETL_DB_HOST}
      - ETL_DB_PORT=${ETL_DB_PORT}
      - ETL_DB_USER=${ETL_DB_USER}
      - ETL_DB_PASSWORD=${ETL_DB_PASSWORD}
      - ETL_DB_DATABASE=${ETL_DB_DATABASE}
      - ETL_DB_SSL=${ETL_DB_SSL:-true}
      - ETL_LLM_PROVIDER=${ETL_LLM_PROVIDER:-openai}
      - ETL_LLM_API_KEY=${OPENAI_API_KEY}
      - ETL_LLM_MODEL=${LLM_MODEL:-gpt-4o-mini}
    ports:
      - "9000:9000"
    volumes:
      - /srv/fixeatAI/etl_logs:/app/logs:rw
      - /srv/fixeatAI/etl_configs:/app/configs:rw
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - fixeatai-network

networks:
  fixeatai-network:
    driver: bridge

volumes:
  chroma_data:
  etl_logs:
  etl_configs:
```

---

### **3. Script de Backup a S3**

Crear `/usr/local/bin/fixeatai-backup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Configuración
DATA_DIR="/srv/fixeatAI/chroma_data"
S3_BUCKET="desa-aibo-wp"
S3_PREFIX="fixeatAI/kb_backups"
STAMP=$(date +%Y%m%d_%H%M%S)
TMP_DIR="/tmp"
BACKUP_FILE="${TMP_DIR}/kb_backup_${STAMP}.tar.gz"
LOG_FILE="/var/log/fixeatai-backup.log"

# Función de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 Iniciando backup de ChromaDB..."

# Crear backup
log "📦 Comprimiendo datos de ChromaDB..."
tar -czf "$BACKUP_FILE" -C "$DATA_DIR" . 2>&1 | tee -a "$LOG_FILE"

# Verificar tamaño
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "📊 Tamaño del backup: $BACKUP_SIZE"

# Subir a S3
log "☁️  Subiendo a S3..."
aws s3 cp "$BACKUP_FILE" "s3://${S3_BUCKET}/${S3_PREFIX}/kb_backup_${STAMP}.tar.gz" \
    --region us-east-1 2>&1 | tee -a "$LOG_FILE"

# Verificar upload
if [ $? -eq 0 ]; then
    log "✅ Backup completado exitosamente: kb_backup_${STAMP}.tar.gz"
else
    log "❌ Error al subir backup a S3"
    exit 1
fi

# Limpiar backups locales antiguos (más de 3 días)
log "🧹 Limpiando backups locales antiguos..."
find "$TMP_DIR" -maxdepth 1 -name 'kb_backup_*.tar.gz' -mtime +3 -delete

# Limpiar backups en S3 antiguos (más de 30 días) - OPCIONAL
# aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" | \
#     while read -r line; do
#         createDate=$(echo $line | awk '{print $1" "$2}')
#         createDate=$(date -d"$createDate" +%s)
#         olderThan=$(date -d"-30 days" +%s)
#         if [[ $createDate -lt $olderThan ]]; then
#             fileName=$(echo $line | awk '{print $4}')
#             aws s3 rm "s3://${S3_BUCKET}/${S3_PREFIX}/${fileName}"
#             log "🗑️  Eliminado backup antiguo: $fileName"
#         fi
#     done

log "✅ Proceso de backup finalizado"
```

**Hacer ejecutable y configurar cron:**
```bash
sudo chmod +x /usr/local/bin/fixeatai-backup.sh

# Backup diario a las 3 AM
echo "0 3 * * * /usr/local/bin/fixeatai-backup.sh" | sudo tee /etc/cron.d/fixeatai-backup
```

---

### **4. Script de Restore desde S3**

Crear `/usr/local/bin/fixeatai-restore.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

S3_BUCKET="desa-aibo-wp"
S3_PREFIX="fixeatAI/kb_backups"
DATA_DIR="/srv/fixeatAI/chroma_data"
TMP_DIR="/tmp"

# Listar backups disponibles
echo "📋 Backups disponibles en S3:"
aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --region us-east-1

# Obtener el más reciente
LATEST=$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --region us-east-1 | \
         sort | tail -1 | awk '{print $4}')

echo ""
echo "🔄 Último backup: $LATEST"
read -p "¿Deseas restaurar este backup? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelado"
    exit 1
fi

# Descargar backup
echo "⬇️  Descargando backup desde S3..."
aws s3 cp "s3://${S3_BUCKET}/${S3_PREFIX}/${LATEST}" \
          "${TMP_DIR}/${LATEST}" --region us-east-1

# Detener servicios
echo "🛑 Deteniendo servicios..."
cd /srv/fixeatAI
sudo docker-compose -f docker-compose.prod.yml stop mcp

# Limpiar datos actuales
echo "🗑️  Limpiando datos actuales..."
sudo rm -rf ${DATA_DIR}/*

# Restaurar backup
echo "📦 Extrayendo backup..."
sudo tar -xzf "${TMP_DIR}/${LATEST}" -C "$DATA_DIR"

# Ajustar permisos
sudo chown -R 1000:1000 "$DATA_DIR"

# Reiniciar servicios
echo "🚀 Reiniciando servicios..."
sudo docker-compose -f docker-compose.prod.yml start mcp

# Verificar
sleep 5
curl -f http://localhost:7070/health && echo "✅ MCP Service restaurado correctamente"

# Limpiar
rm "${TMP_DIR}/${LATEST}"
echo "✅ Restore completado exitosamente"
```

---

## 📊 **Comandos de Gestión en Producción**

```bash
# Conectar a la instancia
ssh -i tu-key.pem ubuntu@TU-EC2-IP

# Ver servicios
cd /srv/fixeatAI
sudo docker-compose -f docker-compose.prod.yml ps

# Ver logs
sudo docker-compose -f docker-compose.prod.yml logs -f api
sudo docker-compose -f docker-compose.prod.yml logs -f mcp
sudo docker-compose -f docker-compose.prod.yml logs -f etl-service

# Reiniciar servicios
sudo docker-compose -f docker-compose.prod.yml restart

# Actualizar código
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml build --no-cache
sudo docker-compose -f docker-compose.prod.yml --env-file .env up -d

# Verificar salud
curl http://localhost:8080/health  # API
curl http://localhost:7070/health  # MCP
curl http://localhost:9000/health  # ETL

# Ver uso de recursos
docker stats

# Ver espacio en disco
df -h
```

---

## 🔍 **URLs de Acceso Post-Deploy**

Una vez desplegado, el sistema estará disponible en:

```
✅ API Principal:    http://TU-EC2-IP:8080
✅ Documentación:    http://TU-EC2-IP:8080/docs
✅ Health Check:     http://TU-EC2-IP:8080/health

✅ MCP Server:       http://TU-EC2-IP:7070
✅ MCP Health:       http://TU-EC2-IP:7070/health

✅ ETL Service:      http://TU-EC2-IP:9000
✅ ETL Docs:         http://TU-EC2-IP:9000/docs
```

---

## ⚠️ **Consideraciones de Seguridad para Producción**

### **1. Cambiar CORS:**
```python
# app/main.py
CORS_ORIGINS = "https://tu-dominio.com"  # No usar "*" en producción
```

### **2. Configurar HTTPS:**
- Usar ALB (Application Load Balancer) con certificado SSL
- O configurar nginx como reverse proxy con Let's Encrypt

### **3. Restringir Security Groups:**
```
❌ NO permitir 0.0.0.0/0 en puertos 7070, 9000
✅ Permitir solo VPC interna o IPs específicas
✅ API (8080) detrás de ALB con HTTPS
```

### **4. Usar Secrets Manager:**
```bash
# En lugar de .env con API keys en texto plano:
aws secretsmanager create-secret \
    --name fixeatai/openai-key \
    --secret-string "sk-proj-XXXXX"

# Modificar docker-compose para leer de Secrets Manager
```

---

## ✅ **Próximos Pasos Inmediatos**

1. **Proveer datos de instancia EC2:**
   - IP pública o DNS
   - SSH key (.pem)
   - Usuario (ubuntu / ec2-user)

2. **Confirmar credenciales:**
   - OpenAI API Key
   - AWS Access Key (para S3)

3. **Ejecutar deployment**

---

**Estado:** ⏳ Esperando datos de infraestructura  
**Tiempo estimado de deploy:** 30-45 minutos una vez tengamos los datos
