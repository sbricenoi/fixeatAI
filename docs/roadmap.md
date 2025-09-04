## Roadmap del Microservicio IA

### Fase 0 — Base operativa (listo / en curso)
- Documentación principal (arquitectura, API, datos, flujo, Docker).
- Esqueleto de código (API, MCP, KB) y tooling (pyproject, Makefile).
- Docker/Compose funcional con persistencia de KB.

Entregables:
- Repositorio ejecutando `docker compose up -d` y endpoints mock operativos.

### Fase 1 — MVP funcional
- Implementar pipeline RAG básico (NLP simple + kb_search) en `predict-fallas` y `soporte-tecnico`.
- Validaciones iniciales en `validar-formulario` con reglas.
- Observabilidad mínima (logs JSON con traceId) y catálogo de errores.

Entregables y criterios:
- Respuestas con `fuentes` significativas desde KB.
- 70% cobertura en lógica de validación.
- Guías actualizadas en `docs/quickstart.md`.

### Fase 2 — Integración IA/Orquestación
- Orquestador configurable (LangChain/LlamaIndex/custom) con pasos multi-tool.
- Nuevas tools MCP (inventario, ticketing) mock y luego reales.
- Parámetros RAG ajustables (`docs/rag-config.md`) con reranking opcional.

Entregables y criterios:
- Flujos reproducibles con configuración por entorno.
- Métricas por tool (latencia, errores) visibles.

### Fase 3 — Calidad, seguridad y MLOps
- Linter/format (Ruff/Black/Isort) y MyPy gradual en `app/` y `services/`.
- Endurecimiento de seguridad (prompt-injection, secretos, roles).
- MLOps: dataset spec, evaluación y registro de modelos.

Entregables y criterios:
- Pipeline CI (lint, test, build) verde.
- Métricas de calidad de respuesta definidas y monitoreadas.

### Fase 4 — Producción y escalado
- Despliegue en entorno gestionado (K8s o equivalente), health checks.
- Observabilidad completa (OTel), SLOs/alertas, runbooks afinados.
- Optimización de rendimiento y costos.

Entregables y criterios:
- SLOs definidos (latencia p95, error rate) y alertas.
- Procedimientos de rollback y reindexación documentados.

### Gestión y gobernanza
- Convenciones de commits/PRs, DoD por tipo de tarea.
- Revisión periódica de la KB y reindexación.


