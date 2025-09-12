# 📘 Guía Completa: ETL Inteligente BD → KB

## 🎯 **Visión General del Sistema**

Este sistema permite **extraer automáticamente** datos de bases de datos MySQL y **transformarlos inteligentemente** usando IA para alimentar el Knowledge Base técnico. La IA analiza el contexto de negocio y optimiza la extracción para obtener el máximo valor predictivo.

### **🔄 Flujo Principal:**
```
BD MySQL → Auto-Documentación → Evaluación IA → Configuración ETL → Extracción → Transformación IA → KB Optimizado
```

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            🏗️ ARQUITECTURA ETL IA                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐ │
│  │   BD MySQL  │───▶│ Context Extractor │───▶│     Schema Analyzer IA        │ │
│  │             │    │                  │    │                               │ │
│  │ • services  │    │ • Business Logic │    │ • Relevance Scoring           │ │
│  │ • equipments│    │ • Data Sampling  │    │ • Strategy Selection          │ │
│  │ • customers │    │ • Relationship   │    │ • Transformation Planning     │ │
│  │ • logs      │    │   Detection      │    │ • Priority Assignment        │ │
│  └─────────────┘    └──────────────────┘    └─────────────────────────────────┘ │
│         │                     │                              │                  │
│         ▼                     ▼                              ▼                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐ │
│  │Manual Config│    │ AI Configuration │    │      ETL Pipeline              │ │
│  │             │    │                  │    │                               │ │
│  │ • Business  │───▶│ • Table Configs  │───▶│ • Incremental Extraction      │ │
│  │   Rules     │    │ • JOIN Strategies│    │ • AI Transformation           │ │
│  │ • Priorities│    │ • Filter Rules   │    │ • Quality Validation          │ │
│  │ • Overrides │    │ • Prompts        │    │ • KB Ingestion               │ │
│  └─────────────┘    └──────────────────┘    └─────────────────────────────────┘ │
│                               │                              │                  │
│                               ▼                              ▼                  │
│                    ┌──────────────────┐    ┌─────────────────────────────────┐ │
│                    │   Monitoring     │    │      Knowledge Base            │ │
│                    │                  │    │                               │ │
│                    │ • Quality Metrics│    │ • Technical Documents          │ │
│                    │ • Success Rates  │    │ • Auto-Generated Metadata     │ │
│                    │ • Error Tracking │    │ • Searchable & Filtered       │ │
│                    │ • Performance    │    │ • Auto-Learning Taxonomy      │ │
│                    └──────────────────┘    └─────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📚 **Paso a Paso: Implementación Completa**

### **🚀 PASO 1: Preparación del Entorno**

#### **1.1 Configuración de Variables de Entorno**

```bash
# Agregar a .env
# ETL Configuration
ETL_ENABLED=true
ETL_INCREMENTAL_HOURS=2
ETL_FULL_SYNC_TIME=02:00
ETL_BATCH_SIZE=500
ETL_RETRY_ATTEMPTS=3

# BD Principal (ya configurada)
MYSQL_HOST=tu-rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=usuario_ro
MYSQL_PASSWORD=******
MYSQL_DATABASE=mi_db

# AI Transformation
ETL_LLM_MODEL=gpt-4o-mini
ETL_LLM_TEMPERATURE=0.1
ETL_MAX_DOCS_PER_BATCH=50

# Quality Monitoring
ETL_QUALITY_THRESHOLD=0.85
ETL_ALERT_EMAIL=admin@company.com
```

#### **1.2 Estructura de Archivos**

```
fixeatAI/
├── services/etl/
│   ├── __init__.py
│   ├── context_extractor.py      # Auto-documentación BD
│   ├── schema_analyzer.py        # Evaluación IA de tablas
│   ├── config_generator.py       # Generación de configuraciones
│   ├── pipeline.py               # Pipeline principal ETL
│   ├── scheduler.py              # Programador de tareas
│   └── monitor.py                # Monitor de calidad
├── configs/etl/
│   ├── bd_business_context.json  # Contexto manual de BD
│   ├── etl_dynamic_config.json   # Configuración generada por IA
│   └── table_mappings.json       # Mapeos específicos
└── docs/etl/
    ├── bd_analysis_report.md     # Reporte de análisis
    └── implementation_log.md     # Log de implementación
```

### **🔍 PASO 2: Auto-Documentación de la BD**

#### **2.1 Ejecutar Context Extractor**

```bash
# Endpoint para descubrir y documentar BD automáticamente
curl -X POST "http://localhost:8000/api/v1/etl/discover-context" | jq .
```

**Qué hace:**
- Introspecciona TODAS las tablas de la BD
- IA analiza nombres, columnas y muestra de datos
- Infiere propósito de negocio de cada tabla
- Detecta relaciones semánticas
- Genera documentación automática

#### **2.2 Revisar Documentación Generada**

```bash
# Ver análisis completo de contexto
curl "http://localhost:8000/api/v1/etl/context-report" | jq .

# Ver análisis de tabla específica
curl "http://localhost:8000/api/v1/etl/table-context/services" | jq .
```

**Ejemplo de Output:**
```json
{
  "database_overview": {
    "business_type": "Servicios técnicos de equipos industriales",
    "industry_context": "Reparación y mantenimiento de equipos de panadería/cocina",
    "main_entities": ["equipments", "services", "customers", "technicians"],
    "data_flow": "Customer reports issue → Service created → Technician assigned → Resolution documented"
  },
  "table_analysis": {
    "services": {
      "business_purpose": "Órdenes de servicio técnico con diagnósticos y resoluciones",
      "ai_relevance": 9,
      "critical_fields": ["issue_description", "resolution", "parts_used"],
      "relationships": ["equipments.id", "customers.id"],
      "kb_value": "CRÍTICO: Casos reales de falla y resolución para entrenamiento IA"
    }
  }
}
```

#### **2.3 Enriquecer con Contexto Manual**

```bash
# Editar contexto manual específico del negocio
nano configs/etl/bd_business_context.json
```

**Complementar con:**
- Reglas de negocio específicas
- Definiciones precisas de campos críticos
- Prioridades del negocio
- Casos de uso específicos

### **🤖 PASO 3: Evaluación IA de Tablas**

#### **3.1 Ejecutar Análisis IA**

```bash
# IA evalúa todas las tablas con contexto completo
curl -X POST "http://localhost:8000/api/v1/etl/analyze-schema" | jq .
```

**Qué evalúa la IA:**
- **Relevancia Técnica (0-10)**: ¿Útil para diagnóstico de equipos?
- **Valor Predictivo (0-10)**: ¿Útil para predecir fallas?
- **Calidad Narrativa (0-10)**: ¿Datos ricos para contenido técnico?
- **Prioridad ETL**: CRÍTICA/ALTA/MEDIA/BAJA
- **Estrategia**: full_table/filtered/joined/enriched

#### **3.2 Revisar Evaluaciones IA**

```bash
# Ver evaluación completa
curl "http://localhost:8000/api/v1/etl/evaluation-report" | jq .

# Dashboard de evaluaciones
curl "http://localhost:8000/api/v1/etl/evaluation-dashboard" | jq .
```

**Ejemplo de Evaluación:**
```json
{
  "services": {
    "relevancia_tecnica": 9,
    "valor_predictivo": 8,
    "calidad_narrativa": 9,
    "prioridad": "CRÍTICA",
    "estrategia": "joined",
    "join_recomendados": ["equipments", "customers"],
    "transformacion": "Narrativa técnica completa con contexto de equipo y resolución",
    "razonamiento": "Tabla central del negocio con casos reales de falla y resolución"
  }
}
```

### **⚙️ PASO 4: Generación de Configuración ETL**

#### **4.1 Generar Configuraciones Automáticas**

```bash
# IA genera configuración ETL optimizada
curl -X POST "http://localhost:8000/api/v1/etl/generate-config" | jq .
```

**Configuración Generada:**
```json
{
  "services": {
    "enabled": true,
    "priority": "CRÍTICA",
    "extraction": {
      "strategy": "joined",
      "sql_template": "SELECT s.*, e.brand, e.model, e.equipment_type FROM services s JOIN equipments e ON s.equipment_id = e.id",
      "incremental_column": "s.updated_at",
      "where_clause": "WHERE s.status IN ('completed', 'in_progress')",
      "batch_size": 500
    },
    "transformation": {
      "ai_prompt": "services_to_technical_narrative.prompt",
      "metadata_extraction": ["brand", "model", "equipment_type", "issue_type"],
      "quality_filters": {"min_text_length": 100}
    }
  }
}
```

#### **4.2 Revisar y Ajustar Configuración**

```bash
# Ver configuración completa generada
curl "http://localhost:8000/api/v1/etl/config" | jq .

# Modificar configuración específica
curl -X PUT "http://localhost:8000/api/v1/etl/config/services" \
  -d '{"extraction": {"where_clause": "WHERE status = \"completed\" AND priority = \"high\""}}' | jq .
```

### **🔄 PASO 5: Ejecutar ETL Pipeline**

#### **5.1 Testing Previo**

```bash
# Probar extracción de tabla específica (dry run)
curl -X POST "http://localhost:8000/api/v1/etl/test-extraction/services?limit=10&dry_run=true" | jq .

# Ver preview de transformación IA
curl "http://localhost:8000/api/v1/etl/preview-transformation/services?limit=3" | jq .
```

#### **5.2 Ejecución Controlada**

```bash
# Ejecutar ETL solo para tablas críticas
curl -X POST "http://localhost:8000/api/v1/etl/sync" \
  -d '{"priority_filter": ["CRÍTICA"], "tables": ["services"], "batch_size": 100}' | jq .

# Ejecutar ETL completo
curl -X POST "http://localhost:8000/api/v1/etl/sync-all" | jq .
```

#### **5.3 Monitoreo en Tiempo Real**

```bash
# Ver progreso del ETL
curl "http://localhost:8000/api/v1/etl/status" | jq .

# Ver logs en tiempo real
tail -f logs/etl.log

# Métricas de calidad
curl "http://localhost:8000/api/v1/etl/metrics" | jq .
```

### **📊 PASO 6: Validación y Optimización**

#### **6.1 Verificar Resultados en KB**

```bash
# Ver documentos ingresados
curl -X POST "http://localhost:7070/tools/kb_search" \
  -d '{"query": "test", "top_k": 10}' | jq '.hits | length'

# Verificar taxonomía aprendida
curl "http://localhost:7070/tools/taxonomy/stats" | jq .

# Búsqueda específica
curl -X POST "http://localhost:7070/tools/kb_search" \
  -d '{"query": "RATIONAL horno problema", "where": {"brand": "RATIONAL"}}' | jq .
```

#### **6.2 Optimizar Configuraciones**

```bash
# Analizar métricas de calidad por tabla
curl "http://localhost:8000/api/v1/etl/quality-report" | jq .

# Ajustar configuración basada en resultados
curl -X PUT "http://localhost:8000/api/v1/etl/config/services" \
  -d '{"transformation": {"quality_filters": {"min_text_length": 150}}}' | jq .
```

## 🔄 **Agregar Nueva Base de Datos: Paso a Paso**

### **📋 Caso: Agregar BD de Inventarios**

#### **PASO 1: Configuración de Conexión**

```bash
# Agregar a .env
# Segunda BD - Inventarios
MYSQL_INVENTORY_HOST=inventarios-rds.amazonaws.com
MYSQL_INVENTORY_PORT=3306
MYSQL_INVENTORY_USER=readonly_user
MYSQL_INVENTORY_PASSWORD=******
MYSQL_INVENTORY_DATABASE=inventarios_db
```

#### **PASO 2: Configurar Cliente MySQL**

```python
# services/db/mysql_inventory.py
class MySQLInventoryClient(MySQLClient):
    def __init__(self):
        # Override para usar variables de inventario
        self.host = os.getenv("MYSQL_INVENTORY_HOST")
        self.user = os.getenv("MYSQL_INVENTORY_USER")
        # ... resto de configuración específica
```

#### **PASO 3: Documentar Contexto de Negocio**

```json
// configs/etl/inventarios_business_context.json
{
  "database_metadata": {
    "business_domain": "Gestión de inventarios y repuestos",
    "industry": "Distribución de repuestos industriales",
    "data_classification": "Logística y stock",
    "relationship_with_main_db": "inventory.part_id → main.services.parts_used"
  },
  
  "table_documentation": {
    "parts_inventory": {
      "business_purpose": "Stock actual de repuestos por bodega",
      "critical_fields": {
        "part_number": "Código único del repuesto - CRÍTICO para matching",
        "part_name": "Descripción del repuesto - CRÍTICO para IA",
        "equipment_compatibility": "Equipos compatibles - CRÍTICO para predicción",
        "stock_quantity": "Cantidad disponible - útil para alertas",
        "supplier": "Proveedor - contexto adicional"
      },
      "ai_usage": {
        "prediction_enhancement": "Enriquecer predicciones con disponibilidad de repuestos",
        "metadata_source": ["part_number", "equipment_compatibility"],
        "cross_reference": "Vincular con services.parts_used"
      }
    }
  }
}
```

#### **PASO 4: Ejecutar Descubrimiento**

```bash
# Descubrir nueva BD
curl -X POST "http://localhost:8000/api/v1/etl/discover-context" \
  -d '{"database": "inventory", "config_source": "MYSQL_INVENTORY"}' | jq .

# Analizar con IA
curl -X POST "http://localhost:8000/api/v1/etl/analyze-schema" \
  -d '{"database": "inventory"}' | jq .
```

#### **PASO 5: Configurar Relaciones Cross-BD**

```json
// Configuración de relaciones entre BDs
{
  "cross_database_relationships": {
    "main_services_to_inventory": {
      "type": "enrichment",
      "source": "main.services.parts_used",
      "target": "inventory.parts_inventory.part_number",
      "purpose": "Enriquecer predicciones con disponibilidad de stock",
      "transformation": "LEFT JOIN para obtener info de stock en predicciones"
    }
  }
}
```

#### **PASO 6: ETL Multi-BD**

```bash
# ETL coordinado entre múltiples BDs
curl -X POST "http://localhost:8000/api/v1/etl/sync-multi-db" \
  -d '{
    "databases": ["main", "inventory"],
    "cross_reference": true,
    "enrichment_mode": true
  }' | jq .
```

## 🛠️ **Comandos de Administración**

### **🔧 Gestión Diaria**

```bash
# Estado general del sistema
curl "http://localhost:8000/api/v1/etl/health" | jq .

# Ejecutar sync incremental manual
curl -X POST "http://localhost:8000/api/v1/etl/sync-incremental" | jq .

# Ver últimas métricas
curl "http://localhost:8000/api/v1/etl/dashboard" | jq .

# Pausar/reanudar ETL
curl -X POST "http://localhost:8000/api/v1/etl/pause" | jq .
curl -X POST "http://localhost:8000/api/v1/etl/resume" | jq .
```

### **🔍 Debugging y Troubleshooting**

```bash
# Ver errores recientes
curl "http://localhost:8000/api/v1/etl/errors?limit=10" | jq .

# Reprocessar tabla con errores
curl -X POST "http://localhost:8000/api/v1/etl/retry/services" | jq .

# Ver logs detallados
tail -f logs/etl_detailed.log | grep ERROR

# Test de conectividad BD
curl "http://localhost:8000/api/v1/etl/test-connection" | jq .
```

### **📊 Reporting y Analytics**

```bash
# Reporte de calidad semanal
curl "http://localhost:8000/api/v1/etl/weekly-report" | jq .

# Estadísticas de KB growth
curl "http://localhost:8000/api/v1/etl/kb-growth-stats" | jq .

# Performance benchmarks
curl "http://localhost:8000/api/v1/etl/performance-report" | jq .
```

## 🎯 **Casos de Uso Comunes**

### **🔄 Caso 1: Agregar Nueva Tabla a BD Existente**

```bash
# 1. Re-discover schema
curl -X POST "http://localhost:8000/api/v1/etl/rediscover" | jq .

# 2. Ver nueva tabla detectada
curl "http://localhost:8000/api/v1/etl/new-tables" | jq .

# 3. Evaluar con IA
curl -X POST "http://localhost:8000/api/v1/etl/evaluate-table/nueva_tabla" | jq .

# 4. Configurar si es relevante
curl -X PUT "http://localhost:8000/api/v1/etl/config/nueva_tabla" \
  -d '{"enabled": true, "priority": "MEDIA"}' | jq .
```

### **🔄 Caso 2: Migrar BD a Nuevo Servidor**

```bash
# 1. Actualizar variables de entorno
export MYSQL_HOST=nuevo-servidor.com

# 2. Test conectividad
curl "http://localhost:8000/api/v1/etl/test-connection" | jq .

# 3. Re-validar schema
curl -X POST "http://localhost:8000/api/v1/etl/validate-schema" | jq .

# 4. Sync completo desde nueva ubicación
curl -X POST "http://localhost:8000/api/v1/etl/full-resync" | jq .
```

### **🔄 Caso 3: Optimizar Performance**

```bash
# 1. Analizar bottlenecks
curl "http://localhost:8000/api/v1/etl/performance-analysis" | jq .

# 2. Ajustar batch sizes
curl -X PUT "http://localhost:8000/api/v1/etl/config/services" \
  -d '{"extraction": {"batch_size": 1000}}' | jq .

# 3. Optimizar horarios
curl -X PUT "http://localhost:8000/api/v1/etl/schedule" \
  -d '{"incremental_hours": 1, "full_sync_time": "01:00"}' | jq .
```

## 📋 **Checklist de Implementación**

### **✅ Pre-Implementación**
- [ ] Variables de entorno configuradas
- [ ] Conexión BD validada
- [ ] Permisos de lectura confirmados
- [ ] Backup de configuraciones existentes

### **✅ Implementación**
- [ ] Context Extractor ejecutado
- [ ] Documentación manual completada
- [ ] Evaluación IA revisada
- [ ] Configuración ETL ajustada
- [ ] Testing en tablas pequeñas exitoso

### **✅ Post-Implementación**
- [ ] ETL completo ejecutado
- [ ] KB poblado correctamente
- [ ] Taxonomía auto-aprendida
- [ ] Métricas de calidad validadas
- [ ] Scheduler configurado
- [ ] Monitoring activo

### **✅ Mantenimiento**
- [ ] Documentación actualizada
- [ ] Reportes de calidad revisados
- [ ] Optimizaciones aplicadas
- [ ] Backup de configuraciones

## 🚨 **Troubleshooting Común**

### **🔧 Problemas de Conexión**
```bash
# Error: Connection refused
# Solución: Verificar host, puerto, credenciales
curl "http://localhost:8000/api/v1/etl/test-connection" | jq .
```

### **🔧 Problemas de Performance**
```bash
# Error: Timeout en ETL
# Solución: Reducir batch_size, optimizar queries
curl -X PUT "http://localhost:8000/api/v1/etl/config/tabla" \
  -d '{"extraction": {"batch_size": 100}}' | jq .
```

### **🔧 Problemas de Calidad**
```bash
# Error: Documentos de baja calidad
# Solución: Ajustar filtros, mejorar prompts IA
curl "http://localhost:8000/api/v1/etl/quality-report" | jq .
```

**¡Con esta guía completa, cualquier desarrollador puede implementar, mantener y escalar el sistema ETL Inteligente!** 🚀📚
