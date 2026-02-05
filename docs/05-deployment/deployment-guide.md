# 🚀 Guía de Deployment - FixeatAI

**Servidor Productivo:** `ec2-18-220-79-28.us-east-2.compute.amazonaws.com`  
**IP:** `18.220.79.28`  
**Usuario:** `ec2-user`  
**Clave PEM:** `fixeatIA.pem` (en raíz del proyecto)

---

## 📋 Tabla de Contenidos

1. [Pre-requisitos](#pre-requisitos)
2. [Deployment Inicial](#deployment-inicial)
3. [Actualización de Código](#actualización-de-código)
4. [Monitoreo](#monitoreo)
5. [Rollback](#rollback)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Pre-requisitos

### En tu máquina local:
- ✅ Acceso a `fixeatIA.pem`
- ✅ SSH configurado
- ✅ Git con cambios commiteados

### En el servidor EC2:
- ✅ Docker y Docker Compose instalados
- ✅ Repositorio clonado en `/home/ec2-user/fixeatAI`
- ✅ Archivo `.env` configurado

---

## 🚀 Deployment Inicial

### 1. Conectarse al servidor

```bash
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI
```

### 2. Configurar variables de entorno

```bash
# Crear .env si no existe
cp .env.example .env

# Editar con tus valores
nano .env
```

**Variables críticas:**
```bash
OPENAI_API_KEY=sk-proj-...
USE_LLM=true
LLM_MODEL=gpt-4o-mini
CORS_ALLOW_ORIGINS=*
MYSQL_HOST=your-rds-endpoint
MYSQL_DATABASE=requisicion_db
```

### 3. Build y levantar servicios

```bash
# Build de imágenes (primera vez o después de cambios)
docker-compose build --no-cache

# Levantar todos los servicios
docker-compose up -d

# Verificar que estén corriendo
docker-compose ps
```

**Servicios esperados:**
```
fixeatai-api-1         ✅ UP (puerto 8000)
fixeatai-mcp-1         ✅ UP (puerto 7070)
fixeatai-etl-service   ✅ UP (puerto 9000)
```

### 4. Health checks

```bash
# API
curl http://localhost:8000/health

# MCP
curl http://localhost:7070/health

# Desde tu máquina local
curl http://18.220.79.28:8000/health
curl http://18.220.79.28:7070/health
```

---

## 🔄 Actualización de Código

### Proceso Completo (Recomendado)

```bash
# 1. Conectarse al servidor
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI

# 2. Backup del .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 3. Pull de cambios desde GitHub
git pull origin main

# 4. Rebuild de servicios modificados
docker-compose build --no-cache api mcp

# 5. Restart de servicios
docker-compose restart api mcp

# 6. Verificar logs
docker-compose logs -f --tail=100 api mcp
```

### Proceso Rápido (Solo código Python)

Si solo cambiaste código Python sin cambios en dependencias:

```bash
# Restart sin rebuild (más rápido)
docker-compose restart api mcp
```

### Actualización con Cambios de Dependencias

Si modificaste `pyproject.toml`:

```bash
# Rebuild completo necesario
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Monitoreo

### Ver logs en tiempo real

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f api
docker-compose logs -f mcp

# Últimas 100 líneas
docker-compose logs --tail=100 api
```

### Desde tu máquina local

```bash
# Ver logs del API
ssh -i fixeatIA.pem ec2-user@18.220.79.28 \
  "cd fixeatAI && docker-compose logs --tail=100 api"

# Ver estado de servicios
ssh -i fixeatIA.pem ec2-user@18.220.79.28 \
  "cd fixeatAI && docker-compose ps"
```

### Monitoreo de recursos

```bash
# Uso de CPU/RAM por contenedor
docker stats

# Espacio en disco
df -h

# Logs de Docker
docker system df
```

---

## 🔙 Rollback

### Rollback de código

```bash
# 1. Ver commits recientes
git log --oneline -10

# 2. Volver al commit anterior
git reset --hard HEAD~1

# 3. Rebuild y restart
docker-compose build --no-cache
docker-compose restart api mcp
```

### Rollback de configuración

```bash
# Restaurar .env anterior
ls -la .env.backup.*  # Ver backups disponibles
cp .env.backup.YYYYMMDD_HHMMSS .env

# Restart servicios
docker-compose restart
```

### Rollback de imágenes Docker

```bash
# Ver imágenes disponibles
docker images | grep fixeatai

# Usar una imagen anterior (si existe)
docker tag fixeatai:old fixeatai:latest
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Problema: Servicios no arrancan

**Síntoma:**
```bash
docker-compose ps
# Muestra servicios en estado "Exit 1" o "Restarting"
```

**Solución:**
```bash
# Ver logs de error
docker-compose logs api
docker-compose logs mcp

# Verificar .env
cat .env | grep -v "^#" | grep -v "^$"

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

### Problema: KB no responde o `kb_hits: 0`

**Síntoma:**
```json
{
  "signals": {
    "kb_hits": 0,
    "llm_used": true
  }
}
```

**Solución:**
```bash
# 1. Verificar que MCP esté corriendo
curl http://localhost:7070/health

# 2. Verificar ChromaDB
docker exec fixeatai-mcp-1 ls -la /data/chroma/

# 3. Verificar ingesta
docker exec fixeatai-mcp-1 python -c "
from services.kb.demo_kb import get_all_documents
docs = get_all_documents()
print(f'Documentos en KB: {len(docs)}')
"

# 4. Re-ingestar si es necesario
# (Ver guía de ingesta)
```

---

### Problema: Dependencias faltantes

**Síntoma:**
```
ModuleNotFoundError: No module named 'pypdf'
```

**Solución:**
```bash
# Instalar en el contenedor corriendo
docker exec fixeatai-mcp-1 pip install pypdf pdfminer.six python-docx openpyxl

# O rebuild con dependencias actualizadas
# (actualizar pyproject.toml primero)
docker-compose build --no-cache mcp
docker-compose restart mcp
```

---

### Problema: Out of Memory

**Síntoma:**
```
docker stats
# Muestra >90% uso de memoria
```

**Solución:**
```bash
# 1. Ver qué consume más
docker stats --no-stream

# 2. Limpiar recursos no usados
docker system prune -a --volumes

# 3. Reiniciar servicios
docker-compose restart

# 4. Si persiste, aumentar RAM de EC2
# (desde AWS Console)
```

---

### Problema: Puerto en uso

**Síntoma:**
```
Error: bind: address already in use
```

**Solución:**
```bash
# Ver qué usa el puerto
sudo lsof -i :8000
sudo lsof -i :7070

# Matar proceso si es necesario
sudo kill -9 <PID>

# O cambiar puerto en docker-compose.yml
```

---

## 📈 Optimizaciones de Producción

### 1. Limpieza periódica

```bash
# Agregar a crontab
crontab -e

# Limpiar cada semana
0 2 * * 0 cd /home/ec2-user/fixeatAI && docker system prune -f
```

### 2. Logs rotation

```bash
# Configurar en docker-compose.yml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. Health check automático

```bash
# Script de monitoreo (save as monitor.sh)
#!/bin/bash
if ! curl -s http://localhost:8000/health | grep -q "ok"; then
  echo "API down, restarting..."
  cd /home/ec2-user/fixeatAI && docker-compose restart api
fi

# Agregar a crontab (cada 5 minutos)
*/5 * * * * /home/ec2-user/monitor.sh
```

---

## ✅ Checklist de Deployment

Antes de hacer deployment:

- [ ] Cambios commiteados y pusheados a GitHub
- [ ] Tests locales pasando
- [ ] Backup de `.env` creado
- [ ] Servicios actuales funcionando correctamente
- [ ] Horario de bajo tráfico (si es crítico)

Durante deployment:

- [ ] Pull de código exitoso
- [ ] Build sin errores
- [ ] Servicios levantados correctamente
- [ ] Health checks OK
- [ ] Logs sin errores críticos

Después de deployment:

- [ ] Prueba de endpoint predict-fallas
- [ ] Verificar KB hits > 0
- [ ] Monitorear logs por 10-15 minutos
- [ ] Notificar al equipo si es deployment mayor

---

## 📞 Contacto de Emergencia

Si algo falla crítico en producción:

1. **Rollback inmediato** (ver sección arriba)
2. **Verificar logs** y guardar para análisis
3. **Notificar** al equipo técnico
4. **Documentar** el incidente

---

**Última actualización:** 2 de febrero de 2026  
**Mantenedor:** Equipo FixeatAI  
**Servidor:** AWS EC2 (us-east-2)
