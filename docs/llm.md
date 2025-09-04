## Integración LLM + RAG

### Resumen
- Recuperamos contexto desde la KB (`kb_search` vía MCP) y lo enviamos al LLM con un prompt que obliga un JSON estructurado.
- El servicio puede operar en modo heurístico (sin LLM) o con LLM según `USE_LLM`.

### Variables de entorno
- `USE_LLM` = true|false (default: true)
- `OPENAI_API_KEY` = clave del proveedor (obligatoria si `USE_LLM=true`)
- `LLM_MODEL` = modelo (default: `gpt-4o-mini`)
- `LLM_TEMPERATURE` (default: 0.1)
- `LLM_MAX_TOKENS` (default: 800)

### Flujo en `/api/v1/predict-fallas`
1. `kb_search` (top_k 5) con filtros `where` por entidad (ej. `brand`, `model`) → se arma un contexto: `[source:doc_id] snippet` por línea.
2. Prompt al LLM con esquema:
```json
{
  "fallas_probables": [{"falla": "string", "confidence": 0.0, "rationale": "string"}],
  "repuestos_sugeridos": ["string"],
  "herramientas_sugeridas": ["string"],
  "pasos": [{"orden": 1, "descripcion": "string", "tipo": "diagnostico|reparacion"}],
  "feedback_coherencia": "string"
}
```
3. Se parsea la respuesta con tolerancia a texto extra (se intenta extraer el primer bloque JSON); se añaden `fuentes`.
4. La API devuelve el estándar `traceId`, `code`, `message`, `data`.

### Endpoint de QA
- `POST /api/v1/qa` → pregunta libre con RAG y LLM, devuelve JSON con `fuentes`.

### Notas
- No se envían documentos completos, solo snippets de `kb_search`.
- Para URLs bloqueadas por anti-scraping, usar `url_headers` con cookies reales o subir archivos por `file_base64`.
- Costos/latencias del LLM están controlados por `LLM_MAX_TOKENS` y `LLM_TEMPERATURE`.
 - El prompt exige JSON en español, con citas de fuentes en cada `rationale`.


