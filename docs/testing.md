## Estrategia de Testing

### Tipos
- Unitarios: lógica pura (NLP helpers, validaciones, utilitarios).
- Integración: endpoints FastAPI con MCP/KB mockeados.
- Contratos: esquemas de request/response según `docs/datos.md`.
- E2E (smoke): recorrido mínimo en local con Quickstart.

### Herramientas
- `pytest`, `httpx`, `pytest-cov`.

### Cobertura
- Objetivo inicial: 70% líneas; crítico: 90% en validación.

### Ejecución
```bash
make test
```


