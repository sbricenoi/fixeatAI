# 🔍 ETL Service - Cómo Funciona Internamente con Queries

## 📊 **1. Schema Discovery Automático**

El ETL Service **NO necesita queries manuales**. Descubre automáticamente tu BD:

### **Queries Automáticas de Introspección:**

```sql
-- 1. Descubrir todas las tablas
SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'requisicion_db' 
AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- 2. Descubrir columnas de cada tabla
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, 
       CHARACTER_MAXIMUM_LENGTH, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'requisicion_db' AND TABLE_NAME = 'requisition'
ORDER BY ORDINAL_POSITION;

-- 3. Descubrir Primary Keys
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'requisicion_db' AND TABLE_NAME = 'requisition' 
AND CONSTRAINT_NAME = 'PRIMARY'
ORDER BY ORDINAL_POSITION;

-- 4. Descubrir Foreign Keys
SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'requisicion_db' AND TABLE_NAME = 'requisition' 
AND REFERENCED_TABLE_NAME IS NOT NULL;
```

## 🧠 **2. Análisis IA + Documentación Rica**

Después del discovery, la IA analiza **automáticamente**:

```python
# El ETL Service combina:
schema_data = auto_discovered_schema  # Queries automáticas arriba
documentation = load_rich_documentation()  # Tu JSON de documentación
business_context = extract_business_intelligence()

# IA decide automáticamente:
ai_analysis = {
    "relevancia_tecnica": 8.5,  # Para tabla 'requisition'
    "valor_predictivo": 9.0,
    "prioridad": "CRÍTICA",
    "estrategia": "joined",  # Automáticamente decide hacer JOIN
    "sql_template": "SELECT r.*, c.name as company_name FROM requisition r JOIN company c ON r.company_id = c.id"
}
```

## ⚙️ **3. Generación Automática de Queries de Extracción**

Basado en el análisis IA, genera **automáticamente** las queries optimizadas:

### **Ejemplo Real - Tabla `requisition`:**

```sql
-- Query generada automáticamente por IA (estrategia "joined"):
SELECT 
    r.id,
    r.company_id,
    r.user_id,
    r.number,
    r.description,
    r.state,
    r.total_amount,
    r.created_at,
    r.updated_at,
    -- Contexto enriquecido automáticamente
    c.name as company_name,
    c.business_type,
    u.name as user_name,
    u.email as user_email,
    s.name as supplier_name
FROM requisition r
LEFT JOIN company c ON r.company_id = c.id
LEFT JOIN user u ON r.user_id = u.id  
LEFT JOIN supplier s ON r.supplier_id = s.id
WHERE r.state IN ('approved', 'completed')  -- Filtro inteligente
ORDER BY r.created_at DESC
LIMIT 500 OFFSET ?;  -- Paginación automática
```

### **Ejemplo - Tabla `requisition_item`:**

```sql
-- Query generada automáticamente (estrategia "joined"):
SELECT 
    ri.id,
    ri.requisition_id,
    ri.product_name,
    ri.quantity,
    ri.unit_price,
    ri.total_price,
    ri.description,
    -- Contexto de la requisición padre
    r.number as requisition_number,
    r.state as requisition_state,
    c.name as company_name
FROM requisition_item ri
INNER JOIN requisition r ON ri.requisition_id = r.id
INNER JOIN company c ON r.company_id = c.id
WHERE r.state != 'draft'  -- Solo requisiciones válidas
ORDER BY ri.id
LIMIT 500 OFFSET ?;
```

## 📦 **4. Extracción por Lotes (Batch Processing)**

El ETL Service extrae datos **automáticamente en lotes**:

```python
# Proceso automático:
async def extract_table_data():
    batch_size = 500  # Configurable
    offset = 0
    
    while True:
        # Query automática con paginación
        query = f"""
        {sql_template_generated_by_ai}
        LIMIT {batch_size} OFFSET {offset}
        """
        
        batch = await execute_query(query)
        if not batch:
            break
            
        # Procesar lote
        await transform_and_ingest_batch(batch)
        offset += batch_size
```

## 🔄 **5. Transformación Inteligente**

Para cada registro extraído, aplica **transformación IA automática**:

```python
# Ejemplo de transformación automática:
def transform_requisition_record(record):
    # La IA genera narrativa técnica automáticamente:
    narrative = f"""
    Requisición {record['number']} de {record['company_name']}:
    
    Descripción: {record['description']}
    Estado: {record['state']}
    Monto: ${record['total_amount']}
    Solicitante: {record['user_name']} ({record['user_email']})
    Proveedor: {record['supplier_name']}
    Fecha: {record['created_at']}
    
    Contexto empresarial: Requisición de compra en empresa {record['company_name']} 
    del tipo {record['business_type']}, procesada por el sistema de gestión de compras.
    """
    
    # Metadata automática extraída:
    metadata = {
        "company": record['company_name'],
        "business_type": record['business_type'],
        "state": record['state'],
        "amount_range": categorize_amount(record['total_amount']),
        "month": extract_month(record['created_at']),
        "source_table": "requisition"
    }
    
    return {
        "content": narrative,
        "metadata": metadata
    }
```

## 📚 **6. Ingesta al Knowledge Base**

Los datos transformados van **automáticamente** al KB:

```python
# Ingesta automática al Knowledge Base
async def ingest_to_kb(transformed_data):
    for record in transformed_data:
        await kb_client.ingest_document(
            content=record['content'],
            metadata=record['metadata']
        )
```

## 🕐 **7. Ejecución Programada Automática**

El ETL Service ejecuta **automáticamente**:

```python
# Configuración automática del scheduler:
- Sincronización incremental: Cada 6 horas
- Sincronización completa: Diariamente a las 2:00 AM
- Monitoreo continuo: Cada 30 segundos
```

## 🎯 **Resumen: Operación Completamente Automática**

### **Lo que TÚ haces:**
1. ✅ Configurar credenciales de BD
2. ✅ Documentar tus tablas (JSON rich documentation)  
3. ✅ Ejecutar ETL Service

### **Lo que hace AUTOMÁTICAMENTE el ETL:**
1. 🔍 **Descubre** esquema completo de BD
2. 🧠 **Analiza** con IA + documentación rica
3. ⚙️ **Genera** queries optimizadas automáticamente
4. 📦 **Extrae** datos por lotes inteligentes
5. 🔄 **Transforma** con IA contextual
6. 📚 **Ingesta** al Knowledge Base
7. 🕐 **Programa** sincronizaciones automáticas
8. 📊 **Monitorea** calidad y métricas

## 🚀 **Queries Reales que Verás en los Logs:**

Cuando ejecutes el ETL Service, verás en los logs queries como:

```bash
# Logs reales que aparecerán:
[INFO] Introspectando esquema de BD 'requisicion_db'...
[INFO] Query: SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE...
[INFO] Encontradas 40 tablas, analizando con IA...
[INFO] Tabla 'requisition': Relevancia 8.5/10, Prioridad CRÍTICA
[INFO] Generando query: SELECT r.*, c.name FROM requisition r JOIN company c...
[INFO] Extrayendo lote 1: 500 registros de 'requisition'
[INFO] Query: SELECT r.*, c.name FROM requisition r JOIN company c... LIMIT 500 OFFSET 0
[INFO] Transformando 500 registros con IA...
[INFO] Ingresando 500 documentos al Knowledge Base...
```

**¡El ETL es 100% automático! Solo necesitas configurarlo una vez y funciona solo.** 🤖✨
