## MCP Tools Specification

### kb_search
Input
```json
{ "query": "string", "top_k": 5, "where": {"brand": {"$eq": "ACME"}, "model": {"$eq": "T900"}} }
```
Output
```json
{ "hits": [{"doc_id":"string","score":0.0,"snippet":"string","metadata":{}}] }
```
Notas:
- `where` es opcional y filtra por metadatos de la colección (Chroma). Operadores soportados: `$eq`, `$contains`, `$in` (según backend).
- Recomendado: etiquetar `metadata` al ingerir (`brand`, `model`, `category`, `source`).

### inventory_lookup
Input: `{ "modelo": "string", "repuesto": "string" }`
Output: `{ "disponible": true, "sku": "string", "eta_dias": 0 }`

### ticket_update
Input: `{ "ticket_id": "string", "comentario": "string" }`
Output: `{ "ok": true }`

### kb_ingest
Permite ingresar documentos en texto y/o URLs (scrapeo HTML básico) a la KB. Puede habilitar curación automática.

Input
```json
{
  "docs": [
    { "id": "string?", "text": "string", "metadata": {} },
    { "filename": "manual.pdf", "file_base64": "...", "mime_type": "application/pdf" },
    { "filename": "manual.docx", "file_base64": "..." },
    { "filename": "tabla.xlsx", "file_base64": "..." }
  ],
  "urls": ["https://.../manual.html", "https://.../manual.pdf", "https://.../tabla.xlsx"],
  "auto_curate": true
}
```
Output
```json
{ "ingested": 3, "from_urls": 1, "curated": true, "stats": {"input": 5, "curated": 3, "quarantine": 2} }
```
### kb_curate
Normaliza, enriquece, fragmenta y puntúa contenido para la KB sin escribirlo. Sirve para validar/previzualizar cargas, o como paso previo a `kb_ingest`.

Input
```json
{
  "docs": [{ "id": "raw-1", "text": "...", "metadata": {"source":"manual_pdf","brand":"ACME","model":"T900"} }],
  "urls": ["https://example.com/manual.html"],
  "url_headers": {"Cookie": "..."}
}
```
Output
```json
{
  "docs": [
    { "id": "acme-t900#c0", "text": "...chunk...", "metadata": {"brand":"ACME","model":"T900","chunk_index":0,"fingerprint":"sha256:...","quality_score":0.9} }
  ],
  "quarantine": [{"id":"acme-t900#cN","reason":"low_quality_or_too_short"}],
  "stats": {"input": 2, "curated": 1, "quarantine": 1}
}
```

Notas
- El esquema de salida sigue el “CanonicalDoc” (ver docs/llm.md o docs/arquitectura.md).
- `quality_score` y `fingerprint` ayudan a deduplicar, revisar y gobernar el contenido.

### Límites y tiempos
- Timeout por tool: 5s (dev), 2s (prod) con reintentos controlados.


