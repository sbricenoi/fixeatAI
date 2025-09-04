## Catálogo de Errores y Códigos

### Códigos estándar
- `OK` → 200: éxito.
- `VALIDATION_ERROR` → 422: entradas inválidas.
- `UNAUTHORIZED` → 401: falta/clave inválida.
- `NOT_FOUND` → 404: recurso ausente.
- `RATE_LIMITED` → 429: demasiadas solicitudes.
- `INTERNAL_ERROR` → 500: fallo inesperado.

### Formato de respuesta de error
```json
{
  "traceId": "<uuid>",
  "code": "VALIDATION_ERROR",
  "message": "equipo.modelo es requerido",
  "data": { "errors": [{"path":"equipo.modelo","msg":"requerido"}] }
}
```

### Lineamientos
- Siempre incluir `traceId` y mensaje humano.
- No exponer detalles sensibles en producción.


