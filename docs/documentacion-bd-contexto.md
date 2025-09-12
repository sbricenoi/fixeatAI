# 📚 Documentación de BD para Contexto IA Completo

## 🎯 **¿Por qué Documentar la BD?**

### **❌ Sin Contexto de Negocio:**
```
IA ve: "services" tabla con "equipment_id" + "issue_description"
IA piensa: "Tabla genérica de servicios, relevancia media"
```

### **✅ Con Contexto Completo:**
```
IA entiende: "services = Órdenes de servicio técnico de equipos industriales
- equipment_id → Equipos de panadería/cocina (hornos, laminadoras, etc.)
- issue_description → Problemas reportados por clientes
- resolution → Pasos de reparación ejecutados por técnicos
- parts_used → Repuestos utilizados en reparación
RELACIÓN: services.equipment_id → equipments.id (marca, modelo, tipo)
VALOR IA: CRÍTICO para predicción de fallas y sugerencia de repuestos"
```

## 🏗️ **Estrategia de Documentación Completa**

### **Nivel 1: Auto-Documentación Inteligente**
- **Análisis de nombres**: IA infiere propósito desde nombres de tablas/columnas
- **Detección de patrones**: Identifica relaciones y tipos de datos
- **Análisis de contenido**: Muestrea datos para entender contexto

### **Nivel 2: Contexto de Negocio Manual**
- **Propósito de cada tabla**: ¿Para qué se usa en el negocio?
- **Relaciones semánticas**: ¿Cómo se conectan conceptualmente?
- **Importancia relativa**: ¿Qué tan crítica es para el KB técnico?

### **Nivel 3: Metadatos Enriquecidos**
- **Diccionario de datos**: Definición precisa de cada campo
- **Reglas de negocio**: Filtros, validaciones, casos especiales
- **Ejemplos de uso**: Casos reales de cómo se usa la data

## 🔍 **Implementación: Auto-Documentador + Manual**

### **1. Extractor de Contexto Automático**

```python
class BusinessContextExtractor:
    def __init__(self):
        self.mysql = MySQLClient()
        self.llm = LLMClient(agent="context_analyzer")
    
    def extract_business_context(self) -> Dict[str, Any]:
        """Extrae contexto de negocio automáticamente desde la BD"""
        
        context = {
            "database_overview": self._analyze_database_purpose(),
            "table_analysis": {},
            "relationship_map": self._build_relationship_map(),
            "business_patterns": self._detect_business_patterns()
        }
        
        # Analizar cada tabla con contexto
        schema = self.mysql.introspect_schema()
        
        for table_name, table_meta in schema["tables"].items():
            table_context = self._analyze_table_context(table_name, table_meta)
            context["table_analysis"][table_name] = table_context
            
        return context
    
    def _analyze_database_purpose(self) -> Dict:
        """IA infiere el propósito general de la BD"""
        
        # Obtener lista de todas las tablas
        schema = self.mysql.introspect_schema()
        table_names = list(schema["tables"].keys())
        
        prompt = f"""
        Analiza estos nombres de tablas y determina el propósito del negocio:
        
        TABLAS: {', '.join(table_names)}
        
        Basándote en los nombres, infiere:
        1. ¿Qué tipo de negocio es? (ej: servicios técnicos, e-commerce, etc.)
        2. ¿Cuáles son las entidades principales del dominio?
        3. ¿Qué procesos de negocio maneja el sistema?
        4. ¿Cuál es el flujo principal de datos?
        
        RESPONDE EN JSON:
        {{
          "business_type": "Servicios técnicos de equipos industriales",
          "main_entities": ["equipments", "services", "customers", "technicians"],
          "business_processes": ["service_requests", "diagnostics", "repairs", "maintenance"],
          "data_flow": "Customer reports issue → Service created → Technician assigned → Work performed → Resolution documented",
          "industry_context": "Reparación y mantenimiento de equipos de panadería/cocina industrial"
        }}
        """
        
        response = self.llm.chat_completion([{"role": "user", "content": prompt}])
        return self._parse_json_response(response)
    
    def _analyze_table_context(self, table_name: str, table_meta: Dict) -> Dict:
        """Analiza contexto específico de cada tabla"""
        
        # Obtener muestra de datos reales
        sample_data = self._get_table_sample(table_name, limit=5)
        
        # Análisis de columnas
        columns = table_meta.get("columns", [])
        column_analysis = self._analyze_column_semantics(columns, sample_data)
        
        # Inferir propósito con IA
        purpose_analysis = self._infer_table_purpose(table_name, columns, sample_data)
        
        return {
            "business_purpose": purpose_analysis.get("purpose", ""),
            "data_type": purpose_analysis.get("data_type", ""),
            "critical_for_ai": purpose_analysis.get("ai_relevance", 0),
            "column_semantics": column_analysis,
            "sample_data": sample_data[:2],  # Solo 2 ejemplos por privacidad
            "relationships": self._analyze_table_relationships(table_name, table_meta),
            "business_rules": self._detect_business_rules(table_name, sample_data)
        }
    
    def _infer_table_purpose(self, table_name: str, columns: List, sample_data: List) -> Dict:
        """IA infiere propósito específico de la tabla"""
        
        column_names = [c["name"] for c in columns]
        sample_preview = json.dumps(sample_data[:2], ensure_ascii=False, indent=2) if sample_data else "Sin datos"
        
        prompt = f"""
        Analiza esta tabla en el contexto de un sistema de servicios técnicos:
        
        TABLA: {table_name}
        COLUMNAS: {', '.join(column_names)}
        MUESTRA DE DATOS:
        {sample_preview}
        
        Determina:
        1. PROPÓSITO DE NEGOCIO: ¿Para qué se usa esta tabla?
        2. TIPO DE DATOS: transaccional, maestra, logs, configuración, etc.
        3. RELEVANCIA PARA IA (0-10): ¿Qué tan útil para predicción técnica?
        4. ENTIDADES TÉCNICAS: ¿Contiene info de equipos, fallas, reparaciones?
        5. VALOR PARA KB: ¿Qué información aportaría al Knowledge Base?
        
        CONTEXTO: Sistema de servicios técnicos para equipos industriales de panadería/cocina
        
        RESPONDE EN JSON:
        {{
          "purpose": "Registra órdenes de servicio técnico con detalles de problemas y resoluciones",
          "data_type": "transaccional",
          "ai_relevance": 9,
          "technical_entities": ["equipment_failures", "repair_procedures", "parts_usage"],
          "kb_value": "Crítico: contiene casos reales de fallas y sus resoluciones para entrenar IA predictiva",
          "business_process": "service_management",
          "key_insights": "Cada registro representa un caso completo de diagnóstico y reparación"
        }}
        """
        
        response = self.llm.chat_completion([{"role": "user", "content": prompt}])
        return self._parse_json_response(response)
```

### **2. Documentación Manual Complementaria**

```python
# configs/bd_business_context.json
{
  "database_metadata": {
    "business_domain": "Servicios técnicos de equipos industriales",
    "industry": "Reparación y mantenimiento de equipos de panadería/cocina",
    "data_classification": "Operacional y técnico",
    "update_frequency": "Tiempo real durante servicios"
  },
  
  "table_documentation": {
    "services": {
      "business_purpose": "Órdenes de trabajo para servicios técnicos",
      "data_lifecycle": "Creado → En progreso → Completado/Cancelado",
      "critical_fields": {
        "equipment_id": "Referencia al equipo atendido (FK a equipments)",
        "issue_description": "Problema reportado por cliente - CRÍTICO para IA",
        "resolution": "Pasos realizados por técnico - CRÍTICO para KB",
        "parts_used": "Lista de repuestos utilizados - CRÍTICO para predicción",
        "technician_id": "Técnico asignado - relevante para contexto",
        "status": "Estado actual del servicio"
      },
      "business_rules": {
        "status_flow": "pending → in_progress → completed/cancelled",
        "required_completion": "resolution y parts_used obligatorios al completar",
        "data_retention": "Histórico completo para análisis de tendencias"
      },
      "ai_usage": {
        "prediction_input": ["equipment_id", "issue_description", "equipment_brand"],
        "training_data": ["issue_description", "resolution", "parts_used"],
        "metadata_source": ["technician_id", "service_date", "priority"]
      }
    },
    
    "equipments": {
      "business_purpose": "Catálogo maestro de equipos industriales",
      "critical_fields": {
        "brand": "Marca del equipo - CRÍTICO para filtros KB",
        "model": "Modelo específico - CRÍTICO para predicción",
        "equipment_type": "Categoría (horno, laminadora, etc.) - CRÍTICO para taxonomía",
        "installation_date": "Fecha instalación - relevante para patrones de falla",
        "customer_id": "Cliente propietario - contexto del entorno"
      },
      "ai_usage": {
        "entity_extraction": ["brand", "model", "equipment_type"],
        "failure_patterns": ["installation_date", "equipment_type"],
        "context_enrichment": ["customer_location", "usage_intensity"]
      }
    }
  },
  
  "relationship_semantics": {
    "services_equipments": {
      "type": "one_to_many",
      "business_meaning": "Un equipo puede tener múltiples servicios a lo largo del tiempo",
      "ai_relevance": "CRÍTICO - permite análisis histórico de fallas por equipo",
      "join_strategy": "INNER JOIN para servicios activos, LEFT JOIN para análisis completo"
    },
    
    "services_customers": {
      "type": "many_to_one", 
      "business_meaning": "Múltiples servicios pueden ser del mismo cliente",
      "ai_relevance": "MEDIO - contexto del entorno operativo",
      "pattern": "Clientes industriales con múltiples equipos"
    }
  },
  
  "extraction_priorities": {
    "high_priority": {
      "tables": ["services", "equipments", "activity_services"],
      "reason": "Contienen información técnica directamente relevante para IA"
    },
    "medium_priority": {
      "tables": ["service_logs", "technicians", "customers"],
      "reason": "Proveen contexto complementario importante"
    },
    "low_priority": {
      "tables": ["user_sessions", "audit_logs"],
      "reason": "Datos operacionales sin valor técnico para KB"
    }
  }
}
```

### **3. Generador de Contexto Enriquecido**

```python
class ContextEnrichedAnalyzer(DatabaseSchemaAnalyzer):
    def __init__(self):
        super().__init__()
        self.context_extractor = BusinessContextExtractor()
        self.manual_context = self._load_manual_context()
    
    def analyze_with_full_context(self) -> Dict[str, Any]:
        """Análisis completo con contexto automático + manual"""
        
        # 1. Extraer contexto automático
        auto_context = self.context_extractor.extract_business_context()
        
        # 2. Combinar con contexto manual
        enriched_context = self._merge_contexts(auto_context, self.manual_context)
        
        # 3. Análisis IA con contexto completo
        table_evaluations = {}
        
        for table_name, table_meta in enriched_context["table_analysis"].items():
            # Evaluación IA con contexto rico
            evaluation = self._evaluate_table_with_context(
                table_name, 
                table_meta,
                enriched_context["database_overview"],
                enriched_context["relationship_map"]
            )
            table_evaluations[table_name] = evaluation
            
        return {
            "context": enriched_context,
            "evaluations": table_evaluations,
            "recommendations": self._generate_context_aware_recommendations(table_evaluations)
        }
    
    def _evaluate_table_with_context(self, table_name: str, table_context: Dict, 
                                   db_overview: Dict, relationships: Dict) -> Dict:
        """Evaluación IA con contexto completo de negocio"""
        
        prompt = f"""
        Evalúa esta tabla con CONTEXTO COMPLETO de negocio:
        
        === CONTEXTO DE NEGOCIO ===
        Tipo de Negocio: {db_overview.get('business_type', 'N/A')}
        Industria: {db_overview.get('industry_context', 'N/A')}
        Proceso Principal: {db_overview.get('data_flow', 'N/A')}
        
        === TABLA A EVALUAR ===
        Nombre: {table_name}
        Propósito de Negocio: {table_context.get('business_purpose', 'N/A')}
        Tipo de Datos: {table_context.get('data_type', 'N/A')}
        Entidades Técnicas: {table_context.get('technical_entities', [])}
        Valor para KB: {table_context.get('kb_value', 'N/A')}
        
        === RELACIONES ===
        {json.dumps(table_context.get('relationships', {}), indent=2)}
        
        === MUESTRA DE DATOS ===
        {json.dumps(table_context.get('sample_data', []), ensure_ascii=False, indent=2)}
        
        Con este CONTEXTO COMPLETO, evalúa:
        
        1. RELEVANCIA TÉCNICA (0-10): ¿Qué tan importante para diagnóstico de equipos?
        2. VALOR PREDICTIVO (0-10): ¿Útil para predecir fallas futuras?
        3. CALIDAD NARRATIVA (0-10): ¿Datos ricos para generar contenido técnico?
        4. PRIORIDAD ETL: CRÍTICA/ALTA/MEDIA/BAJA
        5. ESTRATEGIA EXTRACCIÓN: 
           - full_table: Toda la tabla
           - filtered: Con filtros específicos  
           - joined: Necesita JOIN con otras tablas
           - enriched: Requiere enriquecimiento con contexto
        6. JOIN RECOMENDADOS: ¿Con qué otras tablas debería combinarse?
        7. TRANSFORMACIÓN IA: ¿Cómo convertir en narrativa técnica óptima?
        
        RESPONDE EN JSON con análisis detallado y específico.
        """
        
        response = self.llm.chat_completion([{"role": "user", "content": prompt}])
        return self._parse_evaluation_response(response)
```

## 📊 **Dashboard de Contexto Documentado**

### **Vista de Contexto por Tabla:**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          📚 CONTEXTO DE BD DOCUMENTADO                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tabla: services                                                                 │
│ 🎯 Propósito: Órdenes de servicio técnico con diagnósticos y resoluciones      │
│ 📊 Tipo: Transaccional crítico                                                 │
│ 🤖 IA Score: 9/10 (CRÍTICO para predicción)                                    │
│ 🔗 Relaciones: equipments (marca/modelo), customers (contexto)                 │
│ 💡 Valor KB: Casos reales de falla + resolución = entrenamiento IA             │
│ ⚙️ Estrategia: JOIN con equipments + transformación narrativa rica             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tabla: equipments                                                               │
│ 🎯 Propósito: Catálogo maestro de equipos industriales                         │
│ 📊 Tipo: Datos maestros                                                        │
│ 🤖 IA Score: 8/10 (CRÍTICO para taxonomía y filtros)                          │
│ 🏷️ Entidades: brands, models, categories (auto-aprendizaje taxonomía)          │
│ ⚙️ Estrategia: Enriquecimiento como metadata de servicios                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 **Beneficios del Contexto Completo**

### **🎯 Precisión de Evaluación:**
- **Contexto de negocio** → Evaluaciones más acertadas
- **Relaciones semánticas** → JOINs más inteligentes  
- **Reglas de negocio** → Filtros más efectivos

### **🤖 IA Más Inteligente:**
- **Transformaciones contextuales** → Narrativa técnica rica
- **Metadata semántico** → Búsquedas más precisas
- **Taxonomía automática** → Entidades más relevantes

### **⚡ ETL Optimizado:**
- **Estrategias específicas** por tipo de tabla
- **JOINs pre-planificados** con contexto
- **Priorización inteligente** basada en valor real

## 🚀 **Plan de Implementación**

### **Fase 1: Auto-Documentación (1-2 días)**
1. Implementar `BusinessContextExtractor`
2. Generar análisis automático de tu BD
3. Crear documentación base

### **Fase 2: Enriquecimiento Manual (1 día)**
4. Revisar y completar contexto automático
5. Añadir reglas de negocio específicas
6. Documentar relaciones críticas

### **Fase 3: Análisis Contextual (1 día)**
7. Integrar contexto en evaluación IA
8. Generar configuraciones optimizadas
9. Testing con datos reales

**¿Quieres que implemente el `BusinessContextExtractor` para empezar a documentar automáticamente tu BD?** 📚🤖

