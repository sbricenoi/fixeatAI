# 🔧 Solución: Metadata Faltante en Knowledge Base

**Fecha:** 2 de febrero de 2026  
**Problema:** Los documentos en KB no retornan información de página ni archivo fuente  
**Estado:** ✅ Solución implementada

---

## 🔍 El Problema

Actualmente, la API retorna respuestas como esta:

```json
"metadata": {
    "page": null,              ← ❌ Sin número de página
    "source": "default.services",  ← ❌ Fuente genérica
    "brand": null,
    "model": null
}
```

### ¿Por qué sucede esto?

Los **22,671 documentos** en tu Knowledge Base fueron ingresados **sin metadata completo**. Específicamente:

- ❌ No tienen número de página (`page: null`)
- ❌ No tienen URL o archivo fuente original
- ❌ Algunos tienen source genérico: `"default.services"`, `"default.activities"`

### ¿Por qué es importante?

Sin esta información, los técnicos NO pueden:
- 📄 Saber en qué página del manual está la información
- 📁 Identificar el archivo fuente original
- 🔗 Navegar directamente a la documentación completa
- ✅ Verificar la fuente de la información

---

## ✅ Soluciones Disponibles

### Solución 1: Re-ingestar PDFs con Metadata Completo (RECOMENDADO)

Si tienes acceso a los PDFs originales, la mejor solución es **re-ingestarlos** usando el script actualizado.

#### Script: `ingestar_pdfs.py`

Este script **SÍ guarda todo el metadata necesario:**

```bash
python ingestar_pdfs.py \
  --pdf "Manual_Rational_iCombi_Classic.pdf" \
  --url "https://docs.rational-online.com/manuals/icombi-classic.pdf" \
  --brand "Rational" \
  --model "iCombi Classic" \
  --categoria "Hornos Combinados"
```

**Metadata que guarda:**
- ✅ `page`: Número de página (1, 2, 3...)
- ✅ `total_pages`: Total de páginas del PDF
- ✅ `source`: URL o ruta del archivo original
- ✅ `source_file`: Nombre del archivo
- ✅ `brand`: Marca del equipo
- ✅ `model`: Modelo del equipo
- ✅ `categoria`: Categoría del documento
- ✅ `chunk_type`: "page" (página completa)

**Resultado esperado en API:**
```json
"metadata": {
    "page": 45,
    "source": "https://docs.rational-online.com/manuals/icombi-classic.pdf",
    "source_file": "Manual_Rational_iCombi_Classic.pdf",
    "brand": "Rational",
    "model": "iCombi Classic"
}
```

#### Ventajas:
- ✅ Metadata completo y estructurado
- ✅ URLs navegables con página específica
- ✅ Mejor organización de documentos
- ✅ Mejora la experiencia del técnico

#### Desventajas:
- ⏱️ Requiere tiempo (depende del número de PDFs)
- 📁 Requiere acceso a PDFs originales

---

### Solución 2: Enriquecer Metadata Existente (RÁPIDO)

Si NO tienes los PDFs originales, puedes enriquecer el metadata existente con información inferida del `doc_id`.

#### Script: `fix_kb_metadata.py` (NUEVO)

He creado un script que analiza los IDs de documentos y extrae información:

```bash
# Análisis sin cambios (ver qué se actualizaría)
python fix_kb_metadata.py --dry-run

# Aplicar cambios
python fix_kb_metadata.py --apply
```

**¿Qué hace?**

Extrae información del `doc_id`:

| Formato doc_id | Metadata extraído |
|----------------|-------------------|
| `manual_rational_page_12` | source: "manual_rational.pdf", page: 12 |
| `https://example.com/manual.pdf#c5` | source: "https://example.com/manual.pdf" |
| `default_services_xxx-yyy` | source: "default.services", source_type: "services" |

#### Ventajas:
- ⚡ Rápido (minutos, no horas)
- 📝 No requiere PDFs originales
- 🔄 Mejora parcial inmediata

#### Desventajas:
- ⚠️ Metadata inferido puede ser incompleto
- ⚠️ No puede inferir página si el doc_id no la tiene

---

### Solución 3: Mejorar URLs sin Página (YA IMPLEMENTADO)

He mejorado el código para que **incluso sin página**, las URLs sean más útiles:

**Cambios aplicados:**

1. **`services/kb/demo_kb.py`** - Función `generate_document_url()` mejorada:
   - Maneja mejor casos sin página
   - Agrega parámetros descriptivos a URLs
   - URLs más informativas para sources "default.*"

2. **`app/main.py`** - Response incluye más metadata:
   - Agregado: `source_file` (nombre del archivo)
   - Agregado: `chunk_type` (tipo de chunk)
   - Mejor formateo de `document_url`

**Ejemplo de mejora:**

Antes:
```json
"document_url": "/view-document/default_services_xxx"
```

Después:
```json
"document_url": "/view-document/default_services_xxx?source=services"
```

---

## 🚀 Plan de Acción Recomendado

### Paso 1: Análisis (YA HECHO)

```bash
# Conectar al servidor
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI

# Ver estado actual
docker-compose exec mcp python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/data/chroma')
collection = client.get_or_create_collection('kb_tech')
print('Total docs:', collection.count())
result = collection.get(limit=5, include=['metadatas'])
for i, meta in enumerate(result['metadatas'][:5]):
    print(f'{i+1}. source: {meta.get(\"source\")}, page: {meta.get(\"page\")}')
"
```

**Resultado actual:**
- Total: 22,671 documentos
- Con página: 0% ❌
- Con source: ~100% (pero genéricos)

---

### Paso 2: Decidir Estrategia

#### Opción A: ¿Tienes los PDFs originales?

**SÍ tengo PDFs** → Usar **Solución 1** (re-ingestar)

**Ventaja:** Metadata perfecto  
**Tiempo:** 1-2 horas dependiendo del número de PDFs  
**Resultado:** URLs navegables con página exacta

---

#### Opción B: ¿NO tienes los PDFs?

**NO tengo PDFs** → Usar **Solución 2** (enriquecer metadata)

**Ventaja:** Rápido y mejora parcial  
**Tiempo:** 5-10 minutos  
**Resultado:** Metadata mejorado pero sin páginas

---

### Paso 3: Aplicar Solución

#### Si elegiste Opción A (Re-ingestar):

```bash
# 1. Preparar PDFs en carpeta
mkdir -p ~/pdfs_manuales
# Subir tus PDFs aquí

# 2. Copiar PDFs al servidor
scp -i fixeatIA.pem ~/pdfs_manuales/*.pdf ec2-user@18.220.79.28:~/pdfs/

# 3. Conectar al servidor
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI

# 4. Limpiar KB anterior (OPCIONAL - CUIDADO!)
# docker-compose exec mcp python3 -c "import chromadb; ..."
# Solo hazlo si quieres empezar desde cero

# 5. Ingestar PDFs con metadata completo
for pdf in ~/pdfs/*.pdf; do
  python3 ingestar_pdfs.py \
    --pdf "$pdf" \
    --url "https://tu-servidor-docs.com/$(basename $pdf)" \
    --brand "Rational" \
    --model "iCombi Classic"
done

# 6. Verificar
docker-compose exec mcp python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/data/chroma')
collection = client.get_or_create_collection('kb_tech')
result = collection.get(limit=1, include=['metadatas'], where={'page': {'$ne': None}})
print('Docs con página:', len(result['ids']))
if result['metadatas']:
    print('Ejemplo:', result['metadatas'][0])
"
```

---

#### Si elegiste Opción B (Enriquecer metadata):

```bash
# 1. Conectar al servidor
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI

# 2. Copiar script al servidor
# (el script ya está en el repo, hacer git pull)
git pull origin main

# 3. Análisis (sin cambios)
docker-compose exec mcp python3 fix_kb_metadata.py --dry-run

# 4. Revisar salida y si se ve bien, aplicar
docker-compose exec mcp python3 fix_kb_metadata.py --apply

# 5. Reiniciar MCP para que tome cambios
docker-compose restart mcp

# 6. Verificar
curl -X POST http://localhost:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{"cliente":{"id":"test"},"equipo":{"marca":"Rational"},"descripcion_problema":"service 25"}'
```

---

## 📊 Comparación de Resultados

### Antes (Actual):

```json
{
  "metadata": {
    "page": null,
    "source": "default.services",
    "brand": null,
    "model": null
  },
  "document_url": "/view-document/default_services_xxx"
}
```

❌ El técnico NO sabe:
- En qué página está la información
- Qué documento consultar
- Cómo verificar la fuente

---

### Después (con Solución 1 - Re-ingestar):

```json
{
  "metadata": {
    "page": 45,
    "source": "https://docs.rational-online.com/manuals/icombi-classic.pdf",
    "source_file": "Manual_Rational_iCombi_Classic.pdf",
    "brand": "Rational",
    "model": "iCombi Classic",
    "chunk_type": "page"
  },
  "document_url": "https://docs.rational-online.com/manuals/icombi-classic.pdf#page=45"
}
```

✅ El técnico puede:
- 📄 Ir directamente a la página 45 del manual
- 📁 Saber qué manual consultar
- 🔗 Click en URL y ver el documento original
- ✅ Verificar la información fácilmente

---

### Después (con Solución 2 - Enriquecer):

```json
{
  "metadata": {
    "page": null,
    "source": "default.services",
    "source_type": "services",
    "source_category": "imported_data",
    "source_file": null
  },
  "document_url": "/view-document/default_services_xxx?source=services"
}
```

⚠️ Mejora parcial:
- ✅ Source más descriptivo
- ✅ URL con parámetros informativos
- ❌ Sigue sin página específica
- ❌ No es navegable a documento original

---

## 🎯 Recomendación Final

### Para Máxima Calidad: **Solución 1 (Re-ingestar PDFs)**

**Cuándo:**
- Tienes acceso a los PDFs originales
- Quieres la mejor experiencia de usuario
- Puedes dedicar 1-2 horas al proceso
- El sistema está en fase de construcción/mejora

**Cómo:**
```bash
# Script mejorado que guarda TODO el metadata
python ingestar_pdfs.py \
  --pdf "tu_manual.pdf" \
  --url "https://link-al-pdf-online.com/manual.pdf" \
  --brand "Marca" \
  --model "Modelo"
```

---

### Para Mejora Rápida: **Solución 2 (Enriquecer)**

**Cuándo:**
- NO tienes los PDFs originales
- Necesitas mejora inmediata
- El sistema está en producción y no puedes parar
- Los documentos vienen de fuente externa (BD)

**Cómo:**
```bash
python fix_kb_metadata.py --apply
docker-compose restart mcp
```

---

### Para Mitigación Inmediata: **Solución 3 (Ya Aplicada)**

Los cambios de código que hice **ya están listos** y mejoran las URLs incluso sin página.

**Para activarlos:**

```bash
# Local
git pull origin main
# Reiniciar servicios

# Producción
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📋 Checklist de Implementación

### Antes de empezar:

- [ ] Haz backup de la KB actual
  ```bash
  docker-compose exec mcp tar -czf - /data/chroma > kb_backup_$(date +%Y%m%d).tar.gz
  ```

- [ ] Verifica espacio en disco
  ```bash
  df -h
  ```

- [ ] Decide qué solución usar (1, 2, o ambas)

### Durante:

- [ ] Ejecuta la solución elegida
- [ ] Monitorea logs por errores
- [ ] Verifica que servicios sigan corriendo

### Después:

- [ ] Prueba la API con una consulta
- [ ] Verifica que metadata ahora tiene más información
- [ ] Confirma que `document_url` es más útil
- [ ] Documenta cambios realizados

---

## 🧪 Cómo Verificar que Funcionó

### Test 1: Verificar Metadata en KB

```bash
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI

docker-compose exec mcp python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/data/chroma')
collection = client.get_or_create_collection('kb_tech')

# Buscar docs con página
result = collection.get(
    limit=5,
    include=['metadatas'],
    where={'page': {'$ne': None}}  # Documentos CON página
)

print('Documentos con página:', len(result['ids']))
if result['metadatas']:
    for i, meta in enumerate(result['metadatas'][:3]):
        print(f'{i+1}. page: {meta.get(\"page\")}, source: {meta.get(\"source\")[:50]}')
"
```

**Resultado esperado si funcionó:**
```
Documentos con página: 156
1. page: 45, source: https://docs.rational-online.com/manuals/...
2. page: 12, source: https://docs.electrolux.com/air-o-steam...
3. page: 78, source: Manual_Rational_iCombi_Classic.pdf
```

---

### Test 2: Verificar Response de API

```bash
curl -X POST http://18.220.79.28:8000/api/v1/predict-fallas \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente": {"id": "test"},
    "equipo": {"marca": "Rational", "modelo": "iCombi Classic"},
    "descripcion_problema": "Error service 25 - problema de circulación"
  }' | jq '.data.contextos[0].metadata'
```

**Resultado esperado si funcionó:**
```json
{
  "page": 45,
  "source": "https://docs.rational-online.com/manuals/icombi-classic.pdf",
  "source_file": "Manual_Rational_iCombi_Classic.pdf",
  "brand": "Rational",
  "model": "iCombi Classic",
  "chunk_type": "page"
}
```

---

## 🔄 Estado de los Cambios

### ✅ Cambios Aplicados al Código (Listos para usar)

1. **`services/kb/demo_kb.py`**
   - Mejorada función `generate_document_url()`
   - Mejor manejo de sources "default.*"
   - URLs más descriptivas incluso sin página

2. **`app/main.py`**
   - Response incluye `source_file` y `chunk_type`
   - Mejor estructura de metadata

3. **`fix_kb_metadata.py`** (NUEVO)
   - Script para enriquecer metadata existente
   - Análisis de KB actual
   - Actualización por lotes

4. **`ingestar_pdfs.py`** (Ya existía, verificado)
   - Guarda metadata completo
   - Incluye página, source, brand, model
   - Formato correcto para navegación

### 📤 Subir Cambios a GitHub

```bash
git add -A
git commit -m "fix: Mejorar metadata de KB y URLs navegables con información de página"
git push origin main
```

### 🚀 Aplicar en Producción

```bash
ssh -i fixeatIA.pem ec2-user@18.220.79.28
cd fixeatAI
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

---

## 💡 Mejores Prácticas para el Futuro

### Al Ingestar Nuevos Documentos:

**SIEMPRE usa:**
```bash
python ingestar_pdfs.py \
  --pdf "archivo.pdf" \
  --url "https://url-publica-del-pdf.com/archivo.pdf" \
  --brand "Marca" \
  --model "Modelo" \
  --categoria "Categoría"
```

**NUNCA uses:**
- ❌ Scripts antiguos sin metadata
- ❌ Ingesta directa sin parámetros
- ❌ Importación desde BD sin mapeo de metadata

### Metadata Mínimo Requerido:

| Campo | Tipo | Requerido | Ejemplo |
|-------|------|-----------|---------|
| `source` | string | ✅ SÍ | "https://docs.com/manual.pdf" |
| `page` | integer | ⭐ MUY RECOMENDADO | 45 |
| `brand` | string | ⭐ RECOMENDADO | "Rational" |
| `model` | string | ⭐ RECOMENDADO | "iCombi Classic" |
| `source_file` | string | ⭐ RECOMENDADO | "Manual_Rational.pdf" |
| `chunk_type` | string | Opcional | "page", "section", "paragraph" |

---

## 📞 Soporte

Si tienes problemas implementando estas soluciones:

1. **Revisa logs:**
   ```bash
   docker-compose logs -f mcp
   docker-compose logs -f api
   ```

2. **Verifica health:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:7070/health
   ```

3. **GitHub Issues:** https://github.com/sbricenoi/fixeatAI/issues

---

## ✅ Resumen

**El problema:** Documentos en KB sin metadata de página ni fuente original  
**La causa:** Ingesta sin metadata completo  
**La solución:** Re-ingestar PDFs con `ingestar_pdfs.py` (mejor) o enriquecer metadata con `fix_kb_metadata.py` (rápido)  
**El resultado:** URLs navegables con página específica para los técnicos

**Próximo paso:** Decidir qué solución implementar según tus recursos y tiempo disponible.

---

**Fecha:** 2 de febrero de 2026  
**Autor:** Sistema FIXEAT AI  
**Status:** ✅ Soluciones listas para implementar
