## Quickstart — KB, MCP y FastAPI en local

Este quickstart levanta una KB local (Chroma), un servidor MCP de ejemplo con `kb_search`, y un microservicio FastAPI con endpoints mock que responden con `traceId`, `code`, `message`, `data`.

### 1) Preparar entorno
Requisitos: Python 3.11, `pip`, `venv`.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### 2) KB local: ingesta y búsqueda
Archivo sugerido: `services/kb/demo_kb.py`

```python
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chroma = chromadb.Client()
collection = chroma.get_or_create_collection("kb_tech")

def ingest_docs(docs):
    texts = [d["text"] for d in docs]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    collection.add(
        ids=[d["id"] for d in docs],
        embeddings=embeddings,
        documents=texts,
        metadatas=[d.get("metadata", {}) for d in docs],
    )

def kb_search(query: str, top_k: int = 5):
    q_emb = model.encode([query], normalize_embeddings=True).tolist()[0]
    res = collection.query(query_embeddings=[q_emb], n_results=top_k)
    hits = []
    for i in range(len(res["ids"][0])):
        hits.append({
            "doc_id": res["ids"][0][i],
            "score": float(res["distances"][0][i]),
            "snippet": res["documents"][0][i][:500],
            "metadata": res["metadatas"][0][i],
        })
    return hits

if __name__ == "__main__":
    ingest_docs([
        {"id": "m1", "text": "Manual modelo X: revisar filtro y bomba"},
        {"id": "t1", "text": "Tip técnico: sensor T900 falla con humedad"},
    ])
    print(kb_search("problema de bomba en modelo X", top_k=2))
```

Ejecutar demo KB:
```bash
python services/kb/demo_kb.py
```

### 3) Servidor MCP (mínimo) con `kb_search`
Archivo sugerido: `mcp/server_demo.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel
from services.kb.demo_kb import kb_search

app = FastAPI(title="MCP Demo Server")

class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/tools/kb_search")
def tool_kb_search(req: KBSearchRequest):
    hits = kb_search(req.query, req.top_k)
    return {"hits": hits}

# Ejecutar: uvicorn mcp.server_demo:app --reload --port 7000
```

Levantar servidor MCP demo:
```bash
make mcp
```

Ingestar documentos/URLs vía HTTP:
```bash
curl -s -X POST http://localhost:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "docs": [
      {"id": "m3", "text": "Manual modelo Z: revisar correas"}
    ],
    "urls": ["https://example.com"]
  }'
```

### 4) FastAPI (endpoints con heurística y LLM opcional)
Archivo sugerido: `app/main.py`

```python
import uuid
from fastapi import FastAPI, Header
from pydantic import BaseModel
import requests

app = FastAPI(title="FixeatAI Microservicio IA", version="0.1.0")

def wrap_response(data, message="OK", code="OK", trace_id: str | None = None):
    return {
        "traceId": trace_id or str(uuid.uuid4()),
        "code": code,
        "message": message,
        "data": data,
    }

class PredictRequest(BaseModel):
    cliente: dict
    equipo: dict
    descripcion_problema: str
    tecnico: dict

@app.post("/api/v1/predict-fallas")
def predict_fallas(req: PredictRequest, x_trace_id: str | None = Header(default=None, alias="X-Trace-Id")):
    # Demo: invoca MCP kb_search como contexto
    try:
        hits = requests.post("http://localhost:7000/tools/kb_search", json={"query": req.descripcion_problema, "top_k": 3}, timeout=5).json().get("hits", [])
    except Exception:
        hits = []
    data = {
        "fallas_probables": [
            {"falla": "Bomba obstruida", "confidence": 0.8, "rationale": "coincidencias en KB"}
        ],
        "repuestos_sugeridos": ["Bomba A123"],
        "herramientas_sugeridas": ["Multímetro"],
        "fuentes": [h.get("doc_id") for h in hits],
    }
    return wrap_response(data=data, message="Predicción generada", code="OK", trace_id=x_trace_id)

class SoporteRequest(BaseModel):
    cliente: dict
    equipo: dict
    descripcion_problema: str

@app.post("/api/v1/soporte-tecnico")
def soporte_tecnico(req: SoporteRequest, x_trace_id: str | None = Header(default=None, alias="X-Trace-Id")):
    pasos = [
        {"orden": 1, "descripcion": "Verificar alimentación eléctrica", "tipo": "diagnostico"},
        {"orden": 2, "descripcion": "Medir resistencia en borne X", "tipo": "diagnostico"},
    ]
    return wrap_response(data={"pasos": pasos}, message="Secuencia generada", code="OK", trace_id=x_trace_id)

class ValidarRequest(BaseModel):
    cliente: dict
    equipo: dict
    descripcion_problema: str
    campos_formulario: dict

@app.post("/api/v1/validar-formulario")
def validar_formulario(req: ValidarRequest, x_trace_id: str | None = Header(default=None, alias="X-Trace-Id")):
    data = {
        "es_valido": True,
        "inconsistencias": [],
        "correcciones_sugeridas": {},
        "feedback_coherencia": "OK"
    }
    return wrap_response(data=data, message="Validación completada", code="OK", trace_id=x_trace_id)

# Ejecutar: uvicorn app.main:app --reload --port 8000
```

Levantar FastAPI:
```bash
make run
```

### 5) Variables y .env
Crear `.env` en la raíz:
```
OPENAI_API_KEY=sk-...tu_clave...
USE_LLM=true
MCP_SERVER_URL=http://localhost:7070
```

### 6) Probar con curl
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

Si ves `traceId`, `code`, `message`, `data` en la respuesta, la canalización está operativa.


