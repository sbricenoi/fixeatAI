# 🔧 FIXEAT AI - Predictor de Fallas Inteligente

Sistema de Inteligencia Artificial para diagnóstico de fallas en equipos de cocina industrial, basado en RAG (Retrieval-Augmented Generation) con LLM y Knowledge Base vectorial.

[![Estado](https://img.shields.io/badge/estado-producción-brightgreen)](http://18.220.79.28:8000/health)
[![API](https://img.shields.io/badge/API-v0.2.0-blue)](http://18.220.79.28:8000)
[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)](https://fastapi.tiangolo.com/)

---

## 🎯 ¿Qué es FIXEAT AI?

FIXEAT AI es un sistema inteligente que ayuda a técnicos de servicio a:

- 🔍 **Diagnosticar fallas** con alto nivel de confianza (hasta 85%)
- 🔩 **Sugerir repuestos específicos** con códigos de parte
- 🛠️ **Recomendar herramientas** necesarias
- 📋 **Generar pasos detallados** de diagnóstico y reparación
- ⚠️ **Incluir protocolos de seguridad** automáticamente

---

## ✨ Características Principales

### 🤖 Inteligencia Artificial Avanzada
- **LLM (GPT-4o-mini)** para análisis contextual
- **RAG Pipeline** con búsqueda híbrida (semántica + keywords)
- **LLM Re-Ranker** para ranking inteligente de documentos
- **Taxonomía auto-aprendida** de marcas, modelos y categorías

### 📚 Knowledge Base Vectorial
- **ChromaDB** para almacenamiento de embeddings
- **Sentence-Transformers** para búsqueda semántica
- **Ingesta multi-formato**: PDFs, Word, Excel, HTML, URLs
- **Chunking inteligente** con overlap y quality scoring

### 🎯 Predicción Precisa
- **Confidence scoring** (0.0-1.0) basado en calidad de información
- **Búsqueda optimizada** para códigos de error (Service XX, Error YY)
- **Contexto ampliado** (hasta 2000 caracteres por documento)
- **Fuentes citables** con URLs navegables

---

## 🚀 Quick Start

### Desarrollo Local

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd fixeatAI

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -e .

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# 5. Levantar servicios
make dev-mcp  # Terminal 1: MCP Server (KB)
make run      # Terminal 2: API Server

# 6. Verificar
curl http://localhost:8000/health
```

📖 **[Ver guía completa →](./docs/01-getting-started/quickstart.md)**

---

### Usar API en Producción

```bash
# Health check
curl http://18.220.79.28:8000/health

# Predicción de falla
curl -X POST http://18.220.79.28:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente": {"id": "c001"},
    "equipo": {"marca": "Rational", "modelo": "Icombi Pro"},
    "descripcion_problema": "El horno no calienta correctamente, temperatura no sube de 150 grados",
    "tecnico": {"id": "t001", "experiencia_anios": 5}
  }'
```

**Respuesta esperada:**
```json
{
  "traceId": "uuid",
  "code": "OK",
  "message": "Predicción generada",
  "data": {
    "fallas_probables": [
      {
        "falla": "Problema con resistencia de calefacción",
        "confidence": 0.75,
        "repuestos_sugeridos": ["resistencia", "termopar"],
        "herramientas_sugeridas": ["multímetro", "destornillador"],
        "pasos": [...]
      }
    ],
    "contextos": [...],
    "signals": {"kb_hits": 10, "llm_used": true}
  }
}
```

📖 **[Ver schema completo →](./docs/02-api/schema-respuesta.md)**

---

## 📚 Documentación

La documentación está organizada en secciones temáticas:

| Sección | Descripción | Link |
|---------|-------------|------|
| 🚀 **Getting Started** | Quickstart, arquitectura | [Ver →](./docs/01-getting-started/) |
| 📡 **API** | Endpoints, schemas, integration | [Ver →](./docs/02-api/) |
| ⚙️ **Features** | Predictor, KB, taxonomía | [Ver →](./docs/03-features/) |
| 💻 **Development** | Runbooks, testing | [Ver →](./docs/04-development/) |
| 🚀 **Deployment** | AWS, CI/CD, runbooks | [Ver →](./docs/05-deployment/) |
| 🎨 **Presentations** | Demos para clientes | [Ver →](./docs/06-presentations/) |
| ✅ **Testing** | Resultados de pruebas | [Ver →](./docs/07-testing-results/) |

📖 **[Ver índice completo →](./docs/README.md)**

---

## 🏗️ Arquitectura

```
┌──────────────┐
│   Cliente    │ (Frontend, Mobile, API)
└──────┬───────┘
       │ HTTP POST /api/v1/predict-fallas
       ▼
┌──────────────────────────────────────┐
│    🌐 API (FastAPI)                  │
│    Puerto: 8000                      │
│    - Endpoint principal: predict     │
│    - Health check                    │
└──────┬───────────────────┬───────────┘
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

📖 **[Ver arquitectura detallada →](./docs/01-getting-started/arquitectura.md)**

---

## 🛠️ Stack Tecnológico

### Backend & API
- **Python 3.10** - Lenguaje principal
- **FastAPI** - Framework web
- **Pydantic** - Validación de datos

### AI/ML
- **OpenAI GPT-4o-mini** - Large Language Model
- **Sentence-Transformers** - Embeddings semánticos (all-MiniLM-L6-v2)
- **ChromaDB** - Vector database

### Infraestructura
- **Docker & Docker Compose** - Containerización
- **AWS EC2** - Hosting (us-east-2)

---

## 📊 Resultados en Producción

**Basado en 6 pruebas exhaustivas:**

| Métrica | Valor |
|---------|-------|
| **Tasa de éxito** | 100% |
| **Tiempo de respuesta** | 25-50 segundos |
| **KB Hits promedio** | 10-20 documentos |
| **Confidence máximo** | 0.85 (Muy Alta) |
| **Fuentes citadas** | 10-20 por consulta |

**Niveles de confidence según calidad del input:**
- **0.85** - Descripción muy detallada con múltiples síntomas + código de error
- **0.75** - Código de error específico
- **0.65** - Descripción clara de síntomas
- **0.50** - Descripción genérica
- **0.45** - Información vaga

📖 **[Ver análisis completo →](./docs/07-testing-results/resumen-pruebas.md)**

---

## 🚀 Deployment

### Servidor Productivo

| Info | Valor |
|------|-------|
| **IP** | `18.220.79.28` |
| **Host** | `ec2-18-220-79-28.us-east-2.compute.amazonaws.com` |
| **API** | http://18.220.79.28:8000 |
| **MCP** | http://18.220.79.28:7070 |
| **Estado** | ✅ ACTIVO |

### Deploy Rápido

```bash
# Conectar al servidor
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI

# Actualizar código
git pull origin main

# Rebuild y restart
docker-compose build --no-cache
docker-compose up -d

# Verificar
docker-compose ps
curl http://localhost:8000/health
```

📖 **[Ver guía completa de deployment →](./docs/05-deployment/deployment-guide.md)**

---

## 📁 Estructura del Proyecto

```
fixeatAI/
├── app/                      # 🌐 API Principal
│   └── main.py              # Endpoint predict-fallas
├── mcp/                      # 📚 Servidor MCP con KB
│   └── server_demo.py       # KB tools (search, ingest)
├── services/                 # ⚙️ Servicios Core
│   ├── kb/                  # ChromaDB y funciones KB
│   ├── llm/                 # Cliente LLM (OpenAI)
│   ├── orch/                # Orquestador RAG
│   │   ├── rag.py          # 🔥 Motor principal RAG
│   │   └── llm_reranker.py # Re-ranking LLM
│   ├── predictor/           # Lógica heurística
│   └── taxonomy/            # Auto-aprendizaje
├── chroma_local/            # 💾 Base de datos vectorial
├── configs/                 # ⚙️ Configuraciones
│   └── taxonomy.json       # Taxonomía aprendida
├── docs/                    # 📚 Documentación
├── ingestar_*.py           # 📥 Scripts de ingesta KB
├── docker-compose.yml      # 🐳 Orquestación Docker
├── Dockerfile              # 🐳 Build de imágenes
├── Makefile                # 🔧 Comandos útiles
└── pyproject.toml          # 📦 Dependencias
```

---

## 📥 Ingesta de Knowledge Base

Para alimentar el sistema con documentación técnica:

```bash
# Ingestar PDFs desde URLs
python ingestar_via_api.py --urls urls.txt

# Ingestar directamente
python ingestar_directo.py --pdf manual.pdf

# Batch de múltiples archivos
python ingestar_batch.py --dir ./manuales/
```

📖 **[Ver guía completa de ingesta →](./docs/03-features/ingesta-kb.md)**

---

## 🧪 Testing

```bash
# Tests unitarios
pytest tests/

# Test de API en producción
curl -X POST http://18.220.79.28:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d @tests/fixtures/test_request.json
```

---

## 🤝 Contribuir

1. **Fork** del repositorio
2. **Branch** desde `main`: `git checkout -b feature/nueva-feature`
3. **Commit** con mensajes descriptivos
4. **Push** al branch: `git push origin feature/nueva-feature`
5. **Pull Request** a `main`

📖 **[Ver guía de contribución →](./docs/04-development/contributing.md)**

---

## 🗺️ Roadmap

### ✅ Completado (v0.2.0)
- ✅ RAG Pipeline con LLM
- ✅ Búsqueda híbrida (semántica + keywords)
- ✅ LLM Re-Ranker
- ✅ Taxonomía auto-aprendida
- ✅ Deployment en AWS
- ✅ API simplificada (solo predictor + KB)

### 📅 Planificado (v0.3.0)
- 📅 Análisis de imágenes (visión por computadora)
- 📅 Dashboard de métricas
- 📅 App móvil nativa
- 📅 Multi-idioma (inglés, portugués)

📖 **[Ver roadmap completo →](./docs/01-getting-started/roadmap.md)**

---

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/your-org/fixeatAI/issues)
- **Email:** soporte@fixeat.com
- **Docs:** [Documentación completa](./docs/README.md)

---

## 📄 Licencia

[Especificar licencia]

---

## 👥 Equipo

Desarrollado con ❤️ por el equipo de FIXEAT AI.

**Última actualización:** 2 de febrero de 2026

---

<div align="center">

**[📚 Ver Documentación](./docs/README.md)** • 
**[🚀 Quickstart](./docs/01-getting-started/quickstart.md)** • 
**[📡 API Reference](./docs/02-api/)** • 
**[🔧 Deployment](./docs/05-deployment/deployment-guide.md)**

</div>
