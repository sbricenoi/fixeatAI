## API del Microservicio de IA

Base URL: `/api/v1`

### Convenciones
- Autenticación: `Authorization: Bearer <token>` (opcional según despliegue).
- Trazabilidad: se acepta `X-Trace-Id` en el request y se devuelve como `traceId` en la respuesta. Si no se envía, el servicio generará un UUID.
- Respuesta estándar: todas las respuestas devuelven `traceId`, `code`, `message`, `data`.

```json
{
  "traceId": "<uuid>",
  "code": "OK",
  "message": "<mensaje de estado>",
  "data": {}
}
```

### Códigos de `code`
- `OK`: operación exitosa
- `VALIDATION_ERROR`: error de validación de entrada
- `NOT_FOUND`: recurso no encontrado (si aplica)
- `INTERNAL_ERROR`: error interno no controlado

---

### POST /predict-fallas
Retorna diagnóstico con fallas probables, % de confianza, repuestos y herramientas sugeridas.

Headers
- `Content-Type: application/json`
- `Authorization: Bearer <token>` (si aplica)
- `X-Trace-Id: <uuid>` (opcional)

Request Body
```json
{
  "cliente": { "id": "string", "historial_visitas": ["2023-01-10", "2024-05-11"] },
  "equipo": { "marca": "string", "modelo": "string", "fecha_instalacion": "YYYY-MM-DD", "historial_fallas": ["COD_F1", "COD_F2"] },
  "descripcion_problema": "texto libre",
  "tecnico": { "id": "string", "experiencia_anios": 5, "visitas_previas": 12 }
}
```

Response 200
```json
{
  "traceId": "f7a4d0b8-4c7b-4a67-9c64-1e1d9a41f9b1",
  "code": "OK",
  "message": "Predicción generada",
  "data": {
    "fallas_probables": [
      { "falla": "Bomba obstruida", "confidence": 0.83, "rationale": "síntoma X, modelo Y" },
      { "falla": "Sensor de temperatura defectuoso", "confidence": 0.64 }
    ],
    "repuestos_sugeridos": ["Bomba A123", "Sensor T-900"],
    "herramientas_sugeridas": ["Multímetro", "Llave 12mm"]
  }
}
```

Response 422 (VALIDATION_ERROR)
```json
{
  "traceId": "<uuid>",
  "code": "VALIDATION_ERROR",
  "message": "campo equipo.modelo es requerido",
  "data": { "errors": [{"path": "equipo.modelo", "msg": "requerido"}] }
}
```

---

### POST /soporte-tecnico
Devuelve pasos recomendados de diagnóstico y reparación.

Headers: igual a `/predict-fallas`.

Request Body
```json
{
  "cliente": { "id": "string" },
  "equipo": { "marca": "string", "modelo": "string" },
  "descripcion_problema": "texto libre",
  "contexto": { "nivel_detalle": "basico|intermedio|avanzado" }
}
```

Response 200
```json
{
  "traceId": "<uuid>",
  "code": "OK",
  "message": "Secuencia generada",
  "data": {
    "pasos": [
      { "orden": 1, "descripcion": "Verificar alimentación eléctrica", "tipo": "diagnostico" },
      { "orden": 2, "descripcion": "Medir resistencia en borne X", "tipo": "diagnostico" },
      { "orden": 3, "descripcion": "Reemplazar fusible F1 si fuera necesario", "tipo": "reparacion" }
    ]
  }
}
```

---

### POST /validar-formulario
Valida la coherencia de lo ingresado y sugiere correcciones.

Request Body
```json
{
  "cliente": { "id": "string" },
  "equipo": { "marca": "string", "modelo": "string", "fecha_instalacion": "YYYY-MM-DD" },
  "descripcion_problema": "texto libre",
  "campos_formulario": {
    "fecha_visita": "YYYY-MM-DD",
    "lectura_temperatura": 12.3,
    "codigo_falla": "F-001"
  }
}
```

Response 200
```json
{
  "traceId": "<uuid>",
  "code": "OK",
  "message": "Validación completada",
  "data": {
    "es_valido": true,
    "inconsistencias": [
      { "campo": "lectura_temperatura", "tipo": "rango", "detalle": "fuera de rango esperado 2-8C" }
    ],
    "correcciones_sugeridas": {
      "lectura_temperatura": 6.5
    },
    "feedback_coherencia": "La descripción concuerda con el modelo y el historial"
  }
}
```

---

### Errores comunes
- 401 Unauthorized: token inválido o ausente.
- 404 Not Found: recurso no encontrado (si aplica).
- 429 Too Many Requests: límite de rate alcanzado.
- 500 Internal Server Error: error inesperado.

### Versionado y Deprecación
- Prefijo `/api/v1`. Cambios incompatibles introducen `/api/v2`.
- Cabecera `Deprecation` para anunciar endpoints legados cuando aplique.


