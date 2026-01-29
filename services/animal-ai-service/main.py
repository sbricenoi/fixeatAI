#!/usr/bin/env python3
"""
Animal-AI Service - Microservicio independiente para análisis de comportamiento animal
Puerto: 8080 (configurable)
Completamente autónomo, sin dependencias de otros servicios FixeatAI
"""

from __future__ import annotations

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv("ANIMAL_LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.getenv("ANIMAL_LOG_FILE", "logs/animal-ai.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("animal-ai-service")

# Importar módulos internos del Animal-AI Service
from core.config import AnimalAIConfig
from core.video_processor import VideoProcessor
from core.movement_analyzer import MovementAnalyzer
from core.individual_tracker import IndividualTracker
from core.behavior_classifier import BehaviorClassifier
from core.learning_engine import LearningEngine
from core.kb_integration import KBIntegration
from core.monitor import AnimalAIMonitor
from models.requests import *
from models.responses import *

# Inicializar configuración
config = AnimalAIConfig()

# Crear aplicación FastAPI
app = FastAPI(
    title="Animal-AI Service",
    description="Microservicio independiente para análisis de comportamiento animal",
    version="1.0.0",
    docs_url="/docs" if config.debug_mode else None,
    redoc_url="/redoc" if config.debug_mode else None
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
video_processor = VideoProcessor(config)
movement_analyzer = MovementAnalyzer(config)
individual_tracker = IndividualTracker(config)
behavior_classifier = BehaviorClassifier(config)
learning_engine = LearningEngine(config)
kb_integration = KBIntegration(config)
monitor = AnimalAIMonitor(config)

# Estado global del servicio
service_state = {
    "status": "initializing",
    "active_streams": {},
    "total_animals_detected": 0,
    "total_movements_classified": 0,
    "total_behaviors_learned": 0,
    "start_time": datetime.now()
}

@app.on_event("startup")
async def startup_event():
    """Inicializar servicio al arrancar"""
    logger.info("🐾 Iniciando Animal-AI Service...")
    
    try:
        # Inicializar componentes
        await video_processor.initialize()
        await movement_analyzer.initialize()
        await individual_tracker.initialize()
        await behavior_classifier.initialize()
        await learning_engine.initialize()
        await kb_integration.initialize()
        await monitor.initialize()
        
        service_state["status"] = "ready"
        logger.info("✅ Animal-AI Service iniciado correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error iniciando Animal-AI Service: {e}")
        service_state["status"] = "error"
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    logger.info("🔄 Cerrando Animal-AI Service...")
    
    # Detener streams activos
    for stream_id in list(service_state["active_streams"].keys()):
        await stop_video_analysis(stream_id)
    
    # Limpiar componentes
    await video_processor.cleanup()
    await movement_analyzer.cleanup()
    await individual_tracker.cleanup()
    await behavior_classifier.cleanup()
    await learning_engine.cleanup()
    await kb_integration.cleanup()
    await monitor.cleanup()
    
    logger.info("✅ Animal-AI Service cerrado correctamente")

# ==================== ENDPOINTS DE SALUD ====================

@app.get("/health")
async def health_check():
    """Health check independiente del servicio"""
    return AnimalAIResponse(
        traceId="health-check",
        code="OK",
        message="Animal-AI Service funcionando correctamente",
        data={
            "status": service_state["status"],
            "uptime_seconds": (datetime.now() - service_state["start_time"]).total_seconds(),
            "active_streams": len(service_state["active_streams"]),
            "total_animals_detected": service_state["total_animals_detected"],
            "total_movements_classified": service_state["total_movements_classified"],
            "version": "1.0.0"
        }
    )

@app.get("/metrics")
async def get_metrics():
    """Métricas del servicio para Prometheus"""
    if not config.metrics_enabled:
        raise HTTPException(status_code=404, detail="Métricas deshabilitadas")
    
    return await monitor.get_prometheus_metrics()

# ==================== ENDPOINTS DE VIDEO ====================

@app.post("/api/v1/video/analyze", response_model=AnimalAIResponse)
async def start_video_analysis(
    request: VideoAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Iniciar análisis de video desde una fuente"""
    try:
        logger.info(f"🎥 Iniciando análisis de video: {request.source}")
        
        # Generar ID único para el stream
        stream_id = f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Iniciar procesamiento en background
        background_tasks.add_task(
            process_video_stream,
            stream_id,
            request.source,
            request.analysis_config
        )
        
        # Registrar stream activo
        service_state["active_streams"][stream_id] = {
            "source": request.source,
            "start_time": datetime.now(),
            "status": "starting"
        }
        
        return AnimalAIResponse(
            traceId=request.trace_id or f"video-{stream_id}",
            code="OK",
            message="Análisis de video iniciado",
            data={
                "stream_id": stream_id,
                "source": request.source,
                "status": "starting"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error iniciando análisis de video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/video/streams", response_model=AnimalAIResponse)
async def get_active_streams():
    """Obtener streams de video activos"""
    return AnimalAIResponse(
        traceId="get-streams",
        code="OK",
        message="Streams activos obtenidos",
        data={
            "active_streams": service_state["active_streams"],
            "total_count": len(service_state["active_streams"])
        }
    )

@app.delete("/api/v1/video/streams/{stream_id}", response_model=AnimalAIResponse)
async def stop_video_stream(stream_id: str):
    """Detener un stream de video específico"""
    try:
        if stream_id not in service_state["active_streams"]:
            raise HTTPException(status_code=404, detail="Stream no encontrado")
        
        await stop_video_analysis(stream_id)
        
        return AnimalAIResponse(
            traceId=f"stop-{stream_id}",
            code="OK",
            message="Stream detenido correctamente",
            data={"stream_id": stream_id}
        )
        
    except Exception as e:
        logger.error(f"❌ Error deteniendo stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINTS DE MOVIMIENTOS ====================

@app.get("/api/v1/movements/recent", response_model=AnimalAIResponse)
async def get_recent_movements(
    limit: int = 50,
    animal_id: Optional[str] = None
):
    """Obtener movimientos recientes detectados"""
    try:
        movements = await movement_analyzer.get_recent_movements(
            limit=limit,
            animal_id=animal_id
        )
        
        return AnimalAIResponse(
            traceId="get-recent-movements",
            code="OK",
            message="Movimientos recientes obtenidos",
            data={
                "movements": movements,
                "count": len(movements),
                "animal_id": animal_id
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo movimientos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/movements/unlabeled", response_model=AnimalAIResponse)
async def get_unlabeled_movements(limit: int = 20):
    """Obtener movimientos sin etiquetar para revisión manual"""
    try:
        movements = await behavior_classifier.get_unlabeled_movements(limit)
        
        return AnimalAIResponse(
            traceId="get-unlabeled-movements",
            code="OK",
            message="Movimientos sin etiquetar obtenidos",
            data={
                "unlabeled_movements": movements,
                "count": len(movements)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo movimientos sin etiquetar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/movements/label", response_model=AnimalAIResponse)
async def label_movement(request: LabelMovementRequest):
    """Etiquetar un movimiento manualmente"""
    try:
        logger.info(f"🏷️ Etiquetando movimiento {request.movement_id}: {request.label}")
        
        # Etiquetar movimiento
        result = await behavior_classifier.label_movement(
            request.movement_id,
            request.label,
            request.admin_id
        )
        
        # Actualizar KB con nuevo conocimiento
        await kb_integration.update_with_labeled_movement(result)
        
        # Actualizar motor de aprendizaje
        await learning_engine.process_new_label(result)
        
        service_state["total_behaviors_learned"] += 1
        
        return AnimalAIResponse(
            traceId=request.trace_id or f"label-{request.movement_id}",
            code="OK",
            message="Movimiento etiquetado correctamente",
            data=result
        )
        
    except Exception as e:
        logger.error(f"❌ Error etiquetando movimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINTS DE ANIMALES ====================

@app.get("/api/v1/animals", response_model=AnimalAIResponse)
async def get_detected_animals():
    """Obtener lista de animales detectados"""
    try:
        animals = await individual_tracker.get_all_animals()
        
        return AnimalAIResponse(
            traceId="get-animals",
            code="OK",
            message="Animales detectados obtenidos",
            data={
                "animals": animals,
                "total_count": len(animals)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo animales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/animals/{animal_id}/history", response_model=AnimalAIResponse)
async def get_animal_history(animal_id: str, days: int = 7):
    """Obtener historial de comportamiento de un animal específico"""
    try:
        history = await individual_tracker.get_animal_history(animal_id, days)
        
        return AnimalAIResponse(
            traceId=f"history-{animal_id}",
            code="OK",
            message="Historial de animal obtenido",
            data={
                "animal_id": animal_id,
                "history": history,
                "days": days
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial de {animal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINTS DE ADMINISTRACIÓN ====================

@app.get("/api/v1/admin/dashboard", response_model=AnimalAIResponse)
async def get_admin_dashboard():
    """Dashboard de administración con estadísticas"""
    try:
        dashboard_data = await monitor.get_dashboard_data()
        
        return AnimalAIResponse(
            traceId="admin-dashboard",
            code="OK",
            message="Dashboard de administración obtenido",
            data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/retrain", response_model=AnimalAIResponse)
async def retrain_models(background_tasks: BackgroundTasks):
    """Reentrenar modelos con nuevos datos etiquetados"""
    try:
        logger.info("🔄 Iniciando reentrenamiento de modelos...")
        
        background_tasks.add_task(learning_engine.retrain_models)
        
        return AnimalAIResponse(
            traceId="retrain-models",
            code="OK",
            message="Reentrenamiento iniciado en background",
            data={"status": "started"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error iniciando reentrenamiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WEBSOCKET PARA TIEMPO REAL ====================

@app.websocket("/ws/live-analysis")
async def websocket_live_analysis(websocket: WebSocket):
    """WebSocket para análisis en tiempo real"""
    await websocket.accept()
    
    try:
        logger.info("🔌 Cliente WebSocket conectado para análisis en vivo")
        
        # Enviar actualizaciones en tiempo real
        while True:
            # Obtener datos recientes
            recent_data = await get_live_analysis_data()
            
            # Enviar al cliente
            await websocket.send_json(recent_data)
            
            # Esperar antes de la siguiente actualización
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"❌ Error en WebSocket: {e}")
    finally:
        logger.info("🔌 Cliente WebSocket desconectado")

# ==================== FUNCIONES AUXILIARES ====================

async def process_video_stream(
    stream_id: str,
    source: str,
    analysis_config: Optional[Dict[str, Any]] = None
):
    """Procesar stream de video en background"""
    try:
        logger.info(f"🎬 Procesando stream {stream_id} desde {source}")
        
        # Actualizar estado
        service_state["active_streams"][stream_id]["status"] = "processing"
        
        # Iniciar procesamiento
        async for frame_data in video_processor.process_stream(source, analysis_config):
            # Analizar movimiento
            movements = await movement_analyzer.analyze_frame(frame_data)
            
            # Rastrear individuos
            tracked_animals = await individual_tracker.track_animals(movements)
            
            # Clasificar comportamientos
            behaviors = await behavior_classifier.classify_behaviors(tracked_animals)
            
            # Actualizar contadores
            service_state["total_animals_detected"] += len(tracked_animals)
            service_state["total_movements_classified"] += len(behaviors)
            
            # Enviar a KB si hay comportamientos conocidos
            for behavior in behaviors:
                if behavior.get("is_known", False):
                    await kb_integration.ingest_behavior(behavior)
        
    except Exception as e:
        logger.error(f"❌ Error procesando stream {stream_id}: {e}")
        service_state["active_streams"][stream_id]["status"] = "error"
    
    finally:
        # Limpiar stream
        if stream_id in service_state["active_streams"]:
            del service_state["active_streams"][stream_id]

async def stop_video_analysis(stream_id: str):
    """Detener análisis de video"""
    if stream_id in service_state["active_streams"]:
        service_state["active_streams"][stream_id]["status"] = "stopping"
        await video_processor.stop_stream(stream_id)
        del service_state["active_streams"][stream_id]
        logger.info(f"🛑 Stream {stream_id} detenido")

async def get_live_analysis_data():
    """Obtener datos para análisis en vivo"""
    return {
        "timestamp": datetime.now().isoformat(),
        "active_streams": len(service_state["active_streams"]),
        "total_animals": service_state["total_animals_detected"],
        "total_movements": service_state["total_movements_classified"],
        "recent_movements": await movement_analyzer.get_recent_movements(limit=5)
    }

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    # Configuración del servidor
    port = config.service_port
    host = "0.0.0.0"
    
    logger.info(f"🚀 Iniciando Animal-AI Service en {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=config.debug_mode,
        log_level=config.log_level.lower(),
        access_log=True
    )

