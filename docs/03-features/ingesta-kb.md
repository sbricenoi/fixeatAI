# 📚 GUÍA COMPLETA - INGESTA DE KNOWLEDGE BASE (KB)

## 🎯 ¿Qué es la Ingesta de KB?

La ingesta de KB es el proceso de **alimentar el sistema con documentación técnica** (manuales, PDFs, hojas técnicas, etc.) para que el sistema pueda:

- 🔍 Buscar información relevante
- 🤖 Generar diagnósticos inteligentes
- 🔩 Sugerir repuestos específicos
- 📋 Proporcionar pasos de reparación contextualizados

---

## 🏗️ ARQUITECTURA DE INGESTA

```
┌─────────────────────────────────────────────────┐
│          ENTRADA DE DATOS                       │
│  - PDFs                                         │
│  - Documentos Word (DOCX)                       │
│  - Excel (XLSX)                                 │
│  - HTML/URLs                                    │
│  - Texto plano                                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│       EXTRACCIÓN DE TEXTO                       │
│  - pypdf / pdfminer.six (PDFs)                  │
│  - python-docx (Word)                           │
│  - pandas + openpyxl (Excel)                    │
│  - BeautifulSoup (HTML)                         │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│       CURACIÓN Y PROCESAMIENTO                  │
│  1. Extracción de entidades (marca, modelo)     │
│  2. Chunking (división en fragmentos 1200 chars)│
│  3. Quality scoring (filtrar baja calidad)      │
│  4. Fingerprinting (deduplicación)              │
│  5. Auto-aprendizaje de taxonomía (opcional)    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│       GENERACIÓN DE EMBEDDINGS                  │
│  Sentence-Transformers                          │
│  (all-MiniLM-L6-v2)                            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│       ALMACENAMIENTO                            │
│  ChromaDB (Vector Database)                     │
│  - Texto completo                               │
│  - Embeddings vectoriales                       │
│  - Metadata (marca, modelo, categoría, etc.)    │
└─────────────────────────────────────────────────┘
```

---

## 🌐 SERVIDOR PRODUCTIVO

**IP:** `18.220.79.28`  
**Puerto MCP:** `7070`  
**Base URL:** `http://18.220.79.28:7070`

---

## 📡 ENDPOINTS DE INGESTA

### 1️⃣ Ingesta Simple - `/tools/kb_ingest`

**Endpoint más usado para ingesta básica**

```bash
POST http://18.220.79.28:7070/tools/kb_ingest
```

**Body:**
```json
{
  "docs": [
    {
      "id": "doc_001",
      "text": "Contenido del documento...",
      "metadata": {
        "brand": "Rational",
        "model": "Icombi Pro",
        "category": "horno",
        "source": "manual_rational.pdf"
      }
    }
  ],
  "urls": [
    "https://example.com/manual.pdf",
    "https://example.com/hoja-tecnica.pdf"
  ],
  "auto_curate": true,
  "auto_learn_taxonomy": true
}
```

---

### 2️⃣ Curación Previa - `/tools/kb_curate`

**Para revisar y limpiar datos antes de ingestar**

```bash
POST http://18.220.79.28:7070/tools/kb_curate
```

**Body:**
```json
{
  "docs": [...],
  "urls": [...],
  "auto_learn_taxonomy": true
}
```

**Respuesta:**
```json
{
  "docs": [...],           // Documentos aprobados
  "quarantine": [...],     // Documentos rechazados (baja calidad)
  "stats": {
    "input": 10,
    "curated": 8,
    "quarantine": 2
  },
  "taxonomy_updated": true
}
```

---

## 📋 FORMATOS SOPORTADOS

| Formato | Extensión | Librería Usada | Estado |
|---------|-----------|----------------|--------|
| **PDF** | `.pdf` | pypdf, pdfminer.six | ✅ Soportado |
| **Word** | `.docx` | python-docx | ✅ Soportado |
| **Excel** | `.xlsx` | pandas, openpyxl | ✅ Soportado |
| **HTML** | `.html`, `.htm` | BeautifulSoup | ✅ Soportado |
| **Texto** | `.txt` | Nativo | ✅ Soportado |
| **URLs** | `http(s)://` | requests + extractores | ✅ Soportado |

---

## 💡 EJEMPLOS PRÁCTICOS

### Ejemplo 1: Ingestar un PDF desde URL

```bash
curl -X POST http://18.220.79.28:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "urls": [
      "https://fixeat-dev.s3.us-east-2.amazonaws.com/kb/manual_rational.pdf"
    ],
    "auto_curate": true,
    "auto_learn_taxonomy": true
  }'
```

**Respuesta:**
```json
{
  "ingested": 25,
  "from_urls": 1,
  "errors": [],
  "curated": true,
  "stats": {
    "input": 1,
    "curated": 25,
    "quarantine": 0
  },
  "auto_learning": {
    "brands_learned": 2,
    "models_learned": 3,
    "categories_learned": 1
  }
}
```

---

### Ejemplo 2: Ingestar Texto Directo con Metadata

```bash
curl -X POST http://18.220.79.28:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "docs": [
      {
        "id": "manual_rational_001",
        "text": "HORNO RATIONAL ICOMBI PRO\n\nProblema: Bomba de drenaje no funciona\nSolución: Verificar filtro de drenaje (referencia: 7103721)\nHerramientas: destornillador, multímetro",
        "metadata": {
          "brand": "Rational",
          "model": "Icombi Pro",
          "category": "horno",
          "source": "manual_rational.pdf",
          "page": 45
        }
      }
    ],
    "auto_curate": true
  }'
```

---

### Ejemplo 3: Ingestar Múltiples URLs

```bash
curl -X POST http://18.220.79.28:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "urls": [
      "https://example.com/manual_electrolux.pdf",
      "https://example.com/hoja_tecnica_rational.pdf",
      "https://example.com/guia_mantenimiento.pdf"
    ],
    "auto_curate": true,
    "auto_learn_taxonomy": true
  }' \
  -s | python3 -m json.tool
```

---

### Ejemplo 4: Ingestar Archivo Base64

```bash
curl -X POST http://18.220.79.28:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "docs": [
      {
        "id": "manual_hobart",
        "file_base64": "JVBERi0xLjQKJcfsj6IKN...",
        "filename": "manual_hobart.pdf",
        "mime_type": "application/pdf",
        "metadata": {
          "brand": "Hobart",
          "model": "Convection Oven"
        }
      }
    ],
    "auto_curate": true
  }'
```

---

## 🔧 PROCESO DE CURACIÓN

### 1. Extracción Automática de Entidades

El sistema busca automáticamente en el texto:

- **Marca (brand):** Rational, Electrolux, Hobart, Zanussi, etc.
- **Modelo (model):** Icombi Pro, Air-O-Steam, SelfCookingCenter, etc.
- **Categoría (category):** horno, laminadora, amasadora, freidora, etc.

**Patrones de búsqueda:**
```
Marca: "MARCA: Rational", "Brand: Electrolux", "Fabricante: Hobart"
Modelo: "MODELO: Icombi Pro", "Mod. SM-520", "REF: ABC123"
Categoría: "HORNO", "laminadora", "amasadora", "divisora"
```

---

### 2. Chunking (División en Fragmentos)

- **Tamaño:** 1200 caracteres por chunk
- **Overlap:** 200 caracteres entre chunks
- **Objetivo:** Mantener contexto entre fragmentos

**Ejemplo:**
```
Documento original: 5000 caracteres
↓
Chunk 1: chars 0-1200
Chunk 2: chars 1000-2200 (overlap de 200)
Chunk 3: chars 2000-3200 (overlap de 200)
Chunk 4: chars 3000-4200 (overlap de 200)
Chunk 5: chars 4000-5000
```

---

### 3. Quality Scoring

Cada chunk recibe un puntaje de calidad:

| Longitud | Score | Acción |
|----------|-------|--------|
| ≥ 4000 chars | 0.95 | ✅ Ingestar |
| ≥ 1500 chars | 0.90 | ✅ Ingestar |
| ≥ 600 chars | 0.75 | ✅ Ingestar |
| ≥ 200 chars | 0.60 | ✅ Ingestar |
| < 200 chars | 0.25 | ⚠️ Cuarentena |

**Cuarentena:**
- Chunks con score < 0.5 o longitud < 200 chars
- Se almacenan aparte para revisión manual

---

### 4. Fingerprinting (Deduplicación)

- Cada chunk genera un hash SHA256
- Previene ingesta duplicada
- Permite actualización de documentos existentes (upsert)

---

### 5. Auto-aprendizaje de Taxonomía

Si `auto_learn_taxonomy: true`, el sistema:

1. Analiza el texto completo
2. Extrae entidades candidatas (marcas, modelos, categorías)
3. Valida con confianza y frecuencia
4. Actualiza la taxonomía automáticamente

**Ejemplo de entidades aprendidas:**
```json
{
  "brands_learned": 2,
  "models_learned": 3,
  "categories_learned": 1,
  "new_entities": [
    {"type": "brand", "value": "Sinmag", "confidence": 0.95},
    {"type": "model", "value": "SM-520", "confidence": 0.90},
    {"type": "category", "value": "laminadora", "confidence": 0.98}
  ]
}
```

---

## 📊 TAXONOMÍA

### Ver Taxonomía Actual

```bash
curl http://18.220.79.28:7070/tools/taxonomy
```

**Respuesta:**
```json
{
  "brands": {
    "Rational": ["rational", "Racional"],
    "Electrolux": ["electrolux", "Electro Lux"],
    "Hobart": ["hobart"],
    "Sinmag": ["sinmag", "Sin Mag"]
  },
  "models": {
    "Icombi Pro": ["icombi pro", "iCombipro"],
    "Air-O-Steam": ["air o steam", "airOsteam"],
    "SM-520": ["sm520", "sm 520"]
  },
  "categories": {
    "horno": ["oven", "forno"],
    "laminadora": ["rolling machine", "laminator"],
    "amasadora": ["mixer", "batidora planetaria"]
  }
}
```

---

### Actualizar Taxonomía Manualmente

```bash
curl -X POST http://18.220.79.28:7070/tools/taxonomy/upsert \
  -H 'Content-Type: application/json' \
  -d '{
    "domain": "brands",
    "canonical": "Rational",
    "alias": "Racional"
  }'
```

---

### Bootstrap Automático de Taxonomía

**Analiza todo el KB y extrae taxonomía:**

```bash
curl -X POST http://18.220.79.28:7070/tools/taxonomy/bootstrap
```

**Respuesta:**
```json
{
  "bootstrap_completed": true,
  "new_brands": 5,
  "new_models": 12,
  "new_categories": 8,
  "total_docs_analyzed": 150,
  "timestamp": "2026-02-02T20:30:00Z"
}
```

---

### Estadísticas de Taxonomía

```bash
curl http://18.220.79.28:7070/tools/taxonomy/stats
```

**Respuesta:**
```json
{
  "brands_count": 15,
  "models_count": 45,
  "categories_count": 20,
  "total_entities": 80,
  "top_brands": ["Rational", "Electrolux", "Hobart", "Zanussi", "Sinmag"],
  "top_models": ["Icombi Pro", "Air-O-Steam", "SM-520", "T900", "XYZ-2000"],
  "top_categories": ["horno", "laminadora", "amasadora", "divisora", "freidora"]
}
```

---

## 🔄 FLUJO COMPLETO DE INGESTA

### Flujo Recomendado (Con Auto-Curación):

```
1. Preparar URLs o documentos
   ↓
2. POST /tools/kb_ingest con auto_curate=true
   ↓
3. Sistema extrae texto automáticamente
   ↓
4. Sistema extrae entidades (marca, modelo, categoría)
   ↓
5. Sistema divide en chunks (1200 chars)
   ↓
6. Sistema aplica quality scoring
   ↓
7. Sistema genera fingerprints
   ↓
8. Sistema aprende taxonomía (si auto_learn_taxonomy=true)
   ↓
9. Sistema genera embeddings
   ↓
10. Sistema almacena en ChromaDB
   ↓
11. Respuesta con estadísticas
```

---

### Flujo Manual (Con Curación Previa):

```
1. POST /tools/kb_curate con documentos
   ↓
2. Revisar respuesta (docs aprobados vs quarantine)
   ↓
3. Ajustar documentos si es necesario
   ↓
4. POST /tools/kb_ingest con documentos curados
   ↓
5. Almacenamiento en ChromaDB
```

---

## 📝 METADATA RECOMENDADA

### Metadata Mínima:
```json
{
  "source": "manual_rational.pdf"
}
```

### Metadata Completa (Recomendada):
```json
{
  "brand": "Rational",
  "model": "Icombi Pro",
  "category": "horno",
  "source": "manual_rational.pdf",
  "source_type": "url",
  "source_ref": "https://example.com/manual.pdf",
  "page": 45,
  "section": "Mantenimiento",
  "language": "es",
  "version": "2.1",
  "date": "2025-01-15"
}
```

### Metadata Enriquecida (Automática):
El sistema agrega automáticamente:
```json
{
  "chunk_index": 0,
  "fingerprint": "sha256:abc123...",
  "quality_score": 0.95,
  "updated_at": "2026-02-02T20:30:00Z",
  "text_length": 1200
}
```

---

## 🚨 MANEJO DE ERRORES

### Error 1: URL no accesible
```json
{
  "ingested": 0,
  "from_urls": 1,
  "errors": [
    {
      "url": "https://example.com/manual.pdf",
      "error": "HTTP 404 - Not Found"
    }
  ]
}
```

### Error 2: Formato no soportado
```json
{
  "ingested": 0,
  "errors": [
    {
      "file": "documento.xyz",
      "error": "Formato no soportado"
    }
  ]
}
```

### Error 3: Dependencias faltantes
```bash
# Si falta pypdf para PDFs:
docker exec fixeatai-mcp-1 pip install pypdf pdfminer.six

# Si falta python-docx para Word:
docker exec fixeatai-mcp-1 pip install python-docx

# Si falta openpyxl para Excel:
docker exec fixeatai-mcp-1 pip install pandas openpyxl
```

---

## 📈 MEJORES PRÁCTICAS

### ✅ DO (Hacer):

1. **Usar `auto_curate: true`** para procesamiento automático
2. **Incluir metadata** (brand, model, category) cuando sea posible
3. **Usar `auto_learn_taxonomy: true`** para construir taxonomía automáticamente
4. **Ingestar por lotes** para eficiencia
5. **Verificar taxonomía** después de ingesta masiva
6. **Usar fingerprinting** para prevenir duplicados

### ❌ DON'T (Evitar):

1. **NO ingestar sin curación** en producción
2. **NO omitir metadata importante** (dificulta búsqueda)
3. **NO ingestar chunks demasiado pequeños** (< 200 chars)
4. **NO ignorar la cuarentena** (revisar documentos rechazados)
5. **NO ingestar datos sensibles** sin validación

---

## 🧪 PRUEBA EN PRODUCCIÓN

### 1. Verificar que MCP está activo:

```bash
curl http://18.220.79.28:7070/health
```

**Respuesta esperada:**
```json
{"status": "ok"}
```

---

### 2. Ingestar un documento de prueba:

```bash
curl -X POST http://18.220.79.28:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "docs": [
      {
        "id": "test_rational_001",
        "text": "HORNO RATIONAL ICOMBI PRO - GUÍA DE MANTENIMIENTO\n\nProblema común: La bomba de drenaje no funciona correctamente\n\nCausa probable:\n1. Filtro de drenaje obstruido\n2. Bomba defectuosa\n3. Conexión eléctrica suelta\n\nSolución:\n1. Desconectar alimentación eléctrica\n2. Revisar filtro de drenaje (Ref: 7103721 - FILTRO DRENAJE 16M3/HORA)\n3. Limpiar o reemplazar filtro\n4. Verificar conexiones eléctricas con multímetro\n5. Probar bomba directamente\n\nHerramientas necesarias:\n- Destornillador\n- Multímetro\n- Llave inglesa\n\nTiempo estimado: 30-45 minutos",
        "metadata": {
          "brand": "Rational",
          "model": "Icombi Pro",
          "category": "horno",
          "source": "manual_rational_mantenimiento.pdf",
          "page": 23,
          "section": "Mantenimiento Preventivo"
        }
      }
    ],
    "auto_curate": true,
    "auto_learn_taxonomy": true
  }' \
  -s | python3 -m json.tool
```

---

### 3. Verificar ingesta con búsqueda:

```bash
curl -X POST http://18.220.79.28:7070/tools/kb_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "problema bomba drenaje",
    "top_k": 3
  }' \
  -s | python3 -m json.tool
```

**Respuesta esperada:**
```json
{
  "hits": [
    {
      "doc_id": "test_rational_001#c0",
      "score": 0.92,
      "snippet": "HORNO RATIONAL ICOMBI PRO - GUÍA DE MANTENIMIENTO\n\nProblema común: La bomba de drenaje no funciona correctamente...",
      "metadata": {
        "brand": "Rational",
        "model": "Icombi Pro",
        "category": "horno",
        "source": "manual_rational_mantenimiento.pdf",
        "page": 23,
        "quality_score": 0.95
      }
    }
  ]
}
```

---

## 📊 MONITOREO Y ESTADÍSTICAS

### Ver todos los documentos ingresados:

```python
# Desde Python (scripts de ingesta):
from services.kb.demo_kb import get_all_documents

all_docs = get_all_documents()
print(f"Total documentos en KB: {len(all_docs)}")

for doc in all_docs[:5]:  # Primeros 5
    print(f"- {doc['id']}: {doc['text'][:100]}...")
```

---

### Ver taxonomía aprendida:

```bash
curl http://18.220.79.28:7070/tools/taxonomy/stats
```

---

## 🎓 CASOS DE USO

### Caso 1: Ingesta Masiva de Manuales

**Escenario:** Tienes 50 PDFs de manuales técnicos

**Solución:**
```bash
# Crear archivo urls.txt con todas las URLs
# Luego usar script de ingesta batch

python ingestar_batch.py --urls urls.txt --auto-curate --auto-learn
```

---

### Caso 2: Actualización de Documentación

**Escenario:** Manual actualizado de un modelo existente

**Solución:**
```bash
# Usar mismo ID para actualizar (upsert automático)
curl -X POST http://18.220.79.28:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "docs": [{
      "id": "manual_rational_001",  # Mismo ID = actualización
      "text": "CONTENIDO ACTUALIZADO...",
      "metadata": {
        "brand": "Rational",
        "model": "Icombi Pro",
        "version": "3.0",
        "updated_at": "2026-02-02"
      }
    }],
    "auto_curate": true
  }'
```

---

### Caso 3: Ingesta con Validación Manual

**Escenario:** Documentos críticos que requieren revisión

**Solución:**
```bash
# 1. Curar primero
curl -X POST http://18.220.79.28:7070/tools/kb_curate \
  -H 'Content-Type: application/json' \
  -d '{...}' > curated_output.json

# 2. Revisar curated_output.json

# 3. Ingestar solo documentos aprobados
curl -X POST http://18.220.79.28:7070/tools/kb_ingest \
  -H 'Content-Type: application/json' \
  -d @curated_output.json
```

---

## 🚀 SCRIPTS DE UTILIDAD

En el proyecto hay varios scripts de ingesta disponibles:

### 1. `ingestar_via_api.py`
Ingesta directa vía API del MCP

### 2. `ingestar_batch.py`
Ingesta masiva desde archivo de URLs

### 3. `ingestar_produccion.py`
Script optimizado para producción

### 4. `ingestar_pdfs.py`
Especializado en PDFs

---

## ✅ CHECKLIST DE INGESTA

Antes de ingestar en producción:

- [ ] MCP está activo (`/health` responde OK)
- [ ] Dependencias instaladas (pypdf, python-docx, openpyxl)
- [ ] URLs son accesibles
- [ ] Metadata está bien formada
- [ ] `auto_curate: true` está habilitado
- [ ] `auto_learn_taxonomy: true` si quieres auto-aprendizaje
- [ ] Prueba con 1-2 documentos primero
- [ ] Verifica ingesta con búsqueda
- [ ] Revisa taxonomía después de ingesta

---

## 🎉 RESUMEN

La ingesta de KB es el **corazón del sistema inteligente**. Un KB bien poblado significa:

- ✅ Diagnósticos más precisos
- ✅ Repuestos más específicos
- ✅ Mayor confidence en predicciones
- ✅ Respuestas contextualizadas

**Servidor productivo:** `http://18.220.79.28:7070`  
**Endpoint principal:** `/tools/kb_ingest`  
**Auto-curación:** `auto_curate: true`  
**Auto-aprendizaje:** `auto_learn_taxonomy: true`

---

**Creado:** 2 de febrero de 2026  
**Servidor:** AWS EC2 (18.220.79.28)  
**Estado:** ✅ ACTIVO
