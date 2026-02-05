# 📚 Documentación FIXEAT AI - Predictor de Fallas

Bienvenido a la documentación del sistema FIXEAT AI - Predictor Inteligente de Fallas para Equipos de Cocina Industrial.

---

## 🎯 Sistema Enfocado

Este sistema tiene **dos componentes principales**:

1. **🔧 Predictor de Fallas** - API REST para diagnóstico inteligente
2. **📚 Knowledge Base** - Base de conocimiento vectorial con ChromaDB

---

## 📋 Índice de Documentación

### 🚀 [01. Getting Started](./01-getting-started/)
Documentación para comenzar con el proyecto.

| Documento | Descripción |
|-----------|-------------|
| [Quickstart](./01-getting-started/quickstart.md) | Guía rápida de inicio local (5 minutos) |
| [Arquitectura](./01-getting-started/arquitectura.md) | Visión general del sistema |
| [Estructura del Repo](./01-getting-started/estructura-repo.md) | Organización de carpetas y archivos |
| [Roadmap](./01-getting-started/roadmap.md) | Plan de desarrollo futuro |

---

### 📡 [02. API](./02-api/)
Documentación de la API del predictor.

| Documento | Descripción |
|-----------|-------------|
| [API Reference](./02-api/api.md) | Documentación completa de endpoints |
| [Endpoints Reference](./02-api/endpoints-reference.md) | Quick reference con ejemplos |
| [Schema de Respuesta](./02-api/schema-respuesta.md) | ⭐ Estructura detallada de JSON |
| [Integration Guide](./02-api/integration-guide.md) | Guía de integración |

**Endpoint Principal:**
```
POST http://18.220.79.28:8000/api/v1/predict-fallas
```

---

### ⚙️ [03. Features](./03-features/)
Funcionalidades del sistema.

| Documento | Descripción |
|-----------|-------------|
| [Predictor de Fallas](./03-features/predictor-fallas.md) | ⭐ Flujo completo del predictor |
| [Ingesta de KB](./03-features/ingesta-kb.md) | ⭐ Guía de carga de documentación |
| [Taxonomía](./03-features/taxonomia.md) | Sistema de taxonomía auto-aprendida |
| [Búsqueda de Errores](./03-features/busqueda-errores.md) | Búsqueda híbrida optimizada |
| [RAG Configuration](./03-features/rag-config.md) | Configuración del pipeline RAG |

---

### 💻 [04. Development](./04-development/)
Guías para desarrolladores.

| Documento | Descripción |
|-----------|-------------|
| [Runbook Local](./04-development/runbook-local.md) | Desarrollo en local |
| [Testing](./04-development/testing.md) | Estrategia de testing |
| [Estándares de Código](./04-development/estandares-codigo.md) | Convenciones |
| [Contributing](./04-development/contributing.md) | Guía de contribución |
| [Docker](./04-development/docker.md) | Uso de Docker local |
| [Entorno](./04-development/entorno-configuracion.md) | Variables de entorno |
| [LLM](./04-development/llm.md) | Integración con LLMs |
| [MCP Tools](./04-development/mcp-tools.md) | Herramientas MCP |

---

### 🚀 [05. Deployment](./05-deployment/)
Deployment y operaciones en producción.

| Documento | Descripción |
|-----------|-------------|
| **[Deployment Guide](./05-deployment/deployment-guide.md)** | 🌟 **Guía maestra** |
| [Deploy AWS](./05-deployment/deploy-aws.md) | Configuración de AWS EC2 |
| [Deploy CI/CD](./05-deployment/deploy-ci-cd.md) | Pipeline de CI/CD |
| [Runbooks](./05-deployment/runbooks.md) | Procedimientos operativos |
| [Observabilidad](./05-deployment/observabilidad.md) | Monitoreo y logs |
| [Seguridad](./05-deployment/seguridad.md) | Políticas de seguridad |

**Servidor:** `18.220.79.28` (AWS EC2 us-east-2)

---

### 🎨 [06. Presentations](./06-presentations/)
Presentaciones y demos.

| Documento | Descripción |
|-----------|-------------|
| [README](./06-presentations/README.md) | Guía de presentaciones |
| [Presentación Técnica](./06-presentations/presentacion-predictor.md) | Markdown completo |
| [Presentación Visual](./06-presentations/presentacion_visual.html) | HTML interactivo |

---

### ✅ [07. Testing Results](./07-testing-results/)
Resultados de pruebas del sistema.

| Documento | Descripción |
|-----------|-------------|
| [Resumen de Pruebas](./07-testing-results/resumen-pruebas.md) | Análisis de 6 pruebas (100% éxito) |
| [Test Cases](./07-testing-results/test-cases/) | JSONs de casos de prueba |

**Métricas:**
- Tasa de éxito: 100%
- Confidence: 0.45-0.85
- Tiempo: 25-50s
- KB Hits: 10-20 docs

---

### 🔧 [09. Technical Docs](./09-technical-docs/)
Documentación técnica detallada de implementaciones.

| Documento | Descripción |
|-----------|-------------|
| [Análisis del Sistema](./09-technical-docs/ANALISIS-SISTEMA-COMPLETO.md) | Análisis técnico completo |
| [Optimización iCombi](./09-technical-docs/OPTIMIZACION-ICOMBI-CLASSIC.md) | Optimización específica |
| [Sistema de Relevancia](./09-technical-docs/SISTEMA-RELEVANCIA-FINAL.md) | LLM Re-Ranker |
| [Búsqueda Híbrida](./09-technical-docs/IMPLEMENTACION-BUSQUEDA-ERRORES.md) | Implementación técnica |
| [Evaluación](./09-technical-docs/evaluacion-busqueda-errores-mejorada.md) | Evaluación de mejoras |
| [Mejoras IA](./09-technical-docs/mejoras-ia-implementadas.md) | Changelog técnico |

---

## 🔗 Quick Links por Rol

### 👨‍💻 Desarrolladores:
1. [Quickstart](./01-getting-started/quickstart.md) - Empezar en 5 minutos
2. [Runbook Local](./04-development/runbook-local.md) - Desarrollo local
3. [Schema de Respuesta](./02-api/schema-respuesta.md) - Estructura de datos

### 🚀 DevOps:
1. [Deployment Guide](./05-deployment/deployment-guide.md) - Guía completa
2. [Deploy AWS](./05-deployment/deploy-aws.md) - Configuración AWS
3. [Runbooks](./05-deployment/runbooks.md) - Procedimientos

### 📊 Product Managers:
1. [Arquitectura](./01-getting-started/arquitectura.md) - Visión del sistema
2. [Roadmap](./01-getting-started/roadmap.md) - Planificación
3. [Presentaciones](./06-presentations/) - Demos

### 🎓 Clientes/Demos:
1. [Presentación Visual](./06-presentations/presentacion_visual.html) - Demo interactivo
2. [Presentación Técnica](./06-presentations/presentacion-predictor.md) - Documentación

---

## 🎯 Flujo de Trabajo Típico

### 1. Desarrollar Localmente
```bash
source .venv/bin/activate
make dev-mcp  # Terminal 1
make run      # Terminal 2
```

### 2. Cargar Knowledge Base
```bash
python ingestar_via_api.py --urls urls.txt
```

### 3. Probar Predictor
```bash
curl -X POST http://localhost:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{...}'
```

### 4. Deploy a Producción
```bash
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Componentes del Sistema

### Core (Predictor + KB)
```
✅ /app/main.py                    # API principal
✅ /mcp/server_demo.py             # Servidor MCP con KB
✅ /services/kb/demo_kb.py         # ChromaDB
✅ /services/orch/rag.py           # Motor RAG
✅ /services/orch/llm_reranker.py  # Re-ranking
✅ /services/predictor/heuristic.py # Heurística
✅ /services/llm/client.py         # Cliente LLM
✅ /services/taxonomy/             # Taxonomía
✅ /chroma_local/                  # Base vectorial
✅ ingestar_*.py                   # Scripts ingesta
```

### Infraestructura
```
✅ docker-compose.yml
✅ Dockerfile
✅ Makefile
✅ pyproject.toml
✅ configs/taxonomy.json
```

---

## 🚀 Quick Commands

```bash
# Local
make dev-mcp       # Levantar MCP (KB)
make run           # Levantar API
make test          # Correr tests

# Producción
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI && docker-compose ps
curl http://18.220.79.28:8000/health
```

---

## 📈 Estado del Sistema

| Servicio | Estado | Puerto | URL |
|----------|--------|--------|-----|
| **API** | ✅ ACTIVO | 8000 | http://18.220.79.28:8000 |
| **MCP/KB** | ✅ ACTIVO | 7070 | http://18.220.79.28:7070 |

**Última actualización:** 2 de febrero de 2026

---

<div align="center">

### 🎯 El sistema está enfocado en lo esencial:

**PREDICTOR DE FALLAS + KNOWLEDGE BASE**

Nada más. Nada menos.

---

**[🚀 Comenzar →](./01-getting-started/quickstart.md)** • 
**[📡 API →](./02-api/)** • 
**[📚 Ingesta KB →](./03-features/ingesta-kb.md)**

</div>
