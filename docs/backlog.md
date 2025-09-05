## Backlog de mejoras (priorizado)

- Curaduría y Taxonomía
  - Aprendizaje continuo de taxonomías desde la KB (alias/canónicos).
  - Extracción automática de entidades desde texto (brand/model/category/zona/parte).
  - Reglas de quarantine configurables (longitud mínima, calidad, idioma) y vista de revisión.
  - Deduplicación: fingerprint + similitud (near-duplicates) y merges.

- Búsqueda y RAG
  - Re‑ranker (cross‑encoder) para filtrar top‑50 → top‑5.
  - Cache de contexto por consulta (reduce latencia/costo).
  - Señales ampliadas: cobertura de fuentes, diversidad, contradicciones.
  - Prompts por dominio (mantenimiento, médico, soporte) con esquemas de salida distintos.

- Endpoints y contratos
  - `qa` con `filtros` genéricos → mapeo directo a `where`.
  - Perfiles de respuesta configurables (ej. "mantenimiento" vs "médico").
  - Endpoint de planificación de repuestos (con inventario externo).

- Observabilidad
  - Métricas: kb_hits, low_evidence, tokens/costo, latencia por fase.
  - Trazabilidad de ingesta (lineage: source_ref, fingerprint, versión).
  - Logs estructurados y panel básico (Grafana) en local.

- Seguridad y gobierno
  - API key/JWT, scopes, rate‑limit.
  - Sanitización entrada/salida, PII y redacción segura.
  - Auditoría de ingestas y backups de la KB.

- Integraciones de ingesta
  - ETL desde BD (watermark `updated_at`), colas asíncronas.
  - Conectores S3/SharePoint/Drive.

- Testing y calidad
  - Tests E2E de ingesta→búsqueda→RAG (URLs/archivos/BD).
  - Datasets sintéticos para regresión de prompts.
  - Pruebas de resiliencia (timeouts, 403/429, reintentos con backoff).


