## Configuración RAG (Retrieval-Augmented Generation)

### Pipeline
- Ingesta → Chunking → Embeddings → Indexación → Consulta → Fusión y generación.

### Parámetros sugeridos
- Chunk size: 800-1200 chars; overlap: 100-200.
- Modelo de embeddings: `sentence-transformers/all-MiniLM-L6-v2` (dev) / más robusto en prod.
- `top_k`: 3-8; reranking opcional (Cross-Encoder).
- Contexto máximo a LLM: 2-4k tokens efectivos.

### Reindexación
- Batch incremental, versionado de colecciones, pruebas canary.


