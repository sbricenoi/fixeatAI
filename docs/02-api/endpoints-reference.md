# 🚀 QUICK REFERENCE - Predictor de Fallas API

## 🌐 Servidor Productivo
```
IP: 18.220.79.28
Puerto: 8000
Base URL: http://18.220.79.28:8000
```

## 📡 Endpoints

### Health Check
```bash
curl http://18.220.79.28:8000/health
```

### Predict Fallas (Principal)
```bash
curl -X POST http://18.220.79.28:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente": {"id": "c001"},
    "equipo": {"marca": "Rational", "modelo": "Icombi Pro"},
    "descripcion_problema": "descripción detallada del problema",
    "tecnico": {"id": "t001", "experiencia_anios": 5}
  }'
```

## 📊 Respuesta Típica
```json
{
  "code": "OK",
  "data": {
    "fallas_probables": [{
      "falla": "descripción",
      "confidence": 0.75,
      "repuestos_sugeridos": ["repuesto1", "repuesto2"],
      "herramientas_sugeridas": ["herramienta1"],
      "pasos": [
        {"orden": 1, "descripcion": "...", "tipo": "seguridad"}
      ]
    }],
    "signals": {
      "kb_hits": 10,
      "llm_used": true
    }
  }
}
```

## ⚡ Tips

- **Tiempo de respuesta**: 25-50 segundos
- **Mejor confidence**: Descripciones detalladas con síntomas específicos
- **Siempre incluye**: Protocolos de seguridad en los pasos
- **Guardar**: `traceId` para soporte

## 📈 Niveles de Confidence
- **0.85+** 🟢 Muy Alta (descripción muy detallada)
- **0.70-0.84** 🟢 Alta (código de error específico)
- **0.50-0.69** 🟡 Media (descripción clara)
- **0.30-0.49** 🟡 Baja (información vaga)

## 🔍 Tipos de Pasos
- `seguridad` - Protocolos de seguridad
- `diagnostico` - Inspección y pruebas
- `reparacion` - Acciones de reparación
