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

#### Multi‑agente (opcional)
- `LLM_AGENTS`: JSON para configurar modelo/base_url por agente (router, db, kb, writer, etc.).
  Ejemplo:
  ```json
  {
    "router": {"model": "gpt-4o-mini"},
    "db": {"model": "gpt-4o-mini"},
    "writer": {"model": "gpt-4o-mini"}
  }
  ```

#### Base de datos MySQL (RDS)
- `MYSQL_HOST`: endpoint de RDS
- `MYSQL_PORT`: puerto (default: 3306)
- `MYSQL_USER`: usuario de solo lectura
- `MYSQL_PASSWORD`: contraseña
- `MYSQL_DATABASE`: base de datos
- `DB_SCHEMA_HINT` (opcional): pista de esquema si no quieres introspección en runtime, ej.
  `inventario(sku,stock,bodega); visitas(ticket_id,equipo_model,issue)`

### Archivo .env (uso local)
Ejemplo mínimo de `.env` en la raíz del repo:

```
OPENAI_API_KEY=sk-...tu_clave...
USE_LLM=true
MCP_SERVER_URL=http://localhost:7070
X_TRACE_ID_HEADER=X-Trace-Id
LLM_MODEL=gpt-4o-mini

# Multi‑agente (opcional)
LLM_AGENTS={"router":{"model":"gpt-4o-mini"},"db":{"model":"gpt-4o-mini"},"writer":{"model":"gpt-4o-mini"}}

# MySQL RDS (si usas NL2SQL y ejecución real)
MYSQL_HOST=tu-rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=usuario_ro
MYSQL_PASSWORD=******
MYSQL_DATABASE=mi_db
# Alternativa a introspección automática
# DB_SCHEMA_HINT=inventario(sku,stock,bodega); visitas(ticket_id,equipo_model,issue)
```

El `Makefile` carga automáticamente `.env` al ejecutar `make run` y `make mcp`.

### Perfiles
- Local: mocks, Chroma embebido, logs debug.
- Dev/Staging: pgvector, tracing OTel, autenticación.
- Prod: secretos gestionados, escalado horizontal, observabilidad completa.

### Carga de configuración
- 12-Factor App. Variables por entorno, `.env` en local solo.
- Validación al inicio. Falla rápida si falta una clave crítica.


