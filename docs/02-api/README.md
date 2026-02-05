# 📡 API Documentation - FIXEAT AI

Documentación completa de la API del predictor de fallas.

---

## 📚 Documentos Disponibles

### [API Reference](./api.md)
Documentación completa de todos los endpoints.

**Incluye:**
- `/api/v1/predict-fallas` - Predicción principal
- `/api/v1/soporte-tecnico` - Soporte técnico
- `/api/v1/qa` - Q&A general
- `/api/v1/validar-formulario` - Validación
- Ejemplos de uso para cada endpoint

---

### [Endpoints Reference](./endpoints-reference.md) ⚡
Referencia rápida de endpoints (cheat sheet).

**Formato compacto con:**
- URLs y métodos HTTP
- Request/Response examples
- Quick tips
- Niveles de confidence

---

### [Schema de Respuesta](./schema-respuesta.md) 📋
Estructura detallada de las respuestas JSON.

**Incluye:**
- Wrapper estándar (`traceId`, `code`, `message`, `data`)
- Estructura de `fallas_probables`
- Estructura de `pasos` (seguridad, diagnóstico, reparación)
- Estructura de `contextos` con LLM Re-Ranker
- `signals` y `quality_metrics`
- Interfaces TypeScript
- Ejemplos completos

---

### [Integration Guide](./integration-guide.md) 🔌
Guía para integrar el predictor con tu aplicación.

**Incluye:**
- Integración en frontend (React, Vue, Angular)
- Integración en backend (Node.js, Python, PHP)
- Integración en mobile (iOS, Android)
- Manejo de errores
- Best practices

---

## 🌐 Servidor Productivo

**Base URL:** `http://18.220.79.28:8000`

**Endpoints principales:**
- Health: `http://18.220.79.28:8000/health`
- Predict Fallas: `http://18.220.79.28:8000/api/v1/predict-fallas`
- MCP: `http://18.220.79.28:7070`

---

## 🚀 Quick Start

### Verificar Health

```bash
curl http://18.220.79.28:8000/health
```

**Respuesta esperada:**
```json
{"status": "ok"}
```

---

### Predicción de Falla

```bash
curl -X POST http://18.220.79.28:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente": {"id": "c001"},
    "equipo": {"marca": "Rational", "modelo": "Icombi Pro"},
    "descripcion_problema": "El horno no calienta",
    "tecnico": {"id": "t001", "experiencia_anios": 5}
  }'
```

---

## 📊 Niveles de Confidence

| Rango | Interpretación | Causa Típica |
|-------|----------------|--------------|
| **0.85+** | Muy Alta | Descripción muy detallada con código de error |
| **0.70-0.84** | Alta | Código de error o síntomas claros |
| **0.50-0.69** | Media | Descripción clara pero general |
| **0.30-0.49** | Baja | Información vaga |
| **< 0.30** | Muy Baja | Información insuficiente |

---

[← Volver al índice principal](../README.md)
