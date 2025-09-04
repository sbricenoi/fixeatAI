## Entorno y Configuración

### Variables de entorno (principales)
- `ENV`: local|dev|staging|prod (default: local)
- `LOG_LEVEL`: info|debug|warning|error (default: info)
- `X_TRACE_ID_HEADER`: nombre de cabecera para trazas (default: X-Trace-Id)
- `MCP_SERVER_URL`: URL del servidor MCP (default: http://localhost:7070)
- `ORCH_PROVIDER`: langchain|llamaindex|custom (default: custom)
- `VECTOR_DB_URL`: conexión a vector DB (si aplica)
- `OPENAI_API_KEY`: clave para LLM (opcional en mock)
 - `USE_LLM`: habilita LLM (true|false, default: true)
 - `LLM_MODEL`: modelo LLM (default: gpt-4o-mini)
 - `LLM_TEMPERATURE`: float (default: 0.1)
 - `LLM_MAX_TOKENS`: entero (default: 800)

### Archivo .env (uso local)
Ejemplo mínimo de `.env` en la raíz del repo:

```
OPENAI_API_KEY=sk-...tu_clave...
USE_LLM=true
MCP_SERVER_URL=http://localhost:7070
X_TRACE_ID_HEADER=X-Trace-Id
```

El `Makefile` carga automáticamente `.env` al ejecutar `make run` y `make mcp`.

### Perfiles
- Local: mocks, Chroma embebido, logs debug.
- Dev/Staging: pgvector, tracing OTel, autenticación.
- Prod: secretos gestionados, escalado horizontal, observabilidad completa.

### Carga de configuración
- 12-Factor App. Variables por entorno, `.env` en local solo.
- Validación al inicio. Falla rápida si falta una clave crítica.


