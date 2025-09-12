# 🗺️ Estrategia de Mapeo y Evaluación de BD para ETL

## 🎯 **Estrategias de Mapeo de Tablas**

### **Opción 1: Evaluación Automática + IA (RECOMENDADO)**

**🧠 Funcionamiento Inteligente:**
1. **Introspección automática** de todas las tablas
2. **IA evalúa relevancia** de cada tabla para KB técnico
3. **Configuración dinámica** basada en contenido real
4. **Auto-priorización** según valor técnico

### **Opción 2: Configuración Manual Selectiva**

**⚙️ Control Granular:**
- Mapeo explícito de tablas importantes
- Configuración por tabla (campos, filtros, transformaciones)
- Mantenimiento manual pero predictible

### **Opción 3: Híbrida Inteligente + Manual**

**🎯 Lo mejor de ambos mundos:**
- IA sugiere configuración inicial
- Admin revisa y ajusta
- Auto-adaptación continua con supervisión

## 🔍 **Implementación: Evaluador IA de Tablas**

### **1. Descubridor Automático de Esquema**

```python
class DatabaseSchemaAnalyzer:
    def __init__(self):
        self.mysql = MySQLClient()
        self.llm = LLMClient(agent="schema_analyzer")
    
    def discover_and_analyze_schema(self) -> Dict[str, Any]:
        """Descubre y analiza todas las tablas automáticamente"""
        
        # 1. Obtener esquema completo
        schema = self.mysql.introspect_schema()
        
        # 2. Evaluar cada tabla con IA
        table_evaluations = {}
        
        for table_name, table_meta in schema["tables"].items():
            evaluation = self._evaluate_table_with_ai(table_name, table_meta)
            table_evaluations[table_name] = evaluation
            
        # 3. Priorizar y recomendar configuración
        recommendations = self._generate_etl_recommendations(table_evaluations)
        
        return {
            "schema": schema,
            "evaluations": table_evaluations,
            "recommendations": recommendations
        }
    
    def _evaluate_table_with_ai(self, table_name: str, table_meta: Dict) -> Dict:
        """IA evalúa relevancia de tabla para KB técnico"""
        
        # Construir descripción de tabla
        columns = table_meta.get("columns", [])
        column_desc = ", ".join([f"{c['name']} ({c['type']})" for c in columns[:10]])
        
        prompt = f"""
        Analiza esta tabla de base de datos y evalúa su relevancia para un Knowledge Base técnico de equipos industriales:

        TABLA: {table_name}
        COLUMNAS: {column_desc}
        
        Evalúa en estas dimensiones:
        
        1. RELEVANCIA TÉCNICA (0-10):
           - ¿Contiene información técnica útil?
           - ¿Datos de equipos, servicios, fallas, reparaciones?
           
        2. VALOR PARA IA (0-10):
           - ¿Información útil para predicción de fallas?
           - ¿Datos de diagnóstico/resolución?
           
        3. CALIDAD DE DATOS (0-10):
           - ¿Columnas descriptivas vs solo IDs?
           - ¿Texto libre vs códigos?
           
        4. PRIORIDAD ETL (ALTA/MEDIA/BAJA):
           - ¿Qué tan importante para el primer despliegue?
           
        5. ESTRATEGIA SUGERIDA:
           - full_table: Toda la tabla es relevante
           - filtered: Solo algunos registros (especifica filtros)
           - joined: Necesita JOIN con otras tablas
           - skip: No relevante para KB
           
        6. CAMPOS CLAVE:
           - ¿Qué columnas contienen la información más valiosa?
           
        7. TRANSFORMACIÓN SUGERIDA:
           - ¿Cómo convertir los datos en texto técnico narrativo?

        RESPONDE EN JSON:
        {{
          "relevancia_tecnica": 8,
          "valor_ia": 7,
          "calidad_datos": 6,
          "prioridad": "ALTA",
          "estrategia": "filtered",
          "filtros_sugeridos": "WHERE status != 'deleted' AND created_at > '2023-01-01'",
          "campos_clave": ["description", "equipment_model", "issue_type", "resolution"],
          "transformacion": "Combinar equipment_model + issue_type + resolution en narrativa técnica",
          "razonamiento": "Tabla con datos de servicios técnicos, alta relevancia para predicción"
        }}
        """
        
        try:
            response = self.llm.chat_completion([{"role": "user", "content": prompt}])
            # Parse JSON response
            evaluation = self._parse_evaluation_response(response)
            
            # Añadir metadatos adicionales
            evaluation.update({
                "row_count_estimate": self._estimate_table_size(table_name),
                "has_timestamps": self._has_timestamp_columns(table_meta),
                "text_columns": self._identify_text_columns(table_meta)
            })
            
            return evaluation
            
        except Exception as e:
            # Fallback evaluation básico
            return self._fallback_evaluation(table_name, table_meta)
```

### **2. Generador de Configuración ETL**

```python
class ETLConfigGenerator:
    def generate_table_configs(self, evaluations: Dict) -> Dict[str, Any]:
        """Genera configuración ETL basada en evaluaciones IA"""
        
        configs = {}
        
        for table_name, eval_data in evaluations.items():
            prioridad = eval_data.get("prioridad", "BAJA")
            relevancia = eval_data.get("relevancia_tecnica", 0)
            
            # Solo configurar tablas relevantes
            if prioridad in ["ALTA", "MEDIA"] and relevancia >= 6:
                config = {
                    "enabled": True,
                    "priority": prioridad,
                    "strategy": eval_data.get("estrategia", "full_table"),
                    "extraction": self._build_extraction_config(table_name, eval_data),
                    "transformation": self._build_transformation_config(table_name, eval_data),
                    "metadata": self._build_metadata_config(table_name, eval_data)
                }
                configs[table_name] = config
                
        return configs
    
    def _build_extraction_config(self, table_name: str, eval_data: Dict) -> Dict:
        """Configuración de extracción por tabla"""
        
        config = {
            "table": table_name,
            "batch_size": 500,
            "order_by": None,
            "where_clause": eval_data.get("filtros_sugeridos", ""),
            "key_columns": eval_data.get("campos_clave", [])
        }
        
        # Auto-detectar columna de timestamp para incremental
        if eval_data.get("has_timestamps"):
            config["incremental_column"] = self._detect_timestamp_column(table_name)
            
        # Ajustar batch size según tamaño estimado
        estimated_rows = eval_data.get("row_count_estimate", 1000)
        if estimated_rows > 100000:
            config["batch_size"] = 1000
        elif estimated_rows < 1000:
            config["batch_size"] = 100
            
        return config
    
    def _build_transformation_config(self, table_name: str, eval_data: Dict) -> Dict:
        """Configuración de transformación IA por tabla"""
        
        return {
            "ai_prompt_template": self._generate_transformation_prompt(table_name, eval_data),
            "target_format": "technical_narrative",
            "metadata_extraction": {
                "auto_detect_entities": True,
                "extract_brands": True,
                "extract_models": True,
                "extract_categories": True
            },
            "quality_filters": {
                "min_text_length": 50,
                "required_fields": eval_data.get("campos_clave", [])[:3]
            }
        }
```

### **3. Configuración Dinámica Inteligente**

```python
# configs/etl_dynamic.json (generado automáticamente)
{
  "discovery_settings": {
    "auto_discovery_enabled": true,
    "reevaluate_interval_days": 30,
    "min_relevance_threshold": 6,
    "priority_thresholds": {
      "ALTA": 8,
      "MEDIA": 6,
      "BAJA": 4
    }
  },
  
  "table_configs": {
    "services": {
      "enabled": true,
      "priority": "ALTA",
      "strategy": "filtered",
      "extraction": {
        "table": "services",
        "incremental_column": "updated_at",
        "where_clause": "WHERE status IN ('completed', 'in_progress') AND created_at > '2023-01-01'",
        "key_columns": ["service_description", "equipment_brand", "equipment_model", "issue_description", "resolution", "technician_notes"],
        "batch_size": 500
      },
      "transformation": {
        "ai_prompt_template": "services_to_technical_narrative.prompt",
        "target_format": "technical_narrative",
        "metadata_extraction": {
          "auto_detect_entities": true,
          "extract_brands": true,
          "extract_models": true
        }
      }
    },
    
    "activity_services": {
      "enabled": true,
      "priority": "MEDIA",
      "strategy": "joined",
      "extraction": {
        "join_with": ["services", "equipments"],
        "sql_template": "SELECT a.*, s.equipment_model, e.brand FROM activity_services a JOIN services s ON a.service_id = s.id JOIN equipments e ON s.equipment_id = e.id",
        "incremental_column": "a.created_at",
        "batch_size": 300
      }
    },
    
    "service_logs": {
      "enabled": true,
      "priority": "MEDIA",
      "strategy": "filtered",
      "extraction": {
        "where_clause": "WHERE log_type IN ('diagnostic', 'resolution', 'parts_replaced')",
        "key_columns": ["log_message", "log_type", "created_by"]
      }
    }
  },
  
  "ignored_tables": [
    "user_sessions",
    "audit_logs", 
    "system_config",
    "migrations"
  ]
}
```

## 🎯 **Workflow de Implementación**

### **Paso 1: Descubrimiento Automático**

```bash
# Endpoint para ejecutar descubrimiento
POST /api/v1/etl/discover-schema

# Respuesta
{
  "discovered_tables": 15,
  "relevant_tables": 8,
  "high_priority": 3,
  "medium_priority": 3,
  "low_priority": 2,
  "config_generated": true
}
```

### **Paso 2: Revisión y Ajuste Manual**

```bash
# Ver configuración generada
GET /api/v1/etl/config

# Modificar configuración específica
PUT /api/v1/etl/config/services
{
  "extraction": {
    "where_clause": "WHERE status = 'completed' AND priority = 'high'"
  }
}
```

### **Paso 3: Validación y Testing**

```bash
# Probar extracción de una tabla específica
POST /api/v1/etl/test-table/services
{
  "limit": 10,
  "dry_run": true
}

# Ver preview de transformación IA
GET /api/v1/etl/preview/services?limit=3
```

### **Paso 4: Ejecución Controlada**

```bash
# Ejecutar ETL solo para tablas de alta prioridad
POST /api/v1/etl/sync
{
  "priority_filter": ["ALTA"],
  "tables": ["services", "equipments"]
}
```

## 📊 **Dashboard de Mapeo**

### **Vista de Evaluación de Tablas:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    📊 ANÁLISIS DE TABLAS BD                     │
├─────────────────────────────────────────────────────────────────┤
│ Tabla           │ Relevancia │ Valor IA │ Prioridad │ Estado    │
├─────────────────────────────────────────────────────────────────┤
│ services        │    9/10    │   8/10   │   ALTA    │ ✅ Config │
│ equipments      │    8/10    │   7/10   │   ALTA    │ ✅ Config │
│ activity_svcs   │    7/10    │   6/10   │   MEDIA   │ ✅ Config │
│ service_logs    │    6/10    │   7/10   │   MEDIA   │ ✅ Config │
│ customers       │    4/10    │   3/10   │   BAJA    │ ⏸️ Skip   │
│ user_sessions   │    1/10    │   1/10   │   SKIP    │ ❌ Ignore │
├─────────────────────────────────────────────────────────────────┤
│ Total tablas: 12 │ Relevantes: 8 │ Configuradas: 6 │ Activas: 4│
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 **Comandos de Control**

### **Gestión de Configuración:**

```bash
# Re-descubrir y re-evaluar esquema
curl -X POST "http://localhost:8000/api/v1/etl/rediscover"

# Ver tabla específica
curl "http://localhost:8000/api/v1/etl/table-analysis/services" | jq .

# Habilitar/deshabilitar tabla
curl -X PUT "http://localhost:8000/api/v1/etl/table/customers/disable"

# Ver estadísticas de mapeo
curl "http://localhost:8000/api/v1/etl/mapping-stats" | jq .
```

## 🎯 **Ventajas de Esta Estrategia**

### **🤖 Inteligencia Automática:**
- **Auto-descubrimiento** de todas las tablas
- **Evaluación IA** de relevancia técnica
- **Configuración automática** optimizada

### **🎛️ Control Granular:**
- **Revisión manual** de configuraciones IA
- **Ajustes específicos** por tabla
- **Enable/disable** dinámico

### **📈 Escalabilidad:**
- **Re-evaluación periódica** de nuevas tablas
- **Adaptación automática** a cambios de esquema
- **Optimización continua** basada en uso

### **🔍 Transparencia:**
- **Dashboard visual** del mapeo
- **Explicaciones IA** de decisiones
- **Métricas** de efectividad por tabla

**¿Te parece bien este enfoque híbrido? ¿Quieres que implemente primero el Descubridor Automático para evaluar tu BD actual?** 🚀
