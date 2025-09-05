## Microservicio IA — FixeatAI

Documentación inicial del microservicio de IA para diagnóstico técnico, sugerencia de repuestos y validación de formularios.

### Documentación
- Arquitectura: `docs/arquitectura.md`
- API: `docs/api.md`
- Contratos de datos: `docs/datos.md`
- Integración MCP/Orquestadores: `docs/mcp-orquestacion.md`
- Quickstart local (KB, MCP, FastAPI): `docs/quickstart.md`
- Docker/Compose: `docs/docker.md`
- Flujo operativo y de desarrollo: `docs/flujo.md`
- Roadmap: `docs/roadmap.md`
 - LLM + RAG: `docs/llm.md`
 - Entorno y configuración: `docs/entorno-configuracion.md`
 - Manual de ejecución: `docs/runbook-local.md`
 - Despliegue AWS + Docker: `docs/deploy-aws.md`
 - Estructura del repositorio (guía no técnica): `docs/estructura-repo.md`

### Roadmap (MVP)
1) Definir contratos y endpoints (listo).
2) Prototipo FastAPI con endpoints mock y esquema de respuesta estándar (`traceId`, `code`, `message`, `data`).
3) Integración básica de NLP y reglas.
4) Conectar a MCPs/Vector DB para KB.
5) Observabilidad (logs/tracing) y hardening de seguridad.

### Stack
- Python 3.11, FastAPI
- Opcional: LangChain/LlamaIndex, OpenTelemetry, pgvector/FAISS


