## Orquestador IA multi‑agente (OpenAI‑compatible local)

Este documento define cómo reestructuraremos el proyecto para operar con varios "agentes" LLM, cada uno especializado por rol, pudiendo apuntar a un servidor local OpenAI‑compatible (Ollama, LocalAI, vLLM) o a un proveedor cloud.

### Objetivo
- Desacoplar la lógica en agentes especializados (router, DB/text‑to‑SQL, KB/RAG, enlazador, redactor, validador, ops analyst).
- Permitir elegir modelo/base_url por agente (local vs cloud) sin cambiar código de negocio.
- Mantener el estándar de respuestas del microservicio (`traceId`, `code`, `message`, `data`).

### Estado actual (resumen)
- API FastAPI con endpoints (`predict-fallas`, `soporte-tecnico`, `validar-formulario`, `qa`, `ops-analitica`).
- MCP como capa de herramientas: `kb_ingest`, `kb_curate`, `kb_search`, `taxonomy`, y persistencia de KB en Chroma.
- RAG orquestado en `services/orch/rag.py` (con filtros `where`), validación con/sin LLM, y analista de operaciones.

### Propuesta de reestructuración
1) Capa de Agentes (nuevo):
   - Router/Planner: clasifica intención (consulta soporte, reporte, KPI) y define plan de herramientas.
   - DB Agent (Text‑to‑SQL): genera y ejecuta SQL de solo lectura contra la BD (tool `db_query` o conexión MySQL directa).
   - KB Agent: usa MCP `kb_search`/filtros, construye contexto RAG.
   - Synthesizer (Enlazador): fusiona outputs (DB+KB), deduplica, resuelve conflictos y cita fuentes.
   - Writer (Redactor): adapta a canal (WhatsApp/Zendesk), tono y longitud.
   - Validator (Form): valida y mejora redacción de formularios (ya existe `services/orch/validate.py`).
   - Ops Analyst: genera alertas operativas concretas (ya existe `services/orch/ops_analyst.py`).

2) Selección de modelo por agente vía variables
   - Nueva variable `LLM_AGENTS` (JSON) para mapear cada agente a `model`, `base_url` y parámetros:
     ```json
     {
       "router":  {"model": "llama3.1:8b", "base_url": "http://localhost:11434/v1", "temperature": 0},
       "db":      {"model": "qwen2.5-coder:7b", "base_url": "http://localhost:11434/v1", "temperature": 0},
       "kb":      {"model": "llama3.1:8b", "base_url": "http://localhost:11434/v1"},
       "writer":  {"model": "gpt-4o-mini"},
       "validator": {"model": "gpt-4o-mini"},
       "ops":     {"model": "llama3.1:8b", "base_url": "http://localhost:11434/v1"}
     }
     ```
   - Fallback: si un agente no está definido, usar `LLM_MODEL`/`OPENAI_API_KEY` actuales.

3) Extender `services/llm/client.py`
   - Soportar `base_url` y selección por nombre de agente: `LLMClient(agent="router")`.
   - Si `base_url` está definido, inicializar OpenAI client con `base_url` y sin enviar la API key a terceros locales (o una dummy si el servidor la exige).

4) Orquestación
   - Paso 1: Router recibe `{channel, userId, text, context?}` y decide plan: p. ej., `[DB → KB → Synth → Writer]`.
   - Paso 2: Cada agente invoca tools MCP necesarias (`kb_search`, futura `db_query`).
   - Paso 3: Synthesizer fusiona y normaliza a `{answer, sources, actions?}`.
   - Paso 4: Writer adapta formato a canal y corta a límites.
   - Todas las salidas citan fuentes y viajan con `traceId`.

### Cambios en el repositorio
- `services/llm/client.py`: agregar selector por agente, soporte `base_url` (OpenAI‑compatible) y parámetros por agente.
- `services/orch/agents/` (nuevo directorio):
  - `router.py`, `db.py` (text‑to‑sql), `kb.py`, `synth.py`, `writer.py`.
- MCP (tools): agregar `db_query` (solo lectura, allowlist de tablas/campos, límites/paginación).
- Endpoint nuevo (opcional): `/api/v1/orquestar` para canal único; o integrar al `qa`/`soporte` según intención.

### Pasos a seguir (plan de implementación)
1. Variables y cliente LLM
   - Añadir `LLM_AGENTS` y extender `LLMClient` para leer config por agente (`model`, `base_url`, `temperature`, `max_tokens`).
2. Agentes base
   - `kb.py`: wrapper fino sobre `kb_search` con filtros y construcción de contexto.
   - `writer.py`: pragma de formatos (WhatsApp/Zendesk/API) con reglas de truncado.
3. Enrutamiento mínimo
   - `router.py`: clasificación simple por keywords (fase 1) y, si `USE_LLM=true`, function‑calling para plan.
4. DB tool
   - MCP: `POST /tools/db_query` con allowlist (SQL parametrizado), límite de filas y masking de PII.
   - MySQL RDS: `services/db/mysql.py` permite ejecutar SELECT read‑only y obtener el esquema.
   - NL2SQL: el `DBAgent` introspecciona `INFORMATION_SCHEMA` y forma un hint tipo `tabla(col tipo?, ...)` que se pasa al LLM para generar el SELECT.
5. Orquestación demo
   - Endpoint `/api/v1/orquestar` que reciba `{text, canal?, filtros?}` y ejecute: Router → (DB?) → KB → Synth → Writer.
6. Observabilidad
   - Logs JSON por agente, `traceId` encadenado, métricas de tool‑calls y tokens.
7. Seguridad
   - Rate‑limit por canal, sanitización, permisos por tool, auditoría de queries.

### Consideraciones de despliegue (local/ AWS)
- Servidor OpenAI‑compatible (Ollama / LocalAI / vLLM) levantado localmente o en EC2.
- Definir `LLM_AGENTS` en `.env` o en SSM Parameter Store (AWS) para cada ambiente.
- Persistencia KB: bind mount EBS (`/srv/fixeatAI/chroma_store`) → `/data/chroma` (ver `docs/deploy-aws.md`).

### Testing y validación
- Unit tests por agente (inputs → JSON esperado, sin LLM en modo mock).
- E2E: chat de ejemplo → orquestación → respuesta con `sources` y `low_evidence` correctamente gestionado.
- Pruebas anti‑alucinación: KB vacía → listas vacías y `missing_data` poblado.

### Ejemplo de flujo NL2SQL
1) Usuario pregunta: "listar SKUs con stock < 5 en SCL".
2) Router clasifica intención `db`.
3) DBAgent:
   - Introspecciona esquema (o usa `DB_SCHEMA_HINT`).
   - Prompt al LLM con el esquema: devuelve `SELECT sku, stock, bodega FROM inventario WHERE stock < 5 AND bodega = 'SCL' LIMIT 50`.
   - Ejecuta en MySQL (solo lectura) y retorna filas.
4) Writer sintetiza respuesta para el canal.

### Riesgos y mitigaciones
- Alucinación en agentes: prompts estrictos, post‑filtro de fuentes y `low_evidence`.
- Seguridad DB: allowlist estricta, solo lectura, cuota y auditoría.
- Costos/latencia: modelos locales para router/KB, cloud solo para writer si es necesario.

### Roadmap breve
1) Cliente multi‑agente + `LLM_AGENTS` (día 1).
2) Agentes `kb` y `writer` + router simple (día 2).
3) Tool `db_query` + agente `db` (día 3–4).
4) Endpoint `/api/v1/orquestar` + métricas/logs (día 5).
5) Piloto con un canal (Zendesk/WhatsApp) (día 6+).


