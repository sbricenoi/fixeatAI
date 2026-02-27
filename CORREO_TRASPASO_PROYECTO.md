# CORREO DE TRASPASO - PROYECTO FIXEAT AI

---

**Asunto:** Traspaso de Proyecto - FIXEAT AI: Predictor Inteligente de Fallas en Equipos

---

## Estimado/a [Nombre del Receptor],

Me complace realizar el traspaso formal del proyecto **FIXEAT AI**, un sistema de inteligencia artificial para diagnóstico de fallas en equipos de cocina industrial. Este correo contiene toda la información necesaria para que puedas asumir el proyecto con claridad y confianza.

---

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Acceso a Recursos](#acceso-a-recursos)
5. [Cómo Ejecutar Localmente](#cómo-ejecutar-localmente)
6. [Servidor de Producción](#servidor-de-producción)
7. [Documentación Completa](#documentación-completa)
8. [Estado Actual del Proyecto](#estado-actual-del-proyecto)
9. [Próximos Pasos Sugeridos](#próximos-pasos-sugeridos)
10. [Contacto y Soporte](#contacto-y-soporte)

---

## 1. RESUMEN EJECUTIVO

### ¿Qué es FIXEAT AI?

FIXEAT AI es un sistema de inteligencia artificial que ayuda a técnicos de servicio a diagnosticar fallas en equipos de cocina industrial. El sistema:

- ✅ Analiza descripciones de problemas técnicos
- ✅ Busca en una base de conocimiento vectorial (ChromaDB)
- ✅ Utiliza GPT-4o-mini para análisis contextual
- ✅ Sugiere fallas probables con nivel de confianza
- ✅ Recomienda repuestos y herramientas específicas
- ✅ Genera pasos detallados de diagnóstico y reparación

### Métricas de Rendimiento

| Métrica | Valor |
|---------|-------|
| **Tasa de éxito** | 100% |
| **Tiempo de respuesta** | 25-50 segundos |
| **Confidence máximo** | 0.85 (Muy Alta) |
| **Documentos consultados** | 10-20 por consulta |
| **Estado en producción** | ✅ ACTIVO desde Diciembre 2025 |

### Limpieza Reciente (Feb 2, 2026)

El proyecto acaba de pasar por una **limpieza completa** donde se eliminaron todos los componentes no relacionados con el predictor de fallas:

- ❌ Eliminados: 4 servicios no relacionados (animal-ai, recommender, ETL, etc.)
- ❌ Eliminados: 30+ archivos de documentación obsoletos
- ❌ Eliminados: ~80 MB de código no usado
- ✅ Resultado: **Proyecto 100% enfocado en Predictor + Knowledge Base**

---

## 2. ARQUITECTURA DEL SISTEMA

### Arquitectura de Alto Nivel

```
┌──────────────┐
│   Cliente    │ (Frontend, Mobile, API)
└──────┬───────┘
       │ HTTP POST /api/v1/predict-fallas
       ▼
┌────────────────────────────────────────┐
│    🌐 API (FastAPI)                    │
│    Puerto: 8000                        │
│    - Endpoint principal: predict       │
│    - Health check                      │
└──────┬───────────────────┬─────────────┘
       │                   │
       │ Búsqueda          │ Análisis
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ 📚 MCP/KB    │    │ 🤖 LLM       │
│ ChromaDB     │◄───│ GPT-4o-mini  │
│ Puerto: 7070 │    │ (OpenAI)     │
└──────────────┘    └──────────────┘
       │
       │ Semantic + Keyword Search
       ▼
┌──────────────────────────┐
│  Knowledge Base          │
│  - Manuales técnicos     │
│  - Hojas de datos        │
│  - Documentación         │
│  - Historial de casos    │
└──────────────────────────┘
```

### Componentes Core

1. **API Service** (`app/main.py`)
   - Framework: FastAPI
   - Puerto: 8000
   - Endpoint principal: `POST /api/v1/predict-fallas`
   - Health check: `GET /health`

2. **MCP Service** (`mcp/server_demo.py`)
   - Knowledge Base Server con ChromaDB
   - Puerto: 7070
   - Funciones: búsqueda semántica, ingesta, taxonomía

3. **Services** (carpeta `services/`)
   - `kb/`: Gestión de ChromaDB y búsquedas
   - `llm/`: Cliente OpenAI GPT
   - `orch/`: Orquestador RAG y re-ranker LLM
   - `predictor/`: Motor de predicción heurística
   - `taxonomy/`: Auto-aprendizaje de marcas/modelos

### Flujo de Predicción

```
1. Cliente envía problema → API
2. API consulta MCP/KB (búsqueda híbrida)
3. KB retorna 10-20 documentos relevantes
4. LLM re-rankea por relevancia
5. RAG genera predicción con LLM
6. API retorna JSON con fallas, repuestos, pasos
```

---

## 3. STACK TECNOLÓGICO

### Backend & API
- **Python 3.10** - Lenguaje principal
- **FastAPI** - Framework web moderno y rápido
- **Pydantic 2.x** - Validación de datos
- **Uvicorn** - ASGI server

### Inteligencia Artificial
- **OpenAI GPT-4o-mini** - Large Language Model
- **Sentence-Transformers** - Embeddings semánticos (modelo: all-MiniLM-L6-v2)
- **ChromaDB 0.5+** - Base de datos vectorial

### Dependencias Principales
```
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
sentence-transformers>=3.0.0
chromadb>=0.5.0
openai>=1.40.0
pymupdf>=1.24.0  # Para PDFs
beautifulsoup4>=4.12.3  # Para HTML
```

### Infraestructura
- **Docker & Docker Compose** - Containerización
- **AWS EC2** - us-east-2 (Ohio)
- **Amazon Linux 2023** - Sistema operativo
- **Git/GitHub** - Control de versiones

---

## 4. ACCESO A RECURSOS

### Repositorio GitHub

```
URL: https://github.com/sbricenoi/fixeatAI
Branch principal: main
Último commit: refactor: Limpieza completa del proyecto (Feb 2, 2026)
```

**Clonar repositorio:**
```bash
git clone https://github.com/sbricenoi/fixeatAI.git
cd fixeatAI
```

### Servidor de Producción (AWS EC2)

| Recurso | Valor |
|---------|-------|
| **IP Pública** | `18.220.79.28` |
| **Hostname** | `ec2-18-220-79-28.us-east-2.compute.amazonaws.com` |
| **Región AWS** | us-east-2 (Ohio) |
| **Sistema Operativo** | Amazon Linux 2023 |
| **Usuario SSH** | `ec2-user` |
| **Clave SSH** | `fixeatIA.pem` (NO está en Git, solicitar por canal seguro) |

**Conexión SSH:**
```bash
ssh -i fixeatIA.pem ec2-user@18.220.79.28
```

### URLs de Servicios en Producción

| Servicio | URL | Estado |
|----------|-----|--------|
| **API** | http://18.220.79.28:8000 | ✅ ACTIVO |
| **MCP/KB** | http://18.220.79.28:7070 | ✅ ACTIVO |
| **Health Check API** | http://18.220.79.28:8000/health | ✅ OK |
| **Health Check MCP** | http://18.220.79.28:7070/health | ✅ OK |

### Credenciales y Variables de Entorno

**Variables requeridas** (archivo `.env` en servidor):
```bash
OPENAI_API_KEY=sk-...        # API Key de OpenAI (solicitar acceso)
USE_LLM=true                 # Usar LLM (true/false)
LLM_MODEL=gpt-4o-mini        # Modelo GPT
CORS_ALLOW_ORIGINS=*         # CORS config
```

**⚠️ IMPORTANTE:** El archivo `.env` con credenciales NO está en Git por seguridad. Solicitar acceso al archivo por canal seguro.

---

## 5. CÓMO EJECUTAR LOCALMENTE

### Requisitos Previos

- Python 3.10 o superior
- Git
- Cuenta OpenAI con API Key

### Paso a Paso

#### 1. Clonar y preparar entorno

```bash
# Clonar repositorio
git clone https://github.com/sbricenoi/fixeatAI.git
cd fixeatAI

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -e .
```

#### 2. Configurar variables de entorno

```bash
# Copiar template
cp .env.example .env

# Editar .env y agregar tu OpenAI API Key
nano .env  # o el editor de tu preferencia
```

Contenido mínimo del `.env`:
```
OPENAI_API_KEY=sk-tu-api-key-aqui
USE_LLM=true
LLM_MODEL=gpt-4o-mini
```

#### 3. Levantar servicios

**Opción A: Usando Makefile (Recomendado)**

En dos terminales separadas:

```bash
# Terminal 1: Levantar MCP/KB
make dev-mcp

# Terminal 2: Levantar API
make run
```

**Opción B: Comandos directos**

```bash
# Terminal 1: MCP
ROLE=mcp uvicorn mcp.server_demo:app --host 0.0.0.0 --port 7000 --reload

# Terminal 2: API
ROLE=api uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. Verificar funcionamiento

```bash
# Health checks
curl http://localhost:7000/health
curl http://localhost:8000/health

# Buscar en KB (debe retornar hits si ya hay datos)
curl -X POST http://localhost:7000/tools/kb_search \
  -H 'Content-Type: application/json' \
  -d '{"query": "horno rational problema calor", "n_results": 5}'

# Test de predicción
curl -X POST http://localhost:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente": {"id": "test001"},
    "equipo": {"marca": "Rational", "modelo": "Icombi Pro"},
    "descripcion_problema": "El horno no calienta, temperatura no sube",
    "tecnico": {"id": "t001", "experiencia_anios": 3}
  }'
```

#### 5. Ingestar datos a la KB (Opcional)

Si la KB está vacía, puedes cargar documentación:

```bash
# Ingestar PDFs desde URLs
python ingestar_via_api.py --urls lista_urls.txt

# O un PDF local
python ingestar_pdfs.py --pdf manual_rational.pdf

# Batch de múltiples archivos
python ingestar_batch.py --dir ./manuales/
```

---

## 6. SERVIDOR DE PRODUCCIÓN

### Información del Servidor

| Aspecto | Detalle |
|---------|---------|
| **Proveedor** | AWS EC2 |
| **Tipo instancia** | [Verificar con `aws ec2 describe-instances`] |
| **Sistema operativo** | Amazon Linux 2023 |
| **Docker** | Instalado |
| **Docker Compose** | v2.29.7 |
| **Servicios activos** | `fixeatai-mcp` (puerto 7070) + `fixeatai-api` (puerto 8000) |

### Conectarse al Servidor

```bash
# Conectar vía SSH (requiere clave privada fixeatIA.pem)
ssh -i fixeatIA.pem ec2-user@18.220.79.28

# Una vez conectado
cd fixeatAI
```

### Comandos Útiles en Producción

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs -f api    # Logs de API
docker-compose logs -f mcp    # Logs de MCP
docker-compose logs -f --tail=100  # Últimas 100 líneas de todos

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Levantar servicios
docker-compose up -d
```

### Actualizar el Código en Producción

**Proceso completo:**

```bash
# 1. Conectar al servidor
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI

# 2. Descargar últimos cambios
git pull origin main

# 3. Detener contenedores (incluye limpieza de huérfanos)
docker-compose down --remove-orphans

# 4. Rebuild de imágenes (sin cache para garantizar actualización)
docker-compose build --no-cache

# 5. Levantar servicios
docker-compose up -d

# 6. Verificar que levantaron correctamente
docker-compose ps

# 7. Verificar health checks
curl http://localhost:8000/health
curl http://localhost:7070/health

# 8. Ver logs por unos segundos para confirmar
docker-compose logs -f --tail=50
```

**Verificación esperada:**

```
NAME                STATUS              PORTS
fixeatai-mcp        Up XX seconds       0.0.0.0:7070->7000/tcp
fixeatai-api        Up XX seconds       0.0.0.0:8000->8000/tcp
```

### Persistencia de Datos

La base de datos vectorial (ChromaDB) se almacena en un volumen Docker:

```bash
# Volumen: chroma_data
# Path interno contenedor: /data/chroma
# Backup automático: Configurado cada 24h a S3 (verificar cron)
```

**Crear backup manual:**

```bash
# Desde el servidor
docker-compose exec mcp tar -czf - /data/chroma > chroma_backup_$(date +%Y%m%d).tar.gz

# Copiar backup a local (desde tu máquina)
scp -i fixeatIA.pem ec2-user@18.220.79.28:~/chroma_backup_*.tar.gz ./backups/
```

### Monitoreo

**Health Checks Automáticos:**

Los servicios tienen health checks configurados cada 30 segundos. Docker reinicia automáticamente si fallan.

**Verificar manualmente:**

```bash
# Desde el servidor
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:7070/health | jq .

# Ver recursos del sistema
docker stats

# Ver espacio en disco
df -h
```

---

## 7. DOCUMENTACIÓN COMPLETA

La documentación está completamente reorganizada en la carpeta `docs/` del repositorio.

### Estructura de Documentación

```
docs/
├── README.md                    # 📋 Índice maestro de documentación
│
├── 01-getting-started/         # 🚀 INICIO RÁPIDO
│   ├── quickstart.md           # Guía de inicio rápido
│   ├── arquitectura.md         # Arquitectura detallada del sistema
│   ├── estructura-repo.md      # Explicación de carpetas y archivos
│   └── roadmap.md              # Roadmap y próximas features
│
├── 02-api/                     # 📡 API REFERENCE
│   ├── api.md                  # Guía general de la API
│   ├── endpoints-reference.md  # Referencia completa de endpoints
│   ├── schema-respuesta.md     # Schema detallado de respuestas JSON
│   └── integration-guide.md    # Cómo integrar con otros sistemas
│
├── 03-features/                # ⚙️ CARACTERÍSTICAS
│   ├── predictor-fallas.md     # Cómo funciona el predictor
│   ├── ingesta-kb.md           # Carga de documentos a la KB
│   ├── busqueda-errores.md     # Búsqueda optimizada de códigos error
│   ├── rag-config.md           # Configuración del RAG pipeline
│   └── taxonomia.md            # Sistema de auto-aprendizaje
│
├── 04-development/             # 💻 DESARROLLO
│   ├── runbook-local.md        # Cómo desarrollar localmente
│   ├── docker.md               # Uso de Docker
│   ├── testing.md              # Cómo ejecutar tests
│   ├── contributing.md         # Guía para contribuir código
│   ├── estandares-codigo.md    # Estándares de código
│   ├── llm.md                  # Trabajar con LLMs
│   ├── mcp-orquestacion.md     # MCP y orquestación
│   └── mcp-tools.md            # Herramientas MCP disponibles
│
├── 05-deployment/              # 🚀 DEPLOYMENT
│   ├── deployment-guide.md     # Guía maestra de deployment
│   ├── deploy-aws.md           # Deploy específico en AWS
│   ├── deploy-ci-cd.md         # Configuración CI/CD
│   ├── runbooks.md             # Runbooks de operaciones
│   ├── observabilidad.md       # Monitoreo y logs
│   └── seguridad.md            # Consideraciones de seguridad
│
├── 06-presentations/           # 🎨 PRESENTACIONES
│   ├── README.md               # Índice de presentaciones
│   ├── presentacion-predictor.md    # Presentación ejecutiva
│   └── presentacion_visual.html     # Demo interactivo
│
├── 07-testing-results/         # ✅ RESULTADOS DE PRUEBAS
│   ├── resumen-pruebas.md      # Análisis de 6 pruebas exhaustivas
│   └── test-cases/             # Casos de prueba en JSON
│       ├── test1_rational_calentamiento.json
│       ├── test2_electrolux_vapor.json
│       └── ...
│
└── 09-technical-docs/          # 📚 DOCUMENTACIÓN TÉCNICA AVANZADA
    ├── ANALISIS-SISTEMA-COMPLETO.md
    ├── IMPLEMENTACION-BUSQUEDA-ERRORES.md
    └── ...
```

### Documentos Clave para Comenzar

**Para entender el proyecto:**
1. `README.md` (raíz del repo) - Visión general
2. `docs/README.md` - Índice de toda la documentación
3. `docs/01-getting-started/arquitectura.md` - Arquitectura detallada

**Para desarrollar:**
1. `docs/01-getting-started/quickstart.md` - Inicio rápido
2. `docs/04-development/runbook-local.md` - Desarrollo local
3. `docs/02-api/schema-respuesta.md` - Schema de API

**Para deployment:**
1. `docs/05-deployment/deployment-guide.md` - Guía maestra
2. `docs/05-deployment/deploy-aws.md` - Deploy en AWS

**Para entender cambios recientes:**
1. `LIMPIEZA_PROYECTO.md` - Detalle de limpieza (Feb 2, 2026)
2. `REORGANIZACION_DOCS.md` - Mapa de reorganización

---

## 8. ESTADO ACTUAL DEL PROYECTO

### ✅ Completado y Funcionando

- ✅ **API REST** funcionando en producción (v0.2.0)
- ✅ **Endpoint de predicción** `/api/v1/predict-fallas` operativo
- ✅ **Knowledge Base** con ChromaDB funcionando
- ✅ **Búsqueda híbrida** (semántica + keywords)
- ✅ **LLM Re-Ranker** para mejorar relevancia
- ✅ **Taxonomía auto-aprendida** de marcas/modelos
- ✅ **Deployment en AWS EC2** estable
- ✅ **Docker Compose** con 2 servicios (mcp + api)
- ✅ **Health checks** automáticos
- ✅ **Documentación** completa y reorganizada
- ✅ **Limpieza de código** (eliminados servicios no relacionados)

### Métricas de Producción (últimas pruebas)

| Test | Equipo | Confidence | KB Hits | Tiempo | Resultado |
|------|--------|------------|---------|--------|-----------|
| 1 | Rational Icombi Pro | 0.85 | 20 | 35s | ✅ Éxito |
| 2 | Electrolux Air-O-Steam | 0.75 | 18 | 28s | ✅ Éxito |
| 3 | Rational (código error) | 0.75 | 15 | 42s | ✅ Éxito |
| 4 | Genérico | 0.65 | 12 | 25s | ✅ Éxito |
| 5 | Muy detallado | 0.85 | 20 | 50s | ✅ Éxito |
| 6 | Mínimo | 0.45 | 10 | 22s | ✅ Éxito |

**Conclusión:** Sistema estable con 100% de tasa de éxito.

### 📊 Estadísticas del Código

| Métrica | Valor |
|---------|-------|
| **Lenguaje principal** | Python 3.10 |
| **Total de líneas** | ~5,000 líneas (después de limpieza) |
| **Servicios activos** | 2 (mcp, api) |
| **Endpoints API** | 3 (predict-fallas, health, root) |
| **Módulos core** | 5 (kb, llm, orch, predictor, taxonomy) |
| **Scripts de ingesta** | 3 (via_api, batch, pdfs) |
| **Tests** | Manuales (ver docs/07-testing-results/) |

### ⚙️ Configuración Actual

**LLM:**
- Modelo: GPT-4o-mini
- Temperatura: 0.7 (configurable)
- Max tokens: 2000 (configurable)
- Provider: OpenAI

**Vector DB:**
- Motor: ChromaDB 0.5+
- Embeddings: all-MiniLM-L6-v2 (Sentence-Transformers)
- Dimensiones: 384
- Distancia: Cosine similarity

**Búsqueda:**
- Método: Híbrido (semántica + keywords)
- Top K: 20 documentos
- Re-ranking: LLM-based
- Chunk size: ~500 tokens con overlap de 50

---

## 9. PRÓXIMOS PASOS SUGERIDOS

### Prioridad Alta 🔴

1. **Familiarización con el código**
   - Leer `README.md` y `docs/README.md`
   - Revisar arquitectura en `docs/01-getting-started/arquitectura.md`
   - Ejecutar localmente siguiendo `docs/01-getting-started/quickstart.md`

2. **Verificar acceso a recursos**
   - Solicitar clave SSH `fixeatIA.pem` (si no la tienes)
   - Solicitar archivo `.env` con credenciales de OpenAI
   - Conectarte al servidor de producción y verificar estado
   - Clonar repositorio y verificar que compila localmente

3. **Hacer pruebas de concepto**
   - Levantar servicios localmente
   - Hacer al menos 3 llamadas de prueba a la API
   - Ingestar un documento de prueba a la KB
   - Verificar que la búsqueda encuentra el documento

### Prioridad Media 🟡

4. **Monitoreo y mantenimiento**
   - Configurar alertas de health checks (CloudWatch, Datadog, etc.)
   - Verificar backups de la KB (revisar cron en servidor)
   - Documentar procedimientos de rollback

5. **Mejoras incrementales**
   - Implementar tests unitarios automatizados (pytest)
   - Configurar CI/CD (GitHub Actions sugerido)
   - Mejorar logging y observabilidad

6. **Optimizaciones**
   - Evaluar caché de consultas frecuentes (Redis)
   - Optimizar chunking de documentos
   - Ajustar hiperparámetros del RAG

### Prioridad Baja 🟢

7. **Features nuevas** (ver `docs/01-getting-started/roadmap.md`)
   - Análisis de imágenes (visión por computadora)
   - Dashboard de métricas
   - App móvil
   - Multi-idioma

---

## 10. CONTACTO Y SOPORTE

### Recursos de Soporte

| Recurso | Link/Contacto |
|---------|---------------|
| **GitHub Issues** | https://github.com/sbricenoi/fixeatAI/issues |
| **Documentación** | https://github.com/sbricenoi/fixeatAI/tree/main/docs |
| **Archivo de traspaso** | Este documento (CORREO_TRASPASO_PROYECTO.md) |

### Para Consultas Urgentes

- **Desarrollador saliente:** [Tu nombre] - [Tu email] - [Tu teléfono]
- **Soporte técnico:** [Email de soporte]
- **AWS Account:** [Contacto del dueño de la cuenta AWS]
- **OpenAI API:** [Contacto con acceso a la API Key]

### Checklist de Transferencia

Antes de considerar el traspaso completo, verifica:

- [ ] Has recibido acceso al repositorio GitHub
- [ ] Has recibido la clave SSH `fixeatIA.pem`
- [ ] Has recibido el archivo `.env` con credenciales
- [ ] Has podido conectarte al servidor de producción
- [ ] Has ejecutado el proyecto localmente con éxito
- [ ] Has hecho al menos 1 llamada exitosa a la API de producción
- [ ] Has leído la documentación principal (README + arquitectura)
- [ ] Has revisado el estado de los servicios en producción
- [ ] Conoces el proceso de actualización de código
- [ ] Tienes los contactos de soporte necesarios

---

## 📎 ANEXOS

### A. Ejemplo de Request/Response de API

**Request:**
```bash
curl -X POST http://18.220.79.28:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente": {
      "id": "cliente-123",
      "nombre": "Restaurante Demo"
    },
    "equipo": {
      "marca": "Rational",
      "modelo": "Icombi Pro 10-1/1",
      "numero_serie": "123456"
    },
    "descripcion_problema": "El horno no calienta correctamente, la temperatura no sube más de 150 grados. Muestra código de error Service 05.",
    "sintomas_adicionales": [
      "Ventilador funciona normalmente",
      "No hay fugas de vapor visibles"
    ],
    "tecnico": {
      "id": "tec-001",
      "nombre": "Juan Pérez",
      "experiencia_anios": 5
    }
  }'
```

**Response (simplificado):**
```json
{
  "traceId": "abc-123-xyz",
  "code": "OK",
  "message": "Predicción generada exitosamente",
  "data": {
    "fallas_probables": [
      {
        "falla": "Problema con resistencia de calefacción",
        "confidence": 0.85,
        "descripcion": "La resistencia principal podría estar dañada o desconectada",
        "repuestos_sugeridos": [
          {"nombre": "Resistencia calefactora", "codigo": "RAT-RES-1001"},
          {"nombre": "Termopar", "codigo": "RAT-TEMP-200"}
        ],
        "herramientas_sugeridas": ["Multímetro", "Destornillador Torx"],
        "pasos": [
          "1. Desconectar equipo de la red eléctrica",
          "2. Retirar panel lateral derecho",
          "3. Medir continuidad de resistencia con multímetro",
          "4. Si no hay continuidad, reemplazar resistencia",
          "5. Verificar conexiones del termopar"
        ],
        "precauciones_seguridad": [
          "Desconectar energía antes de manipular componentes",
          "Usar guantes dieléctricos"
        ]
      }
    ],
    "contextos": [
      {
        "contenido": "Service 05 indica fallo en sistema de calentamiento...",
        "fuente": "Manual Rational Icombi Pro - Sección 8.5",
        "url": "https://...",
        "relevancia": 0.92
      }
    ],
    "signals": {
      "kb_hits": 18,
      "llm_used": true,
      "search_time_ms": 1250,
      "llm_time_ms": 8500
    }
  }
}
```

### B. Comandos Makefile Disponibles

```bash
make help              # Ver todos los comandos disponibles
make dev-mcp           # Levantar MCP en modo desarrollo
make run               # Levantar API en modo desarrollo
make docker-up         # Levantar con Docker Compose
make docker-down       # Detener Docker Compose
make docker-rebuild    # Rebuild de imágenes
make docker-logs       # Ver logs de contenedores
make health-local      # Health check local
make health-prod       # Health check producción
```

### C. Archivos de Configuración Importantes

| Archivo | Propósito |
|---------|-----------|
| `pyproject.toml` | Dependencias Python y configuración |
| `docker-compose.yml` | Orquestación de servicios |
| `Dockerfile` | Build de imagen Docker |
| `.env` | Variables de entorno (NO en Git) |
| `.gitignore` | Archivos excluidos de Git |
| `Makefile` | Comandos de desarrollo |

---

## 🎯 RESUMEN FINAL

**El proyecto FIXEAT AI está:**

✅ **Producción-ready** - Funcionando establemente en AWS  
✅ **Bien documentado** - 7 secciones de docs organizadas  
✅ **Limpio y enfocado** - Solo código esencial (Feb 2, 2026)  
✅ **Escalable** - Arquitectura modular con Docker  
✅ **Mantenible** - Código Python claro con estándares  

**Para comenzar:**

1. Leer este documento completo ✅
2. Clonar repositorio y leer README.md
3. Solicitar accesos (SSH key, .env)
4. Ejecutar localmente
5. Conectarte a producción y verificar estado

**Si tienes cualquier duda o necesitas aclaraciones, no dudes en contactarme.**

---

Saludos cordiales,

**[Tu Nombre]**  
[Tu Cargo]  
[Tu Email]  
[Tu Teléfono]

**Fecha de traspaso:** 2 de febrero de 2026

---

*Este documento contiene información sensible sobre infraestructura y accesos. Mantenerlo en lugar seguro y compartir solo con personal autorizado.*
