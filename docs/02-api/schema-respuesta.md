# 📋 SCHEMA DE RESPUESTA - PREDICTOR DE FALLAS

## 🎯 Estructura Completa de la Respuesta

La respuesta del endpoint `/api/v1/predict-fallas` sigue esta estructura JSON:

---

## 📦 Response Wrapper (Estándar del Proyecto)

```json
{
  "traceId": "uuid-único",
  "code": "OK",
  "message": "Predicción generada",
  "data": {
    // ... contenido específico del predictor (ver abajo)
  }
}
```

### Campos del Wrapper:

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `traceId` | `string` | UUID único para trazabilidad de la request | `"baab2085-1347-49c1-a361-baea96be9733"` |
| `code` | `string` | Código de estado de la respuesta | `"OK"`, `"ERROR"`, `"PARTIAL"` |
| `message` | `string` | Mensaje descriptivo del resultado | `"Predicción generada"` |
| `data` | `object` | Payload con el contenido específico | Ver estructura abajo |

---

## 🔍 Estructura del Campo `data`

```json
{
  "fallas_probables": [
    {
      "falla": "string",
      "confidence": 0.0 - 1.0,
      "rationale": "string",
      "repuestos_sugeridos": ["string"],
      "herramientas_sugeridas": ["string"],
      "pasos": [
        {
          "orden": 1,
          "descripcion": "string",
          "tipo": "seguridad|diagnostico|reparacion"
        }
      ]
    }
  ],
  "feedback_coherencia": "string",
  "fuentes": ["string"],
  "contextos": [
    {
      "fuente": "string",
      "score": 0.0 - 1.0,
      "relevance_score": 0 - 100,
      "confidence_label": "Baja|Media|Alta|Muy Alta",
      "llm_explanation": "string",
      "contexto": "string",
      "document_url": "string",
      "metadata": {
        "page": "number|null",
        "source": "string",
        "brand": "string|null",
        "model": "string|null"
      }
    }
  ],
  "signals": {
    "kb_hits": 0,
    "context_length": 0,
    "low_evidence": false,
    "fallback_used": false,
    "llm_used": true,
    "validation_passed": true
  },
  "quality_metrics": {
    "context_relevance": 0.0 - 1.0,
    "source_diversity": 0.0 - 1.0,
    "prediction_confidence": 0.0 - 1.0
  }
}
```

---

## 📊 Descripción Detallada de Cada Campo

### 1️⃣ `fallas_probables` (array)

Lista de fallas diagnosticadas, ordenadas por confidence descendente.

**Estructura de cada falla:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `falla` | `string` | ✅ | Descripción de la falla detectada |
| `confidence` | `float` | ✅ | Nivel de confianza del diagnóstico (0.0 a 1.0) |
| `rationale` | `string` | ✅ | Explicación del diagnóstico con referencias a fuentes |
| `repuestos_sugeridos` | `array<string>` | ✅ | Lista de repuestos necesarios (puede incluir códigos) |
| `herramientas_sugeridas` | `array<string>` | ✅ | Lista de herramientas necesarias |
| `pasos` | `array<object>` | ✅ | Pasos ordenados de diagnóstico y reparación |

**Ejemplo:**
```json
{
  "falla": "Fallo en el ventilador y posible sobrecalentamiento del motor",
  "confidence": 0.85,
  "rationale": "El código de error E004 indica un problema relacionado con el ventilador [source:default_comments_9dce19b5]",
  "repuestos_sugeridos": ["ventilador", "motor"],
  "herramientas_sugeridas": ["destornillador", "multímetro"],
  "pasos": [...]
}
```

---

### 2️⃣ `pasos` (array dentro de cada falla)

Secuencia ordenada de pasos para diagnóstico y reparación.

**Estructura de cada paso:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `orden` | `integer` | ✅ | Número secuencial del paso (1, 2, 3...) |
| `descripcion` | `string` | ✅ | Descripción detallada del paso |
| `tipo` | `string` | ✅ | Tipo de paso: `"seguridad"`, `"diagnostico"`, o `"reparacion"` |

**Estructura típica de pasos:**
1. **3 pasos de seguridad inicial** (tipo: `"seguridad"`)
2. **3-5 pasos de diagnóstico** (tipo: `"diagnostico"`)
3. **2-4 pasos de reparación** (tipo: `"reparacion"`)
4. **1 paso de seguridad final** (tipo: `"seguridad"`)

**Ejemplo:**
```json
[
  {
    "orden": 1,
    "descripcion": "Desconectar el equipo de la fuente de alimentación eléctrica",
    "tipo": "seguridad"
  },
  {
    "orden": 2,
    "descripcion": "Usar equipo de protección personal (EPP) adecuado",
    "tipo": "seguridad"
  },
  {
    "orden": 3,
    "descripcion": "Verificar que no haya presión residual en el sistema",
    "tipo": "seguridad"
  },
  {
    "orden": 4,
    "descripcion": "Inspeccionar visualmente el ventilador y el motor",
    "tipo": "diagnostico"
  },
  {
    "orden": 5,
    "descripcion": "Medir la continuidad del motor con un multímetro",
    "tipo": "diagnostico"
  },
  {
    "orden": 6,
    "descripcion": "Reemplazar el ventilador y/o motor si están defectuosos",
    "tipo": "reparacion"
  },
  {
    "orden": 7,
    "descripcion": "Realizar una prueba supervisada del equipo",
    "tipo": "seguridad"
  }
]
```

---

### 3️⃣ `feedback_coherencia` (string)

Evaluación de la coherencia entre el problema reportado y la información disponible en el KB.

**Ejemplos:**
- `"El problema reportado es coherente con los síntomas descritos y el código de error indicado"`
- `"El problema reportado es coherente, pero la falta de información específica limita la certeza del diagnóstico"`
- `"Se requiere más información para un diagnóstico preciso"`

---

### 4️⃣ `fuentes` (array)

Lista de IDs de documentos consultados en el Knowledge Base.

**Formato:**
```json
[
  "default_comments_9decd33e-dde5-4d6b-84df-07c483d1799c",
  "https://fixeat-dev.s3.us-east-2.amazonaws.com/kb/data.txt#c4",
  "default_form_responses_07c3d9cf-c012-4b7a-af46-fd7e4d2f3db2"
]
```

**Uso:** Permite trazabilidad de dónde proviene la información.

---

### 5️⃣ `contextos` (array) ⭐ NUEVO

Lista detallada de contextos consultados con análisis del LLM Re-Ranker.

**Estructura de cada contexto:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fuente` | `string` | ID del documento en el KB |
| `score` | `float` | Score de búsqueda semántica original (0.0-1.0) |
| `relevance_score` | `integer` | **Score del LLM Re-Ranker** (0-100) |
| `confidence_label` | `string` | Etiqueta de confianza: `"Baja"`, `"Media"`, `"Alta"`, `"Muy Alta"` |
| `llm_explanation` | `string` | **Explicación del LLM** de por qué el documento es relevante |
| `contexto` | `string` | Fragmento de texto relevante (hasta 1500 chars) |
| `document_url` | `string` | URL navegable al documento (puede incluir #page=N) |
| `metadata` | `object` | Metadata del documento |

**Ejemplo:**
```json
{
  "fuente": "default_equipment_parts_9bf95f54-d2ba-40c0-aaf2-eb41f64888e6",
  "score": 0.89,
  "relevance_score": 85,
  "confidence_label": "Alta",
  "llm_explanation": "Este documento contiene información específica sobre la bomba de drenaje del modelo Icombi Pro, incluyendo el código de repuesto exacto (7103721)",
  "contexto": "FILTRO DRENAJE, 16M3/HORA (USE 7103721). Reemplazar cuando esté obstruido...",
  "document_url": "https://fixeat-dev.s3.us-east-2.amazonaws.com/kb/manual_rational.pdf#page=45",
  "metadata": {
    "page": 45,
    "source": "manual_rational.pdf",
    "brand": "Rational",
    "model": "Icombi Pro"
  }
}
```

**Importancia:**
- ✅ `relevance_score` y `llm_explanation` son generados por el **LLM Re-Ranker**
- ✅ El LLM analiza semánticamente cada documento y explica su relevancia
- ✅ Los documentos están ordenados por `relevance_score` (más relevante primero)
- ✅ Proporciona transparencia sobre por qué el sistema eligió cada documento

---

### 6️⃣ `signals` (object)

Señales técnicas sobre el proceso de inferencia.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `kb_hits` | `integer` | Número de documentos encontrados en el KB |
| `context_length` | `integer` | Longitud total del contexto usado (en caracteres) |
| `low_evidence` | `boolean` | Si hubo poca evidencia para el diagnóstico |
| `fallback_used` | `boolean` | Si se usó lógica de fallback (heurística) |
| `llm_used` | `boolean` | Si se usó el LLM para el diagnóstico |
| `validation_passed` | `boolean` | Si la respuesta pasó validaciones |

**Ejemplo:**
```json
{
  "kb_hits": 20,
  "context_length": 16653,
  "low_evidence": false,
  "fallback_used": false,
  "llm_used": true,
  "validation_passed": true
}
```

---

### 7️⃣ `quality_metrics` (object)

Métricas de calidad de la respuesta.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `context_relevance` | `float` | Relevancia del contexto encontrado (0.0-1.0) |
| `source_diversity` | `float` | Diversidad de fuentes consultadas (0.0-1.0) |
| `prediction_confidence` | `float` | Confianza global de la predicción (0.0-1.0) |

**Ejemplo:**
```json
{
  "context_relevance": 1.0,
  "source_diversity": 1.0,
  "prediction_confidence": 0.85
}
```

---

## 📝 Ejemplo Completo de Respuesta

```json
{
  "traceId": "4effac94-417b-476a-a8b6-ecbf74e4d348",
  "code": "OK",
  "message": "Predicción generada",
  "data": {
    "fallas_probables": [
      {
        "falla": "Fallo en el ventilador y posible sobrecalentamiento del motor",
        "confidence": 0.85,
        "rationale": "El código de error E004 indica un problema relacionado con el ventilador, y el olor a quemado sugiere un posible sobrecalentamiento del motor, lo cual es crítico para el funcionamiento del equipo [source:default_comments_9dce19b5-0336-47af-af0c-3f179e8ceea4].",
        "repuestos_sugeridos": [
          "ventilador",
          "motor"
        ],
        "herramientas_sugeridas": [
          "destornillador",
          "multímetro"
        ],
        "pasos": [
          {
            "orden": 1,
            "descripcion": "Desconectar el equipo de la fuente de alimentación eléctrica",
            "tipo": "seguridad"
          },
          {
            "orden": 2,
            "descripcion": "Usar equipo de protección personal (EPP) adecuado",
            "tipo": "seguridad"
          },
          {
            "orden": 3,
            "descripcion": "Verificar que no haya presión residual en el sistema",
            "tipo": "seguridad"
          },
          {
            "orden": 4,
            "descripcion": "Inspeccionar visualmente el ventilador y el motor en busca de daños visibles",
            "tipo": "diagnostico"
          },
          {
            "orden": 5,
            "descripcion": "Medir la continuidad del motor con un multímetro para verificar su estado",
            "tipo": "diagnostico"
          },
          {
            "orden": 6,
            "descripcion": "Comprobar el funcionamiento del ventilador al conectarlo directamente a la corriente",
            "tipo": "diagnostico"
          },
          {
            "orden": 7,
            "descripcion": "Reemplazar el ventilador y/o motor si se determina que están defectuosos",
            "tipo": "reparacion"
          },
          {
            "orden": 8,
            "descripcion": "Reensamblar el equipo y asegurarse de que todas las conexiones estén firmes",
            "tipo": "reparacion"
          },
          {
            "orden": 9,
            "descripcion": "Realizar una prueba supervisada del equipo para asegurar su correcto funcionamiento",
            "tipo": "seguridad"
          }
        ]
      }
    ],
    "feedback_coherencia": "El problema reportado es coherente con los síntomas descritos y el código de error indicado.",
    "fuentes": [
      "default_comments_9decd33e-dde5-4d6b-84df-07c483d1799c",
      "https://fixeat-dev.s3.us-east-2.amazonaws.com/kb/data.txt#c4",
      "default_comments_9decd23f-4f8f-4c72-a81f-82f3963d0b38",
      "default_form_responses_07c3d9cf-c012-4b7a-af46-fd7e4d2f3db2"
    ],
    "contextos": [
      {
        "fuente": "default_comments_9decd33e-dde5-4d6b-84df-07c483d1799c",
        "score": 0.92,
        "relevance_score": 95,
        "confidence_label": "Muy Alta",
        "llm_explanation": "Este documento describe exactamente el mismo problema: error E004 con ventilador que no gira y olor a quemado en un equipo Rational Combi Master Plus",
        "contexto": "ERROR E004 - VENTILADOR NO FUNCIONA\n\nProblema: El ventilador del horno no gira, se escucha un zumbido del motor antes de apagarse. Hay un olor característico a quemado.\n\nCausa: Motor del ventilador sobrecalentado o ventilador bloqueado...",
        "document_url": "https://fixeat-dev.s3.us-east-2.amazonaws.com/kb/manual_rational.pdf#page=67",
        "metadata": {
          "page": 67,
          "source": "manual_rational.pdf",
          "brand": "Rational",
          "model": "Combi Master Plus"
        }
      },
      {
        "fuente": "default_form_responses_07c3d9cf-c012-4b7a-af46-fd7e4d2f3db2",
        "score": 0.87,
        "relevance_score": 82,
        "confidence_label": "Alta",
        "llm_explanation": "Contiene procedimiento detallado de diagnóstico del ventilador con multímetro y pruebas de continuidad",
        "contexto": "PROCEDIMIENTO DE DIAGNÓSTICO - VENTILADOR\n\n1. Desconectar alimentación\n2. Medir resistencia del motor (debe ser 50-100 ohms)\n3. Verificar rodamientos del ventilador...",
        "document_url": "/view-document/default_form_responses_07c3d9cf",
        "metadata": {
          "page": null,
          "source": "base_conocimiento_tecnico",
          "brand": null,
          "model": null
        }
      }
    ],
    "signals": {
      "kb_hits": 20,
      "context_length": 16653,
      "low_evidence": false,
      "fallback_used": false,
      "llm_used": true,
      "validation_passed": true
    },
    "quality_metrics": {
      "context_relevance": 1.0,
      "source_diversity": 1.0,
      "prediction_confidence": 0.85
    }
  }
}
```

---

## 🔑 Campos Clave para Frontend

### Para mostrar al usuario:

1. **`fallas_probables[].falla`** - Título del diagnóstico
2. **`fallas_probables[].confidence`** - Nivel de confianza (mostrar como % o barra)
3. **`fallas_probables[].repuestos_sugeridos`** - Lista de repuestos
4. **`fallas_probables[].herramientas_sugeridas`** - Lista de herramientas
5. **`fallas_probables[].pasos`** - Pasos ordenados (separar por tipo)
6. **`contextos[].llm_explanation`** - Mostrar por qué es relevante cada documento
7. **`contextos[].document_url`** - Link para ver documento completo

### Para debugging/logging:

1. **`traceId`** - Para soporte técnico
2. **`signals`** - Métricas técnicas del proceso
3. **`fuentes`** - IDs de documentos consultados
4. **`quality_metrics`** - Calidad de la respuesta

---

## 📊 Niveles de Confidence

| Rango | Etiqueta | Color Sugerido | Significado |
|-------|----------|----------------|-------------|
| 0.85 - 1.00 | Muy Alta | 🟢 Verde | Diagnóstico muy confiable |
| 0.70 - 0.84 | Alta | 🟢 Verde | Diagnóstico confiable |
| 0.50 - 0.69 | Media | 🟡 Amarillo | Diagnóstico razonable |
| 0.30 - 0.49 | Baja | 🟠 Naranja | Requiere más información |
| < 0.30 | Muy Baja | 🔴 Rojo | Información insuficiente |

---

## 🎨 Recomendaciones de UI/UX

### 1. Mostrar Fallas Probables
```
┌────────────────────────────────────────────┐
│ 🔧 Fallo en el ventilador                  │
│ Confianza: ████████░░ 85% (Muy Alta)       │
│                                             │
│ 📋 Repuestos necesarios:                   │
│ • Ventilador                                │
│ • Motor                                     │
│                                             │
│ 🛠️ Herramientas:                           │
│ • Destornillador                            │
│ • Multímetro                                │
│                                             │
│ [Ver pasos de reparación]                  │
└────────────────────────────────────────────┘
```

### 2. Mostrar Pasos (Agrupados por Tipo)
```
⚠️ SEGURIDAD (3 pasos)
 1. Desconectar alimentación eléctrica
 2. Usar EPP adecuado
 3. Verificar presión del sistema

🔍 DIAGNÓSTICO (3 pasos)
 4. Inspeccionar visualmente ventilador
 5. Medir continuidad con multímetro
 6. Probar funcionamiento directo

🔧 REPARACIÓN (2 pasos)
 7. Reemplazar componentes defectuosos
 8. Reensamblar equipo

✅ VERIFICACIÓN (1 paso)
 9. Prueba supervisada del equipo
```

### 3. Mostrar Contextos (Con LLM Re-Ranker)
```
📚 Documentos Consultados

🎯 Relevancia: 95% (Muy Alta)
   Manual Rational - Página 67
   "Describe exactamente el mismo problema: error E004..."
   [Ver documento completo]

⭐ Relevancia: 82% (Alta)
   Base Conocimiento Técnico
   "Contiene procedimiento detallado de diagnóstico..."
   [Ver documento completo]
```

---

## 🚀 Ejemplo de Uso en Frontend

### React/TypeScript:

```typescript
interface FallaProbable {
  falla: string;
  confidence: number;
  rationale: string;
  repuestos_sugeridos: string[];
  herramientas_sugeridas: string[];
  pasos: Paso[];
}

interface Paso {
  orden: number;
  descripcion: string;
  tipo: 'seguridad' | 'diagnostico' | 'reparacion';
}

interface Contexto {
  fuente: string;
  score: number;
  relevance_score: number;  // 0-100 del LLM Re-Ranker
  confidence_label: string;
  llm_explanation: string;  // Explicación del LLM
  contexto: string;
  document_url: string;
  metadata: {
    page?: number;
    source: string;
    brand?: string;
    model?: string;
  };
}

interface PredictorResponse {
  traceId: string;
  code: string;
  message: string;
  data: {
    fallas_probables: FallaProbable[];
    feedback_coherencia: string;
    fuentes: string[];
    contextos: Contexto[];
    signals: {
      kb_hits: number;
      context_length: number;
      low_evidence: boolean;
      fallback_used: boolean;
      llm_used: boolean;
      validation_passed: boolean;
    };
    quality_metrics: {
      context_relevance: number;
      source_diversity: number;
      prediction_confidence: number;
    };
  };
}

// Uso:
const response: PredictorResponse = await fetch(
  'http://18.220.79.28:8000/api/v1/predict-fallas',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  }
).then(r => r.json());

// Acceder a datos:
const fallas = response.data.fallas_probables;
const contextos = response.data.contextos;

// Mostrar primera falla con mayor confidence:
const topFalla = fallas[0];
console.log(`Falla: ${topFalla.falla}`);
console.log(`Confidence: ${(topFalla.confidence * 100).toFixed(0)}%`);
console.log(`Repuestos: ${topFalla.repuestos_sugeridos.join(', ')}`);

// Mostrar contextos ordenados por relevancia del LLM:
contextos.forEach(ctx => {
  console.log(`Relevancia: ${ctx.relevance_score}%`);
  console.log(`Razón: ${ctx.llm_explanation}`);
  console.log(`URL: ${ctx.document_url}`);
});
```

---

## ✅ Validación del Schema

El sistema siempre retorna:
- ✅ Al menos 1 falla en `fallas_probables` (o array vacío si no hay evidencia)
- ✅ Al menos 3 pasos de seguridad inicial
- ✅ Al menos 1 paso de seguridad final
- ✅ Pasos ordenados secuencialmente (1, 2, 3...)
- ✅ Confidence entre 0.0 y 1.0
- ✅ `contextos` siempre presente (puede estar vacío)
- ✅ `signals.llm_used` indica si se usó LLM

---

**Ubicación del código:**
- Request model: `/app/main.py` línea 76-80
- Response builder: `/app/main.py` línea 52-68
- Lógica principal: `/app/main.py` línea 83-226
- Estructura LLM: `/services/orch/rag.py`

**Servidor productivo:** `http://18.220.79.28:8000/api/v1/predict-fallas`

---

**Creado:** 2 de febrero de 2026  
**Versión API:** 0.1.0  
**Estado:** ✅ ACTIVO EN PRODUCCIÓN
