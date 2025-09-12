"""Demo de KB local con Chroma y Sentence-Transformers.

Provee funciones de ingesta y búsqueda (kb_search) usadas por el servidor MCP demo.
"""

from __future__ import annotations

from typing import Any
import os

import chromadb
from sentence_transformers import SentenceTransformer


_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Persistencia opcional mediante variable de entorno (útil en Docker)
_chroma_path = os.getenv("CHROMA_PATH", "/data/chroma")
try:
    _chroma = chromadb.PersistentClient(path=_chroma_path)
except Exception:
    # Fallback a cliente en memoria si la ruta no es válida (entorno local)
    _chroma = chromadb.Client()
_collection = _chroma.get_or_create_collection("kb_tech")


def get_all_documents() -> list[dict[str, Any]]:
    """Obtiene todos los documentos del KB para análisis de taxonomía."""
    try:
        # Obtener todos los documentos de la colección (sin incluir 'ids' explícitamente)
        results = _collection.get(include=["documents", "metadatas"])
        
        documents = []
        for i, doc_id in enumerate(results["ids"]):
            documents.append({
                "id": doc_id,
                "text": results["documents"][i] if i < len(results["documents"]) else "",
                "metadata": results["metadatas"][i] if i < len(results["metadatas"]) else {}
            })
        
        return documents
        
    except Exception as e:
        print(f"Error obteniendo documentos del KB: {e}")
        return []


def ingest_docs(docs: list[dict[str, Any]]) -> None:
    texts = [d["text"] for d in docs]
    embeddings = _model.encode(texts, normalize_embeddings=True).tolist()
    # Chroma requiere metadatas no vacíos; forzamos un valor por defecto
    metadatas = []
    for d in docs:
        md = d.get("metadata") or {"source": "unspecified"}
        # asegurar al menos un atributo
        if isinstance(md, dict) and len(md) == 0:
            md = {"source": "unspecified"}
        metadatas.append(md)

    _collection.add(
        ids=[d["id"] for d in docs],
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )


def kb_search(query: str, top_k: int = 5, where: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    q_emb = _model.encode([query], normalize_embeddings=True).tolist()[0]
    # Filtro por metadatos (opcional)
    kwargs: dict[str, Any] = {"query_embeddings": [q_emb], "n_results": top_k}
    if where and isinstance(where, dict) and len(where) > 0:
        kwargs["where"] = where
    res = _collection.query(**kwargs)
    hits: list[dict[str, Any]] = []
    for i in range(len(res["ids"][0])):
        hits.append(
            {
                "doc_id": res["ids"][0][i],
                "score": float(res["distances"][0][i]),
                "snippet": res["documents"][0][i][:500],
                "metadata": res["metadatas"][0][i],
            }
        )
    return hits


if __name__ == "__main__":
    ingest_docs(
        [
            {"id": "m1", "text": "Manual modelo X: revisar filtro y bomba"},
            {"id": "t1", "text": "Tip técnico: sensor T900 falla con humedad"},
        ]
    )
    print(kb_search("problema de bomba en modelo X", top_k=2))


