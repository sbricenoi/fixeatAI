# 🧪 Endpoints para Pruebas Locales - FixeatAI

## 🚀 **Servidores Activos**

### **✅ MCP Server (Puerto 7070) - ACTIVO**
- **KB y Taxonomía**: http://localhost:7070
- **Estado**: ✅ Funcionando

### **❌ API Principal (Puerto 8000) - NECESARIO INICIAR**
- **Predicciones**: http://localhost:8000  
- **Estado**: ❌ No iniciado

## 🔧 **Comandos para Iniciar Servidores**

```bash
# Terminal 1: MCP Server (Ya corriendo)
make mcp

# Terminal 2: API Principal (NECESARIO)
make run
```

## 📥 **ENDPOINTS DE INGESTA KB**

### **1. 🔍 Test del Sistema de Taxonomía**
```bash
curl -X GET "http://localhost:7070/tools/taxonomy/test" | jq .
```

### **2. 📊 Estadísticas de Taxonomía**
```bash
curl -X GET "http://localhost:7070/tools/taxonomy/stats" | jq .
```

### **3. 📚 Ingesta Simple de Documentos**
```bash
curl -X POST "http://localhost:7070/tools/kb_ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      {
        "id": "test_doc_1",
        "text": "LAMINADORA SOBREMESÓN SINMAG, MOD. SM-520, RODILLO 50[cm], MONOFASICA. Problema: Manilla trabada, cadena desmontada y piñón con desgaste. Resolución: Llevar a taller para desarme completo. Técnico: Jonathan Huichalaf. Estado: Detenido.",
        "metadata": {"source": "test", "brand": "SINMAG", "model": "SM-520", "category": "laminadora"}
      }
    ]
  }' | jq .
```

### **4. 🤖 Ingesta con Auto-Taxonomía**
```bash
curl -X POST "http://localhost:7070/tools/kb_ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_curate": true,
    "auto_learn_taxonomy": true,
    "docs": [
      {
        "id": "servicio_horno_zucchelli",
        "text": "Cliente: LA BIRRA TABANCURA. Equipo: HORNO ROTATORIO 1 CARR. 60X40 18 NIV. GAS-PETROLEO TRIFASICO ZUCCHELLI, MOD. MINIFANTON 60X40G. Problema: Cliente reporta problemas con correa del horno rotatorio. Se realiza inspección visual identificando correa A25 desgastada y tensión incorrecta. Resolución: Se realiza cambio de correa A25 a horno. Se realiza cambio de correa y tensión de correa. Se realizan pruebas de funcionamiento quedando el equipo operativo. Estado: Operativo. Técnico: José Riquelme. Fecha: 02/09/2025",
        "metadata": {"source": "llamada_servicio"}
      },
      {
        "id": "servicio_future_trima", 
        "text": "Cliente: PANIFICADORA PENAFLOR LIMITADA. Equipo: DIVISORA OVILLADORA 4 SALIDAS 30-150[gr] 6000 PIEZAS-HORA FUTURE TRIMA, MOD. PRIMA EVO KE 4. Problema: Se asiste a local para revisión de maquina ovilladora la cual se realiza ajustes mecánicos. El cual el equipo me entrega los 4 ovillos iguales. Equipo presenta problema en ovillos disparejo cuando la masa queda pegada en la cámara y tapa el sensor que provoca que no entre masa a la cámara. Equipo mecánicamente no presenta problema. Resolución: Ajustes mecánicos realizados. Estado: Requiere tecnólogo. Técnico: José Riquelme.",
        "metadata": {"source": "llamada_servicio"}
      }
    ]
  }' | jq .
```

### **5. 📄 Ingesta desde Archivo (Simulando docs/data.txt)**
```bash
curl -X POST "http://localhost:7070/tools/kb_ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_curate": true,
    "auto_learn_taxonomy": true,
    "docs": [
      {
        "id": "mantenimiento_unox_1",
        "text": "MANTENCION HORNO UNOX - Se realiza mantenimiento preventivo, se limpian ventiladores, limpieza de vidrios, limpieza de componentes eléctricos, reaprete de conexiones eléctricas, operativo. Se cambia burlete de puerta, el cliente facilita el repuesto, manilla de puerta con problemas de desgaste se debe reemplazar manilla y anclaje de gancho de manilla, operativo. Técnico: Jonathan Huichalaf. Fecha: 27/08/2025",
        "metadata": {"source": "mantenimiento_preventivo"}
      },
      {
        "id": "reparacion_rational_1",
        "text": "REPARACION HORNO RATIONAL TOTTUS LA CISTERNA - Se realiza reparación según ppto 563096. Cambio burlete, junta carro, sonda nucleo, manguera vapor con abrazadera, manguera presion, kit desague, tubo ventilacion, valvula ventilacion, inyector enfriamiento con sello, cubierta filtros, Estructura montaje ventilador. Se realiza prueba completa de lavado quedando equipo operativo. Nota: deben mejorar procedimientos de limpieza y cuidados de horno. Ablandador de agua en mal estado y sin sal. Técnico: Arturo Gonzalez P.",
        "metadata": {"source": "reparacion"}
      }
    ]
  }' | jq .
```

### **6. 🚀 Bootstrap Automático de Taxonomía**
```bash
curl -X POST "http://localhost:7070/tools/taxonomy/bootstrap" | jq .
```

### **7. 🔍 Búsqueda en KB**
```bash
curl -X POST "http://localhost:7070/tools/kb_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "problemas con laminadora SINMAG",
    "top_k": 5
  }' | jq .
```

### **8. 🔍 Búsqueda Filtrada por Metadatos**
```bash
curl -X POST "http://localhost:7070/tools/kb_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mantenimiento preventivo",
    "top_k": 3,
    "where": {"brand": "UNOX"}
  }' | jq .
```

## 🎯 **ENDPOINTS DE PREDICCIONES** (Requiere API Principal)

### **Iniciar API Principal Primero:**
```bash
# En otra terminal
make run
```

### **1. 🔮 Predicción de Fallas**
```bash
curl -X POST "http://localhost:8000/predict-fallas" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "test_client", 
    "equipo": {
      "marca": "SINMAG",
      "modelo": "SM-520", 
      "tipo": "laminadora"
    },
    "problema_actual": "La laminadora hace ruido y la manilla se traba frecuentemente",
    "historial": "Último mantenimiento hace 6 meses"
  }' | jq .
```

### **2. ❓ Q&A Técnico**
```bash
curl -X POST "http://localhost:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cómo reparar una laminadora SINMAG con problemas de cadena?",
    "contexto": {
      "marca": "SINMAG",
      "modelo": "SM-520"
    }
  }' | jq .
```

### **3. 🛠️ Soporte Técnico**
```bash
curl -X POST "http://localhost:8000/api/v1/soporte-tecnico" \
  -H "Content-Type: application/json" \
  -d '{
    "problema": "Horno RATIONAL no enciende después de limpieza",
    "equipo": {
      "marca": "RATIONAL",
      "modelo": "CombiMaster",
      "ubicacion": "Cocina principal"
    }
  }' | jq .
```

### **4. ✅ Validación de Formulario**
```bash
curl -X POST "http://localhost:8000/api/v1/validar-formulario" \
  -H "Content-Type: application/json" \
  -d '{
    "datos": {
      "cliente": "Panadería Central",
      "equipo": "LAMINADORA SINMAG SM-520",
      "problema": "No funciona",
      "fecha": "2025-01-10"
    }
  }' | jq .
```

### **5. 📊 Análisis Operacional**
```bash
curl -X POST "http://localhost:8000/api/v1/ops-analitica" \
  -H "Content-Type: application/json" \
  -d '{
    "periodo": "ultimo_mes",
    "filtros": {
      "marca": "RATIONAL"
    }
  }' | jq .
```

### **6. 🎭 Orquestador Multi-Agente**
```bash
curl -X POST "http://localhost:8000/api/v1/orquestar" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuántos servicios de SINMAG tuvimos el mes pasado y cuáles fueron los problemas más comunes?"
  }' | jq .
```

## 🧪 **Secuencia de Pruebas Recomendada**

### **Paso 1: Preparar KB**
```bash
# 1. Verificar estado inicial
curl -s http://localhost:7070/tools/taxonomy/stats | jq .

# 2. Ingestar documentos base
curl -X POST "http://localhost:7070/tools/kb_ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_curate": true,
    "auto_learn_taxonomy": true,
    "docs": [...]
  }' | jq .

# 3. Verificar aprendizaje automático
curl -s http://localhost:7070/tools/taxonomy/stats | jq .
```

### **Paso 2: Probar Búsquedas**
```bash
# Búsqueda general
curl -X POST "http://localhost:7070/tools/kb_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "laminadora problemas", "top_k": 3}' | jq .

# Búsqueda filtrada
curl -X POST "http://localhost:7070/tools/kb_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "mantenimiento", "where": {"brand": "SINMAG"}}' | jq .
```

### **Paso 3: Iniciar API y Probar Predicciones**
```bash
# Terminal 2: Iniciar API
make run

# Probar predicción
curl -X POST "http://localhost:8000/predict-fallas" \
  -H "Content-Type: application/json" \
  -d '{
    "problema_actual": "laminadora SINMAG no funciona, hace ruido"
  }' | jq .
```

## 🔧 **Debugging y Monitoreo**

### **Ver Logs en Tiempo Real**
```bash
# MCP Server logs
tail -f logs/mcp.log

# API logs  
tail -f logs/api.log
```

### **Verificar Estado de Servicios**
```bash
# Estado MCP
curl -s http://localhost:7070/health

# Estado API
curl -s http://localhost:8000/health

# Estado ChromaDB
curl -X POST "http://localhost:7070/tools/kb_search" \
  -d '{"query": "test", "top_k": 1}' | jq '.hits | length'
```

## 📊 **Ejemplos de Respuestas Esperadas**

### **Ingesta Exitosa:**
```json
{
  "ingested": 2,
  "curated": true,
  "auto_learning": {
    "new_brands_detected": 1,
    "new_models_detected": 1,
    "examples": {
      "brands": ["FUTURE TRIMA"],
      "models": ["PRIMA EVO KE 4"]
    }
  }
}
```

### **Predicción Exitosa:**
```json
{
  "fallas_probables": [
    {
      "descripcion": "Cadena de transmisión desmontada",
      "confianza": 0.89,
      "sintomas": ["ruido mecánico", "manilla trabada"]
    }
  ],
  "repuestos_sugeridos": ["cadena transmisión", "piñón"],
  "pasos_diagnostico": ["desarmar mecanismo", "inspeccionar cadena"],
  "fuentes": ["servicio_laminadora_1"]
}
```

**¡Ya tienes todo listo para hacer pruebas completas del sistema!** 🚀
