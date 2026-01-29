# 📚 Animal-AI Service - API Reference

## 🎯 **Información General**

- **Base URL**: `http://localhost:8080`
- **Versión API**: `v1`
- **Formato**: JSON
- **Autenticación**: Bearer Token (opcional)
- **Estándar de Respuesta**: Todas las respuestas incluyen `traceId`, `code`, `message`, `data`

---

## 🏥 **Endpoints de Salud**

### **GET /health**
Health check del servicio

**Response:**
```json
{
  "traceId": "health-check",
  "code": "OK",
  "message": "Animal-AI Service funcionando correctamente",
  "data": {
    "status": "ready",
    "uptime_seconds": 3600.5,
    "active_streams": 2,
    "total_animals_detected": 15,
    "total_movements_classified": 342,
    "version": "1.0.0"
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

### **GET /metrics**
Métricas para Prometheus

**Response:** Formato Prometheus
```
# HELP animal_ai_movements_total Total movements detected
# TYPE animal_ai_movements_total counter
animal_ai_movements_total 342

# HELP animal_ai_animals_detected Total animals detected
# TYPE animal_ai_animals_detected gauge
animal_ai_animals_detected 15
```

---

## 🎥 **Endpoints de Video**

### **POST /api/v1/video/analyze**
Iniciar análisis de video desde una fuente

**Request:**
```json
{
  "source": "rtsp://camera.local/stream",
  "trace_id": "video-analysis-001",
  "analysis_config": {
    "resolution": "1920x1080",
    "fps": 30,
    "sensitivity": "medium"
  }
}
```

**Response:**
```json
{
  "traceId": "video-analysis-001",
  "code": "OK",
  "message": "Análisis de video iniciado",
  "data": {
    "stream_id": "stream_20250913_103000",
    "source": "rtsp://camera.local/stream",
    "status": "starting"
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

### **GET /api/v1/video/streams**
Obtener streams de video activos

**Response:**
```json
{
  "traceId": "get-streams",
  "code": "OK",
  "message": "Streams activos obtenidos",
  "data": {
    "active_streams": {
      "stream_20250913_103000": {
        "source": "rtsp://camera.local/stream",
        "start_time": "2025-09-13T10:30:00Z",
        "status": "processing"
      }
    },
    "total_count": 1
  },
  "timestamp": "2025-09-13T10:35:00Z"
}
```

### **DELETE /api/v1/video/streams/{stream_id}**
Detener un stream de video específico

**Response:**
```json
{
  "traceId": "stop-stream_20250913_103000",
  "code": "OK",
  "message": "Stream detenido correctamente",
  "data": {
    "stream_id": "stream_20250913_103000"
  },
  "timestamp": "2025-09-13T10:40:00Z"
}
```

---

## 🏃 **Endpoints de Movimientos**

### **GET /api/v1/movements/recent**
Obtener movimientos recientes detectados

**Query Parameters:**
- `limit` (int, default=50): Límite de resultados
- `animal_id` (string, optional): Filtrar por animal específico

**Response:**
```json
{
  "traceId": "get-recent-movements",
  "code": "OK",
  "message": "Movimientos recientes obtenidos",
  "data": {
    "movements": [
      {
        "id": "mov_001",
        "animal_id": "cow_001",
        "timestamp": "2025-09-13T10:25:00Z",
        "movement_type": "walking",
        "confidence": 0.92,
        "duration_seconds": 15.5,
        "coordinates": [
          {"x": 100.5, "y": 200.3, "timestamp": "2025-09-13T10:25:00Z"},
          {"x": 105.2, "y": 205.1, "timestamp": "2025-09-13T10:25:01Z"}
        ],
        "is_labeled": true,
        "labeled_by": "admin_001",
        "labeled_at": "2025-09-13T10:26:00Z"
      }
    ],
    "count": 1,
    "animal_id": "cow_001"
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

### **GET /api/v1/movements/unlabeled**
Obtener movimientos sin etiquetar para revisión manual

**Query Parameters:**
- `limit` (int, default=20): Límite de resultados

**Response:**
```json
{
  "traceId": "get-unlabeled-movements",
  "code": "OK",
  "message": "Movimientos sin etiquetar obtenidos",
  "data": {
    "unlabeled_movements": [
      {
        "id": "mov_002",
        "animal_id": "cow_002",
        "timestamp": "2025-09-13T10:20:00Z",
        "movement_type": null,
        "confidence": 0.75,
        "duration_seconds": 8.2,
        "coordinates": [...],
        "is_labeled": false,
        "frame_sequence": ["frame_001", "frame_002"]
      }
    ],
    "count": 1
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

### **POST /api/v1/movements/label**
Etiquetar un movimiento manualmente

**Request:**
```json
{
  "movement_id": "mov_002",
  "label": "feeding",
  "admin_id": "admin_001",
  "trace_id": "label-mov_002",
  "confidence": 0.95,
  "notes": "Animal claramente alimentándose en zona de comedero"
}
```

**Response:**
```json
{
  "traceId": "label-mov_002",
  "code": "OK",
  "message": "Movimiento etiquetado correctamente",
  "data": {
    "movement_id": "mov_002",
    "label": "feeding",
    "previous_label": null,
    "confidence": 0.95,
    "admin_id": "admin_001",
    "timestamp": "2025-09-13T10:30:00Z",
    "kb_updated": true,
    "learning_triggered": true
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

---

## 🐾 **Endpoints de Animales**

### **GET /api/v1/animals**
Obtener lista de animales detectados

**Response:**
```json
{
  "traceId": "get-animals",
  "code": "OK",
  "message": "Animales detectados obtenidos",
  "data": {
    "animals": [
      {
        "id": "cow_001",
        "species": "bovine",
        "individual_markers": ["white_spot_forehead", "black_left_ear"],
        "confidence_score": 0.94,
        "first_detected": "2025-09-10T08:00:00Z",
        "last_seen": "2025-09-13T10:25:00Z",
        "total_detections": 1247,
        "status": "active"
      }
    ],
    "total_count": 1
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

### **GET /api/v1/animals/{animal_id}/history**
Obtener historial de comportamiento de un animal específico

**Query Parameters:**
- `days` (int, default=7): Días de historial

**Response:**
```json
{
  "traceId": "history-cow_001",
  "code": "OK",
  "message": "Historial de animal obtenido",
  "data": {
    "animal_id": "cow_001",
    "period_days": 7,
    "total_movements": 156,
    "movement_timeline": [...],
    "behavior_patterns": [
      {
        "pattern_id": "feeding_morning",
        "behavior_name": "morning_feeding",
        "frequency": 7,
        "confidence": 0.89
      }
    ],
    "activity_by_hour": {
      "06": 12,
      "07": 18,
      "08": 15
    },
    "health_trends": {
      "activity_level": "normal",
      "feeding_regularity": "consistent",
      "social_interaction": "active"
    }
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

---

## 👨‍💼 **Endpoints de Administración**

### **GET /api/v1/admin/dashboard**
Dashboard de administración con estadísticas

**Response:**
```json
{
  "traceId": "admin-dashboard",
  "code": "OK",
  "message": "Dashboard de administración obtenido",
  "data": {
    "system_status": {
      "status": "ready",
      "uptime_seconds": 3600.5,
      "memory_usage_mb": 512.3,
      "cpu_usage_percent": 15.2
    },
    "recent_animals": [...],
    "recent_movements": [...],
    "unlabeled_count": 5,
    "active_streams": [...],
    "daily_stats": {
      "movements_detected": 89,
      "animals_identified": 12,
      "behaviors_learned": 3
    },
    "alerts": [
      {
        "type": "info",
        "message": "Nuevo patrón de comportamiento detectado",
        "timestamp": "2025-09-13T10:15:00Z"
      }
    ]
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

### **POST /api/v1/admin/retrain**
Reentrenar modelos con nuevos datos etiquetados

**Response:**
```json
{
  "traceId": "retrain-models",
  "code": "OK",
  "message": "Reentrenamiento iniciado en background",
  "data": {
    "status": "started",
    "job_id": "retrain_20250913_103000",
    "estimated_duration_minutes": 30
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

---

## 🔍 **Endpoints de Búsqueda**

### **POST /api/v1/search/behaviors**
Buscar comportamientos en el Knowledge Base

**Request:**
```json
{
  "query": "comportamiento de alimentación matutino",
  "animal_id": "cow_001",
  "behavior_type": "feeding",
  "date_from": "2025-09-01T00:00:00Z",
  "date_to": "2025-09-13T23:59:59Z",
  "limit": 10,
  "trace_id": "search-behaviors-001"
}
```

**Response:**
```json
{
  "traceId": "search-behaviors-001",
  "code": "OK",
  "message": "Búsqueda de comportamientos completada",
  "data": {
    "results": [
      {
        "doc_id": "behavior_001",
        "score": 0.92,
        "snippet": "Comportamiento de alimentación matutino observado en cow_001...",
        "metadata": {
          "animal_id": "cow_001",
          "movement_type": "feeding",
          "timestamp": "2025-09-12T07:30:00Z"
        }
      }
    ],
    "total_results": 1,
    "query_time_ms": 45
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

---

## 🔧 **Endpoints de Configuración**

### **GET /api/v1/config**
Obtener configuración actual del sistema

**Response:**
```json
{
  "traceId": "get-config",
  "code": "OK",
  "message": "Configuración obtenida",
  "data": {
    "service": {
      "port": 8080,
      "name": "animal-ai-production",
      "debug_mode": false
    },
    "analysis": {
      "enabled": true,
      "movement_sensitivity": "medium",
      "individual_tracking": true
    },
    "video": {
      "resolution": "1920x1080",
      "fps": 30
    }
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

### **PUT /api/v1/config**
Actualizar configuración del sistema

**Request:**
```json
{
  "config_section": "analysis",
  "config_data": {
    "movement_sensitivity": "high",
    "tracking_confidence": 0.9
  },
  "apply_immediately": true,
  "trace_id": "update-config-001"
}
```

**Response:**
```json
{
  "traceId": "update-config-001",
  "code": "OK",
  "message": "Configuración actualizada correctamente",
  "data": {
    "section": "analysis",
    "applied_at": "2025-09-13T10:30:00Z",
    "validation_status": "success",
    "restart_required": false
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

---

## 🔌 **WebSocket Endpoints**

### **WS /ws/live-analysis**
WebSocket para análisis en tiempo real

**Conexión:**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/live-analysis');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Live data:', data);
};
```

**Mensajes recibidos:**
```json
{
  "timestamp": "2025-09-13T10:30:00Z",
  "active_streams": 2,
  "total_animals": 15,
  "total_movements": 342,
  "recent_movements": [
    {
      "animal_id": "cow_001",
      "movement_type": "walking",
      "confidence": 0.92,
      "timestamp": "2025-09-13T10:29:55Z"
    }
  ]
}
```

---

## ❌ **Códigos de Error**

### **Códigos de Estado HTTP**
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable

### **Códigos de Respuesta Personalizados**
- `OK` - Operación exitosa
- `ERROR` - Error general
- `WARNING` - Advertencia
- `VALIDATION_ERROR` - Error de validación
- `NOT_FOUND` - Recurso no encontrado
- `UNAUTHORIZED` - No autorizado
- `SERVICE_UNAVAILABLE` - Servicio no disponible

### **Formato de Error**
```json
{
  "traceId": "error-trace-001",
  "code": "VALIDATION_ERROR",
  "message": "Error de validación en los datos de entrada",
  "data": {
    "errors": [
      {
        "field": "movement_id",
        "message": "Movement ID no puede estar vacío"
      }
    ]
  },
  "timestamp": "2025-09-13T10:30:00Z"
}
```

---

## 🔐 **Autenticación**

### **Bearer Token (Opcional)**
```http
Authorization: Bearer your-api-key-here
```

### **Headers Requeridos**
```http
Content-Type: application/json
X-Trace-Id: optional-trace-id
```

---

## 📊 **Rate Limiting**

- **Límite general**: 1000 requests/hora por IP
- **Análisis de video**: 10 streams simultáneos máximo
- **Búsquedas**: 100 requests/minuto
- **Etiquetado**: 500 requests/hora

---

## 🧪 **Ejemplos de Uso**

### **Curl Examples**

**Iniciar análisis de video:**
```bash
curl -X POST "http://localhost:8080/api/v1/video/analyze" \
  -H "Content-Type: application/json" \
  -H "X-Trace-Id: test-001" \
  -d '{
    "source": "rtsp://camera.local/stream",
    "analysis_config": {"sensitivity": "high"}
  }'
```

**Etiquetar movimiento:**
```bash
curl -X POST "http://localhost:8080/api/v1/movements/label" \
  -H "Content-Type: application/json" \
  -d '{
    "movement_id": "mov_001",
    "label": "feeding",
    "admin_id": "admin_001",
    "confidence": 0.95
  }'
```

**Obtener historial de animal:**
```bash
curl "http://localhost:8080/api/v1/animals/cow_001/history?days=7"
```

---

**Esta documentación cubre todos los endpoints disponibles en el Animal-AI Service, siguiendo los estándares establecidos en el ecosistema FixeatAI.** 🐾📚


