## Observabilidad

### Logging
- Formato JSON, nivel por `LOG_LEVEL`.
- Incluir `traceId` en cada evento.

### Métricas
- Latencia por endpoint, tasa de error, QPS.
- Contadores por tool MCP (éxitos/errores/timeout).

### Trazas
- OpenTelemetry (futuro): span por request y por llamada a MCP/KB.


