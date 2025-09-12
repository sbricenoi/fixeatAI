# 🔄 Estrategia de Extracción Inteligente BD → KB

## 🎯 **Recomendación: ETL Híbrido + IA Adaptativo**

### **📋 Análisis del Estado Actual**

**✅ Lo que YA tenemos:**
- Conexión MySQL funcional (`MySQLClient`)
- DB Agent con NL2SQL automático
- Orquestador multi-agente
- KB con auto-taxonomía y curation
- Sistema de metadatos y filtros

**🔧 Lo que necesitamos construir:**
- ETL Pipeline inteligente
- Transformador IA para adaptación de datos
- Scheduler para extracciones periódicas
- Monitor de cambios incrementales

## 🏗️ **Arquitectura Propuesta**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MySQL DB      │ ──▶│  ETL Pipeline    │ ──▶│   Knowledge     │
│                 │    │  + AI Adapter    │    │      Base       │
│ - services      │    │                  │    │                 │
│ - activity_logs │    │ 🤖 LLM Transform │    │ 🔍 Searchable   │
│ - equipments    │    │ 📊 Auto-Metadata │    │ 📊 Categorized │
│ - customers     │    │ 🏷️  Auto-Taxonomy │    │ 🎯 Filtered    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Change        │    │   Intelligent    │    │   Performance   │
│   Detection     │    │   Chunking       │    │   Monitoring    │
│                 │    │                  │    │                 │
│ • Timestamps    │    │ • Semantic Split │    │ • KB Growth     │
│ • Incremental   │    │ • Context Aware  │    │ • Query Speed   │
│ • Delta Sync    │    │ • Auto-Metadata  │    │ • Data Quality  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 **Propuesta de Implementación**

### **Opción 1: ETL Inteligente Programado (RECOMENDADO)**

**✅ Ventajas:**
- **Eficiente**: Solo procesa datos nuevos/modificados
- **Escalable**: Maneja grandes volúmenes sin sobrecargar
- **Inteligente**: IA adapta y optimiza la información
- **Controlado**: Proceso programado y monitoreable
- **Resiliente**: Manejo de errores y reintentos

**⚙️ Funcionamiento:**
1. **Extracción Incremental**: Solo nuevos registros desde última sync
2. **Transformación IA**: LLM adapta datos al formato KB óptimo
3. **Carga Inteligente**: Auto-taxonomía y metadata enriquecida
4. **Monitoreo**: Métricas y alertas de calidad

### **Opción 2: Queries Bajo Demanda**

**❌ Desventajas:**
- Latencia alta en consultas complejas
- Sobrecarga de BD en picos de uso
- Sin optimización de formato para KB
- Dependencia directa de BD disponibilidad

## 🔧 **Implementación del ETL Inteligente**

### **1. Extractor Incremental (`services/etl/extractor.py`)**

```python
class IntelligentExtractor:
    def __init__(self):
        self.mysql = MySQLClient()
        self.llm = LLMClient(agent="etl_transformer")
        
    def extract_incremental(self, table: str, since: datetime) -> List[Dict]:
        """Extrae solo registros nuevos/modificados"""
        sql = f"""
        SELECT * FROM {table} 
        WHERE updated_at > %s OR created_at > %s
        ORDER BY updated_at DESC
        LIMIT 1000
        """
        return self.mysql.query(sql, [since, since])
        
    def transform_with_ai(self, raw_data: List[Dict], table: str) -> List[Dict]:
        """IA adapta datos crudos al formato KB óptimo"""
        prompt = f"""
        Transforma estos registros de la tabla {table} en documentos 
        técnicos estructurados para Knowledge Base:

        DATOS CRUDOS:
        {json.dumps(raw_data[:3], indent=2)}

        OBJETIVO:
        - Crear texto narrativo técnico
        - Extraer metadatos relevantes (brand, model, category)
        - Generar título descriptivo
        - Identificar keywords técnicos
        - Mantener trazabilidad con ID original

        FORMATO RESPUESTA:
        ```json
        [
          {{
            "kb_id": "service_12345",
            "title": "Mantenimiento RATIONAL CombiMaster - Cambio Burlete",
            "text": "Se realizó mantenimiento preventivo en horno RATIONAL modelo CombiMaster...",
            "metadata": {{
              "source_table": "services",
              "source_id": "12345",
              "brand": "RATIONAL",
              "model": "CombiMaster",
              "category": "horno",
              "service_type": "mantenimiento",
              "date": "2025-01-10",
              "technician": "José Riquelme"
            }}
          }}
        ]
        ```
        """
        
        response = self.llm.chat_completion([{"role": "user", "content": prompt}])
        # Parse JSON response
        return self._parse_ai_response(response)
```

### **2. Pipeline Principal (`services/etl/pipeline.py`)**

```python
class ETLPipeline:
    def __init__(self):
        self.extractor = IntelligentExtractor()
        self.kb_client = requests.Session()
        self.last_sync = self._load_last_sync()
        
    def run_incremental_sync(self) -> Dict:
        """Ejecuta sincronización incremental completa"""
        results = {}
        
        tables = ["services", "activity_services", "service_logs", "equipments"]
        
        for table in tables:
            try:
                # 1. Extraer datos nuevos
                raw_data = self.extractor.extract_incremental(table, self.last_sync)
                
                if not raw_data:
                    results[table] = {"status": "no_new_data"}
                    continue
                    
                # 2. Transformar con IA
                kb_docs = self.extractor.transform_with_ai(raw_data, table)
                
                # 3. Cargar al KB con auto-taxonomía
                ingest_result = self._ingest_to_kb(kb_docs)
                
                results[table] = {
                    "status": "success",
                    "extracted": len(raw_data),
                    "transformed": len(kb_docs),
                    "ingested": ingest_result.get("ingested", 0),
                    "new_entities": ingest_result.get("auto_learning", {})
                }
                
            except Exception as e:
                results[table] = {"status": "error", "error": str(e)}
                
        self._save_last_sync()
        return results
        
    def _ingest_to_kb(self, docs: List[Dict]) -> Dict:
        """Envía documentos al KB con auto-curation"""
        payload = {
            "docs": docs,
            "auto_curate": True,
            "auto_learn_taxonomy": True
        }
        
        response = self.kb_client.post(
            "http://localhost:7070/tools/kb_ingest",
            json=payload
        )
        return response.json()
```

### **3. Scheduler Inteligente (`services/etl/scheduler.py`)**

```python
import schedule
import time
from datetime import datetime, timedelta

class ETLScheduler:
    def __init__(self):
        self.pipeline = ETLPipeline()
        
    def setup_schedules(self):
        """Configura horarios de extracción"""
        
        # Extracción incremental cada 2 horas (horario laboral)
        schedule.every(2).hours.do(self._run_incremental_sync).tag("incremental")
        
        # Extracción completa diaria (madrugada)
        schedule.every().day.at("02:00").do(self._run_full_sync).tag("full")
        
        # Limpieza de taxonomía semanal
        schedule.every().sunday.at("03:00").do(self._cleanup_taxonomy).tag("maintenance")
        
    def _run_incremental_sync(self):
        """Sincronización incremental"""
        print(f"🔄 Iniciando sync incremental: {datetime.now()}")
        
        try:
            results = self.pipeline.run_incremental_sync()
            
            # Log resultados
            total_ingested = sum(r.get("ingested", 0) for r in results.values() if isinstance(r, dict))
            print(f"✅ Sync completado: {total_ingested} documentos ingresados")
            
            # Alertas si hay errores
            errors = [k for k, v in results.items() if v.get("status") == "error"]
            if errors:
                print(f"⚠️  Errores en tablas: {errors}")
                
        except Exception as e:
            print(f"❌ Error en sync incremental: {e}")
```

### **4. Monitor de Calidad (`services/etl/monitor.py`)**

```python
class ETLMonitor:
    def generate_report(self) -> Dict:
        """Genera reporte de calidad del ETL"""
        
        # Estadísticas KB
        kb_stats = requests.get("http://localhost:7070/tools/taxonomy/stats").json()
        
        # Métricas de calidad
        quality_metrics = {
            "kb_documents": self._count_kb_documents(),
            "taxonomy_entities": kb_stats.get("total_entities", 0),
            "last_sync": self._get_last_sync(),
            "data_freshness": self._calculate_freshness(),
            "ingestion_rate": self._calculate_ingestion_rate(),
            "error_rate": self._calculate_error_rate()
        }
        
        return quality_metrics
        
    def health_check(self) -> bool:
        """Verifica salud del pipeline ETL"""
        try:
            # Test conectividad MySQL
            mysql = MySQLClient()
            mysql.query("SELECT 1")
            
            # Test KB disponibilidad
            requests.get("http://localhost:7070/health", timeout=5)
            
            # Test taxonomía funcionando
            requests.get("http://localhost:7070/tools/taxonomy/stats", timeout=5)
            
            return True
        except Exception:
            return False
```

## 📊 **Configuración Propuesta**

### **Variables de Entorno Adicionales:**

```bash
# ETL Configuration
ETL_ENABLED=true
ETL_INCREMENTAL_HOURS=2
ETL_FULL_SYNC_TIME=02:00
ETL_BATCH_SIZE=500
ETL_RETRY_ATTEMPTS=3

# AI Transformation
ETL_LLM_MODEL=gpt-4o-mini
ETL_LLM_TEMPERATURE=0.1
ETL_MAX_DOCS_PER_BATCH=50

# Quality Monitoring
ETL_QUALITY_THRESHOLD=0.85
ETL_ALERT_EMAIL=admin@company.com
```

### **Endpoints de Control:**

```bash
# Control manual del ETL
POST /api/v1/etl/sync-now        # Forzar sync inmediato
GET  /api/v1/etl/status          # Estado actual
GET  /api/v1/etl/metrics         # Métricas de calidad
POST /api/v1/etl/pause           # Pausar scheduler
POST /api/v1/etl/resume          # Reanudar scheduler
```

## 🎯 **Beneficios de Esta Estrategia**

### **🚀 Rendimiento:**
- **Incremental**: Solo procesa datos nuevos
- **Batch Processing**: Optimiza recursos
- **Async**: No bloquea operaciones principales

### **🤖 Inteligencia:**
- **IA Adaptation**: Convierte datos crudos en contenido técnico rico
- **Auto-Taxonomy**: Aprende automáticamente nuevas entidades
- **Context Aware**: Mantiene coherencia semántica

### **🔍 Calidad:**
- **Data Validation**: Verifica integridad antes de ingesta
- **Quality Scoring**: Evalúa calidad del contenido transformado
- **Error Handling**: Reintentos y alertas automáticas

### **⚡ Escalabilidad:**
- **Configurable**: Ajusta frecuencia según necesidades
- **Distributed**: Puede ejecutarse en múltiples instancias
- **Monitoring**: Métricas y alertas proactivas

## 🏁 **Plan de Implementación**

### **Fase 1: Extractor Base (1-2 días)**
1. Crear `IntelligentExtractor` con queries incrementales
2. Implementar transformación IA básica
3. Integrar con KB existente

### **Fase 2: Pipeline Completo (2-3 días)**
4. Desarrollar `ETLPipeline` con manejo de errores
5. Crear sistema de scheduling
6. Implementar métricas básicas

### **Fase 3: Optimización (1-2 días)**
7. Añadir monitor de calidad
8. Crear endpoints de control
9. Documentar y testing

**¿Te parece bien esta estrategia? ¿Quieres que comience implementando el Extractor Inteligente?** 🚀
