## Manual de configuración y ejecución local

### 1) Requisitos
- macOS/Linux, Python 3.11
- `make`, `git`

### 2) Setup del proyecto
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### 3) Configuración de entorno
Crear `.env` en la raíz del repo:
```
OPENAI_API_KEY=sk-...tu_clave...
USE_LLM=true
MCP_SERVER_URL=http://localhost:7070
X_TRACE_ID_HEADER=X-Trace-Id
```

El `Makefile` está configurado para cargar `.env` automáticamente.

### 4) Levantar servicios
- Servidor MCP (tools: `kb_search`, `kb_ingest`):
```bash
make mcp
```

- API FastAPI (endpoints `/api/v1/*`):
```bash
make run
```

### 5) Ingesta de conocimiento (KB)
Ejemplos de ingesta al MCP:

- Texto directo:
```bash
curl -s -X POST http://127.0.0.1:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{"docs":[{"id":"d1","text":"Manual X: revisar filtro de bomba","metadata":{"source":"manual"}}]}'
```

- URL pública:
```bash
curl -s -X POST http://127.0.0.1:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{"urls":["https://example.com"]}'
```

- Archivo base64 (PDF/DOCX/XLSX):
```bash
BASE64=$(base64 -i manual.pdf)
curl -s -X POST http://127.0.0.1:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{"files":[{"id":"pdf1","filename":"manual.pdf","mime_type":"application/pdf","file_base64":"'"$BASE64"'"}]}'
```

Si recibes 403 en URLs, incluye `url_headers` con cookies reales del navegador.

### 6) Probar endpoints de la API
- Predicción de fallas (LLM si `USE_LLM=true`, sino heurística):
```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' -H 'X-Trace-Id: demo-123' \
  -d '{
    "cliente": {"id": "c1"},
    "equipo": {"marca": "X", "modelo": "Y"},
    "descripcion_problema": "falla en bomba modelo X",
    "tecnico": {"id":"t1","experiencia_anios":5,"visitas_previas":3}
  }' | jq
```

- QA libre con RAG:
```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/qa \
  -H 'Content-Type: application/json' -H 'X-Trace-Id: demo-123' \
  -d '{"pregunta":"¿Cómo revisar la bomba del modelo X?"}' | jq
```

- Validación de formulario:
```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/validar-formulario \
  -H 'Content-Type: application/json' -H 'X-Trace-Id: demo-123' \
  -d '{
    "cliente": {"id": "c1"},
    "equipo": {"marca": "X", "modelo": "Y"},
    "descripcion_problema": "texto",
    "campos_formulario": {"fecha_instalacion": "2022-01-01"}
  }' | jq
```

### 7) Troubleshooting
- 404 al llamar `predict-fallas` en puerto 7070 → estás golpeando MCP; usa `http://127.0.0.1:8000`.
- `OPENAI_API_KEY no configurada` → define en `.env` o exporta en shell.
- 403 al ingestar URL → anti-scraping; usa `url_headers` con cookies.
- Puerto 7070 ocupado → cambia puerto o detén proceso conflictivo.

### 8) Seguridad
- No comitees `.env`.
- Limita tokens y temperatura para controlar costos/derivas.
- Sanitiza entradas y valida tipos en payloads.


