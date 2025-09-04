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
Permite ingresar documentos en texto y/o URLs (scrapeo HTML básico) a la KB.

Input
```json
{
  "docs": [
    { "id": "string?", "text": "string", "metadata": {} },
    { "filename": "manual.pdf", "file_base64": "...", "mime_type": "application/pdf" },
    { "filename": "manual.docx", "file_base64": "..." },
    { "filename": "tabla.xlsx", "file_base64": "..." }
  ],
  "urls": ["https://.../manual.html", "https://.../manual.pdf", "https://.../tabla.xlsx"]
}
```
Output
```json
{ "ingested": 3, "from_urls": 1 }
```

### Límites y tiempos
- Timeout por tool: 5s (dev), 2s (prod) con reintentos controlados.


