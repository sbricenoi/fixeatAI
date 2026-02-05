# 🚀 Deployment Documentation - FIXEAT AI

Documentación de deployment y operaciones en producción.

---

## 📚 Documentos Disponibles

### ⭐ [Deployment Guide](./deployment-guide.md) - **EMPEZAR AQUÍ**
Guía maestra completa de deployment.

**Incluye:**
- Pre-requisitos
- Deployment inicial
- Actualización de código
- Monitoreo
- Rollback
- Troubleshooting completo
- Checklist de deployment

**Servidor productivo:**
- IP: `18.220.79.28`
- Usuario: `ec2-user`
- Clave: `fixeatIA.pem`

---

### [Deploy AWS](./deploy-aws.md)
Configuración específica de AWS EC2.

**Incluye:**
- Configuración de EC2
- Security groups
- Elastic IP
- RDS configuration
- S3 para KB

---

### [Deploy CI/CD](./deploy-ci-cd.md)
Pipeline de integración y deployment continuo.

**Incluye:**
- GitHub Actions
- Automated testing
- Automated deployment
- Rollback automático

---

### [Runbooks](./runbooks.md)
Procedimientos operativos estándar.

**Incluye:**
- Procedimientos de emergencia
- Restart de servicios
- Backup y restore
- Escalado

---

### [Observabilidad](./observabilidad.md)
Monitoreo, logs y alertas.

**Incluye:**
- Configuración de logs
- Métricas importantes
- Alertas
- Dashboards

---

### [Seguridad](./seguridad.md)
Políticas y prácticas de seguridad.

**Incluye:**
- Gestión de secretos
- Acceso SSH
- Firewall rules
- Best practices

---

## 🎯 Quick Commands

### Conectar al servidor

```bash
ssh -i fixeatIA.pem ec2-user@18.220.79.28
```

### Ver estado de servicios

```bash
cd fixeatAI
docker-compose ps
```

### Ver logs

```bash
docker-compose logs -f --tail=100 api mcp
```

### Actualizar código

```bash
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

### Health checks

```bash
curl http://localhost:8000/health
curl http://localhost:7070/health
```

---

## 🚨 Emergencias

### Sistema caído

```bash
# 1. Verificar logs
docker-compose logs --tail=200 api mcp

# 2. Restart servicios
docker-compose restart

# 3. Si persiste, rebuild
docker-compose down
docker-compose up -d --build
```

### KB sin respuesta

```bash
# Verificar MCP
docker-compose logs mcp

# Restart MCP
docker-compose restart mcp

# Verificar ChromaDB
docker exec fixeatai-mcp-1 ls -la /data/chroma/
```

---

## 📊 Estado Actual

| Servicio | Estado | Puerto | URL |
|----------|--------|--------|-----|
| API | ✅ UP | 8000 | http://18.220.79.28:8000 |
| MCP | ✅ UP | 7070 | http://18.220.79.28:7070 |
| ETL | ✅ UP | 9000 | http://18.220.79.28:9000 |

**Última verificación:** 2 de febrero de 2026

---

[← Volver al índice principal](../README.md)
