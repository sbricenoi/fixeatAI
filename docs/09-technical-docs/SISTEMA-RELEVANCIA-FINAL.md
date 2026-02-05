# Sistema de Relevancia sin Alucinaciones

## ✅ **IMPLEMENTACIÓN COMPLETADA**

## 📊 **¿Qué se hizo?**

### 1. **Scoring de Relevancia Objetivo** (`services/kb/relevance_scorer.py`)
```python
def calculate_relevance(hit, query, target_model, query_error_codes) -> Dict:
    """
    Calcula relevancia basándose en datos REALES, no alucinaciones:
    - Base: Score de búsqueda (verificable)
    - +20%: Match exacto de código de error
    - +15%: Match de modelo (ej. iCombi Classic)
    - +15%: Documento de troubleshooting
    - +10%: Keyword strength
    
    Retorna:
    - relevance_score: 0-100 (porcentaje)
    - confidence_label: "Muy Alta", "Alta", "Media", "Baja"
    - confidence_emoji: 🎯, ⭐, 📄, 📝
    - document_type: troubleshooting, technical_manual, installation
    """
```

**Ejemplo real:**
```
Documento: 80.51.332_ET_es-ES_page_26 (Service 25)
Base search score: 50
+ 20 (match código "25")
+ 15 (match modelo "iCombi Classic")  
+ 15 (documento troubleshooting)
= 100% de relevancia 🎯 (Muy Alta)
```

---

### 2. **Integración en API** (`app/main.py`)
- ✅ Aplicado a `/api/v1/predict-fallas`
- ✅ Aplicado a `/api/v1/soporte-tecnico`
- ✅ Ranking automático por relevancia
- ✅ Transparencia total (se muestran todos los factores)

**Respuesta API:**
```json
{
  "contextos": [
    {
      "fuente": "80.51.332_ET_es-ES_page_26",
      "relevance_score": 100.0,
      "confidence_label": "Muy Alta",
      "confidence_emoji": "🎯",
      "document_type": "troubleshooting",
      "relevance_factors": {
        "base_search": 50.0,
        "error_code_match": 20.0,
        "model_match": 15.0,
        "document_type_boost": 15.0
      },
      "has_error_code_match": true,
      "has_model_match": true
    }
  ]
}
```

---

### 3. **Frontend Optimizado** (`frontend/chat.html`)

#### Botones de Documentos con Colores por Relevancia:
- **🎯 Verde (80-100%)**: Muy Alta - Documento casi seguro
- **⭐ Azul (60-79%)**: Alta - Documento muy relevante
- **📄 Amarillo (40-59%)**: Media - Documento útil
- **📝 Gris (<40%)**: Baja - Documento de referencia

#### Visual:
```
🎯 📄 Página 26
   Relevancia: 100% - Muy Alta

⭐ 📄 Página 6
   Relevancia: 75% - Alta

📄 📄 Página 10
   Relevancia: 45% - Media
```

---

## 🎯 **Características Clave**

### ✅ **Sin Alucinaciones**
- **TODO el scoring se basa en datos verificables**
- No usa el LLM para determinar relevancia
- Factores objetivos y determinísticos

### ✅ **Transparencia Total**
- Se muestran todos los factores que contribuyen al score
- El técnico puede ver POR QUÉ un documento es relevante
- Desglose de puntos por cada factor

### ✅ **Ordenamiento Automático**
- Los documentos más relevantes SIEMPRE aparecen primero
- No depende del orden de la búsqueda original
- Consistente en todas las llamadas

### ✅ **Optimización para iCombi Classic**
- Detección automática del modelo
- Boost adicional para documentos específicos del modelo
- Matching flexible de variantes ("iCombi Classic", "icombiclassic", etc.)

---

## 📈 **Resultados Esperados**

### Antes (Sin Sistema de Relevancia):
```
[1] Manual instalación - Score: 0.85
[2] Guía de usuario - Score: 0.83
[3] Troubleshooting Service 25 - Score: 0.80  ← El correcto estaba 3ro
```

### Después (Con Sistema de Relevancia):
```
🎯 [1] Troubleshooting Service 25 - 100% (Muy Alta)  ← Ahora es el 1ro
⭐ [2] Referencia técnica Service - 75% (Alta)
📄 [3] Manual técnico iCombi - 50% (Media)
```

**Mejora**: +25% de relevancia en el primer resultado

---

## 🔧 **Cómo Funciona**

### 1. **Usuario hace consulta**
```json
{
  "descripcion_problema": "por que me arroja un service 25",
  "equipo": {"modelo": "iCombi Classic"}
}
```

### 2. **Sistema detecta:**
- Código de error: "25"
- Modelo objetivo: "iCombi Classic"

### 3. **Búsqueda en KB** (híbrida)
- Encuentra 10 documentos candidatos
- Scores originales de búsqueda

### 4. **Aplicación de Relevancia**
```python
for documento in documentos:
    base_score = documento.score  # Score de búsqueda
    
    # Verificar match de código
    if "25" in documento.contenido:
        base_score += 20
    
    # Verificar match de modelo
    if "iCombi Classic" in documento:
        base_score += 15
    
    # Verificar tipo de documento
    if es_troubleshooting(documento):
        base_score += 15
    
    documento.relevance_score = min(100, base_score)
```

### 5. **Ordenamiento y Respuesta**
- Documentos ordenados por `relevance_score` DESC
- Frontend muestra con colores y emojis
- Técnico ve inmediatamente cuáles son los más relevantes

---

## 📊 **Factores de Relevancia**

| Factor | Peso | Ejemplo |
|--------|------|---------|
| **Base Search Score** | Variable (0-100) | Score de búsqueda semántica + keyword |
| **Error Code Match** | +20 puntos | "service 25" encontrado en documento |
| **Model Match** | +15 puntos | "iCombi Classic" encontrado en metadata |
| **Document Type** | +0 a +15 | Troubleshooting > Technical > Installation |
| **Keyword Strength** | +0 a +10 | Match exacto de palabras clave |

**Total Máximo**: 100 puntos (normalizado)

---

## 🚀 **Uso en Producción**

### API Endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/predict-fallas \
  -H "Content-Type: application/json" \
  -d '{
    "equipo": {"marca": "Rational", "modelo": "iCombi Classic"},
    "descripcion_problema": "service 25",
    "cliente": {"id": "c1"},
    "tecnico": {"id": "t1"}
  }'
```

### Frontend:
```
http://localhost:3000/chat.html
```

Simplemente escribe la consulta y el sistema automáticamente:
1. Busca en la KB
2. Calcula relevancia
3. Ordena por score
4. Muestra con colores visuales

---

## 🎯 **Ventajas vs Otros Sistemas**

### ❌ Sistema con LLM para Relevancia:
- Puede alucinar scores
- Inconsistente entre llamadas
- Costo adicional por LLM call
- No explicable

### ✅ Nuestro Sistema:
- **100% basado en datos reales**
- Consistente y determinístico
- Sin costo adicional de LLM
- Transparencia total
- Verificable y auditable

---

## 📝 **Logging y Debugging**

El sistema incluye logging detallado:

```
🎯 Modelo detectado: iCombi Classic, boost=1.5x
🔍 Aplicando scoring de relevancia
  ✅ Boost aplicado a: 80.51.332_ET_es-ES_page_26 (score: 0.8 → 1.2)

📊 Top 3 documentos por relevancia:
  🎯 1. 80.51.332_ET_es-ES_page_26
     Relevancia: 100% (Muy Alta)
     Tipo: troubleshooting

  ⭐ 2. 80.51.887_ServiceReferenz_page_6
     Relevancia: 75% (Alta)
     Tipo: technical_manual

  📄 3. 80.51.282_iCombi_TM_page_214
     Relevancia: 50% (Media)
     Tipo: technical_manual
```

---

## ✅ **Estado Actual**

- ✅ Sistema implementado
- ✅ API actualizado
- ✅ Frontend optimizado
- ✅ Tests manuales exitosos
- ✅ Documentación completa

---

## 🔮 **Próximos Pasos (Opcional)**

1. **Métricas de calidad**
   - Tracking de clicks en documentos
   - Feedback del técnico (útil/no útil)
   - A/B testing de weights

2. **Machine Learning** (Futuro)
   - Aprender weights óptimos de datos reales
   - Ajuste automático por marca/modelo
   - Personalización por técnico

3. **Cache**
   - Cache de scores de relevancia
   - Invalidación inteligente
   - Warm-up de queries comunes

---

## 📚 **Referencias**

- Código: `services/kb/relevance_scorer.py`
- API: `app/main.py` (líneas 121-190)
- Frontend: `frontend/chat.html` (líneas 595-635)
- Tests: Manual via `chat.html` o Postman


