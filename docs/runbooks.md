## Runbooks Operativos

### Endpoint lento o con errores
1. Revisar métricas de latencia/error por `traceId`.
2. Inspeccionar logs y trazas; identificar llamadas MCP con timeout.
3. Ajustar timeouts o degradar funcionalidad (respuestas sin KB).

### MCP no responde
1. Verificar health del servidor MCP.
2. Fallback a respuestas sin herramientas o usar caché local.

### Reindexación de KB
1. Ejecutar proceso de ingesta canary.
2. Validar calidad (precision@k) y promover índice.


