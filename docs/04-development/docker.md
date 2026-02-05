## Docker / Compose

### Build e inicio
```bash
docker compose build
docker compose up -d
```

Servicios:
- `mcp`: expone `kb_search` en `:7070` (mapeado al 7000 interno), persiste KB en volumen `chroma_data` (`/data/chroma`).
- `api`: FastAPI en `:8000`, consulta MCP por hostname `mcp`.

### Probar
```bash
curl -s -X POST http://localhost:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' -H 'X-Trace-Id: demo-123' \
  -d '{
    "cliente": {"id": "c1"},
    "equipo": {"marca": "X", "modelo": "Y"},
    "descripcion_problema": "falla en bomba modelo X",
    "tecnico": {"id":"t1","experiencia_anios":5,"visitas_previas":3}
  }' | jq
```

Deberías ver `traceId`, `code`, `message`, `data` y, tras insertar documentos en la KB, `fuentes` con ids.

### Variables útiles
- `ROLE`: `api` o `mcp` (controla el proceso lanzado en el contenedor).
- `MCP_SERVER_URL`: URL que usa `api` para llamar a MCP (por defecto `http://mcp:7000`).
- `CHROMA_PATH`: ruta de persistencia de Chroma (por defecto `/data/chroma`).
 - `OPENAI_API_KEY`: define tu clave en `.env` y referencia en `docker-compose.yml` con `${OPENAI_API_KEY}`.

Ejemplo `.env` para Compose:
```
OPENAI_API_KEY=sk-...tu_clave...
```

### Detener
```bash
docker compose down
```


