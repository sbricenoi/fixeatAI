# 🚀 Guía de Integración - ETL Service al Proyecto Principal

## ✅ **¡ETL Service Integrado al Proyecto Principal!**

El ETL Service ahora está completamente integrado al proyecto FixeatAI y puede ejecutarse junto con los servicios existentes **sin afectar nada**.

## 📊 **Arquitectura de Servicios**

```
Proyecto FixeatAI
├── 🔌 API Service     → Puerto 8000
├── 🔧 MCP Service     → Puerto 7070  
└── ⚙️ ETL Service     → Puerto 9000 (NUEVO)
```

**✅ Sin conflictos de puertos**
**✅ Comparte variables de entorno**
**✅ Reutiliza conexión a BD**
**✅ Integrado al Makefile**

## 🔧 **Configuración Necesaria**

### **1. Agregar Variables al .env Principal**

Agrega estas líneas al archivo `.env` principal:

```bash
# ETL SERVICE - Variables específicas
ETL_DB_HOST=db-dev-requisition.cluster-cwrwuyokixuk.us-east-1.rds.amazonaws.com
ETL_DB_PORT=3306
ETL_DB_USER=admin
ETL_DB_PASSWORD=gXT5a1R2TWtDfR1p7Iwv
ETL_DB_DATABASE=requisicion_db
ETL_DB_SSL=true

# Configuración ETL
ETL_BATCH_SIZE=500
ETL_QUALITY_THRESHOLD=0.7
ETL_INCREMENTAL_HOURS=6
ETL_FULL_SYNC_TIME=02:00
```

*(Las credenciales ya están correctas basadas en tu BD real)*

### **2. Verificar Documentación de BD**

La documentación rica ya está en:
```
services/etl-service/docs/database/requisicion_db_documentation.json
```

## 🚀 **Comandos de Ejecución**

### **Opción 1: Solo ETL Service**
```bash
make etl
# O directamente:
docker-compose up etl-service --build
```

### **Opción 2: Todos los Servicios**
```bash
make all
# O directamente:
docker-compose up --build
```

### **Opción 3: Servicios Existentes + ETL**
```bash
# Iniciar servicios existentes
docker-compose up api mcp --build

# En otra terminal, agregar ETL
docker-compose up etl-service --build
```

## 📋 **Verificación Post-Integración**

### **1. Health Checks**
```bash
# Verificar todos los servicios
make health

# O individualmente:
curl http://localhost:8000/health  # API principal
curl http://localhost:7070/health  # MCP Service
curl http://localhost:9000/health  # ETL Service (nuevo)
```

### **2. Test del ETL Service**
```bash
# Info del ETL Service
curl http://localhost:9000/api/v1/info

# Validar documentación BD
curl http://localhost:9000/api/v1/validate-documentation/requisicion_db

# Test de conexión BD real
curl -X POST "http://localhost:9000/api/v1/discover-schema" \
  -H "Content-Type: application/json" \
  -d '{"databases": ["default"]}'
```

### **3. Ver Logs**
```bash
# Todos los servicios
make logs

# Solo ETL Service
make logs-etl
```

## 🔄 **Integración con Servicios Existentes**

### **ETL → MCP Integration**
El ETL Service puede comunicarse con el MCP existente:

```bash
# El ETL Service puede usar el KB del MCP
ETL_KB_URL=http://mcp:7000
```

### **ETL → API Integration**
El API principal puede consultar el ETL Service:

```python
# Desde el API principal
import httpx

async def get_etl_analysis():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://etl-service:9000/api/v1/info")
        return response.json()
```

## 🎯 **URLs de Acceso (En EC2)**

Una vez desplegado en EC2:

- **API Principal**: `http://tu-ec2-ip:8000`
- **MCP Service**: `http://tu-ec2-ip:7070`
- **ETL Service**: `http://tu-ec2-ip:9000` ✨ **NUEVO**

## 📊 **Ventajas de la Integración**

### **✅ Reutilización**
- Comparte credenciales de BD
- Reutiliza configuración de LLM
- Aprovecha volúmenes existentes

### **✅ Independencia**
- Puertos separados (sin conflictos)
- Puede ejecutarse independientemente
- Logs y métricas separados

### **✅ Escalabilidad**
- Cada servicio puede escalar por separado
- Deployment independiente posible
- Monitoreo granular

## 🚀 **Deployment en EC2**

### **Método 1: Integrado al Proyecto Principal**
```bash
# En EC2, clonar proyecto completo
git clone tu-repo
cd fixeatAI

# Configurar .env con las variables ETL
nano .env

# Iniciar todos los servicios
docker-compose up --build -d

# Verificar
curl http://localhost:9000/health
```

### **Método 2: Solo ETL Service**
```bash
# Si solo quieres el ETL Service
docker-compose up etl-service --build -d
```

## 📋 **Security Group para EC2**

Agregar puerto **9000** al Security Group existente:

| Puerto | Protocolo | Origen | Descripción |
|--------|-----------|---------|-------------|
| 8000 | TCP | 0.0.0.0/0 | API Principal (existente) |
| 7070 | TCP | 0.0.0.0/0 | MCP Service (existente) |
| 9000 | TCP | 0.0.0.0/0 | **ETL Service (NUEVO)** |

## 🎉 **¡Listo para Usar!**

El ETL Service está completamente integrado y listo para:

1. **✅ Analizar tu BD real** con documentación rica
2. **✅ Generar configuraciones ETL** automáticamente  
3. **✅ Extraer datos inteligentemente** 
4. **✅ Alimentar el Knowledge Base** principal
5. **✅ Funcionar junto a servicios existentes**

### **Comando para Iniciar Todo:**
```bash
# Agregar variables ETL al .env
# Luego ejecutar:
make all
```

**¡El ETL Service está listo para producción integrado al proyecto!** 🚀✨
