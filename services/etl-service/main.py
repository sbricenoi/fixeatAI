#!/usr/bin/env python3
"""
ETL Service - Microservicio independiente para extracción inteligente BD → KB
Puerto: 9000 (configurable)
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
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv("ETL_LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.getenv("ETL_LOG_FILE", "logs/etl-service.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("etl-service")

# Importar módulos internos del ETL Service
from core.config import ETLConfig
from core.database import DatabaseManager
from core.ai_analyzer import AISchemaAnalyzer
from core.pipeline import ETLPipeline
from core.scheduler import ETLScheduler
from core.monitor import ETLMonitor
from models.requests import *
from models.responses import *

# Inicializar configuración
config = ETLConfig()

# Crear aplicación FastAPI
app = FastAPI(
    title="ETL Service",
    description="Microservicio independiente para extracción inteligente BD → KB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS independiente
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Inicializar componentes principales
db_manager = DatabaseManager(config)
ai_analyzer = AISchemaAnalyzer(config)
etl_pipeline = ETLPipeline(config, db_manager, ai_analyzer)
scheduler = ETLScheduler(config, etl_pipeline)
monitor = ETLMonitor(config)

# Estado global del servicio
service_state = {
    "started_at": datetime.utcnow(),
    "status": "initializing",
    "active_jobs": {},
    "last_sync": None,
    "total_syncs": 0,
    "error_count": 0
}

@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio ETL"""
    logger.info("🚀 Iniciando ETL Service...")
    
    try:
        # Verificar conexiones de BD
        await db_manager.test_connections()
        logger.info("✅ Conexiones de BD verificadas")
        
        # Inicializar AI Analyzer
        await ai_analyzer.initialize()
        logger.info("✅ AI Analyzer inicializado")
        
        # Cargar configuraciones existentes
        await etl_pipeline.load_configs()
        logger.info("✅ Configuraciones ETL cargadas")
        
        # Iniciar scheduler si está habilitado
        if config.etl_enabled:
            await scheduler.start()
            logger.info("✅ Scheduler iniciado")
        
        service_state["status"] = "running"
        logger.info("🎉 ETL Service iniciado correctamente en puerto {config.service_port}")
        
    except Exception as e:
        logger.error(f"❌ Error iniciando ETL Service: {e}")
        service_state["status"] = "error"
        service_state["error"] = str(e)

@app.on_event("shutdown") 
async def shutdown_event():
    """Limpieza al cerrar el servicio"""
    logger.info("🛑 Cerrando ETL Service...")
    
    try:
        # Parar scheduler
        await scheduler.stop()
        
        # Cerrar conexiones
        await db_manager.close_connections()
        
        logger.info("✅ ETL Service cerrado correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error cerrando ETL Service: {e}")

# ================================================================
# ENDPOINTS DE SALUD Y ESTADO
# ================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check independiente del servicio ETL"""
    return HealthResponse(
        status="healthy" if service_state["status"] == "running" else "unhealthy",
        service="etl-service",
        version="1.0.0",
        uptime_seconds=int((datetime.utcnow() - service_state["started_at"]).total_seconds()),
        checks={
            "database": await db_manager.health_check(),
            "ai_analyzer": ai_analyzer.health_check(),
            "scheduler": scheduler.is_running(),
            "pipeline": etl_pipeline.is_healthy()
        }
    )

@app.get("/status", response_model=ServiceStatusResponse)
async def get_service_status():
    """Estado detallado del servicio ETL"""
    return ServiceStatusResponse(
        service_info={
            "name": "etl-service",
            "version": "1.0.0",
            "started_at": service_state["started_at"],
            "status": service_state["status"],
            "config": {
                "databases": list(db_manager.get_database_names()),
                "etl_enabled": config.etl_enabled,
                "batch_size": config.batch_size,
                "incremental_hours": config.incremental_hours
            }
        },
        active_jobs=service_state["active_jobs"],
        statistics={
            "total_syncs": service_state["total_syncs"],
            "last_sync": service_state["last_sync"],
            "error_count": service_state["error_count"],
            "uptime_hours": round((datetime.utcnow() - service_state["started_at"]).total_seconds() / 3600, 2)
        },
        scheduler_status={
            "running": scheduler.is_running(),
            "next_incremental": scheduler.get_next_incremental(),
            "next_full_sync": scheduler.get_next_full_sync()
        }
    )

# ================================================================
# ENDPOINTS DE DESCUBRIMIENTO Y ANÁLISIS
# ================================================================

@app.post("/api/v1/discover-schema", response_model=SchemaDiscoveryResponse)
async def discover_database_schema(
    request: SchemaDiscoveryRequest = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Descubrimiento automático e inteligente del esquema de BD"""
    
    job_id = f"discover_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    service_state["active_jobs"][job_id] = {
        "type": "schema_discovery",
        "started_at": datetime.utcnow(),
        "status": "running"
    }
    
    try:
        # Seleccionar BD a analizar
        databases = request.databases if request and request.databases else db_manager.get_database_names()
        
        # Ejecutar descubrimiento
        discovery_results = {}
        
        for db_name in databases:
            logger.info(f"🔍 Descubriendo esquema de BD: {db_name}")
            
            # Introspección básica
            schema = await db_manager.introspect_schema(db_name)
            
            # Análisis AI de cada tabla
            table_analysis = {}
            for table_name, table_meta in schema.get("tables", {}).items():
                analysis = await ai_analyzer.analyze_table_context(
                    db_name, table_name, table_meta
                )
                table_analysis[table_name] = analysis
            
            discovery_results[db_name] = {
                "schema": schema,
                "table_analysis": table_analysis,
                "business_context": await ai_analyzer.infer_business_context(schema),
                "recommendations": await ai_analyzer.generate_etl_recommendations(table_analysis)
            }
        
        # Actualizar estado del job
        service_state["active_jobs"][job_id]["status"] = "completed"
        service_state["active_jobs"][job_id]["completed_at"] = datetime.utcnow()
        service_state["active_jobs"][job_id]["results"] = discovery_results
        
        # Generar resumen
        total_tables = sum(len(result["schema"].get("tables", {})) for result in discovery_results.values())
        relevant_tables = sum(
            len([t for t, analysis in result["table_analysis"].items() 
                if analysis.get("ai_relevance", 0) >= 6])
            for result in discovery_results.values()
        )
        
        return SchemaDiscoveryResponse(
            job_id=job_id,
            databases_analyzed=list(databases),
            total_tables=total_tables,
            relevant_tables=relevant_tables,
            discovery_results=discovery_results,
            summary={
                "high_priority_tables": relevant_tables,
                "business_domains_detected": list(set(
                    result["business_context"].get("business_type", "unknown")
                    for result in discovery_results.values()
                )),
                "recommended_strategies": list(set(
                    rec.get("strategy", "unknown")
                    for result in discovery_results.values()
                    for rec in result.get("recommendations", [])
                ))
            }
        )
        
    except Exception as e:
        service_state["active_jobs"][job_id]["status"] = "error"
        service_state["active_jobs"][job_id]["error"] = str(e)
        service_state["error_count"] += 1
        
        logger.error(f"❌ Error en descubrimiento de esquema: {e}")
        raise HTTPException(status_code=500, detail=f"Error en descubrimiento: {str(e)}")

@app.get("/api/v1/schema-analysis/{job_id}", response_model=SchemaAnalysisResponse)
async def get_schema_analysis(job_id: str):
    """Obtener resultados de análisis de esquema por job ID"""
    
    if job_id not in service_state["active_jobs"]:
        raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado")
    
    job = service_state["active_jobs"][job_id]
    
    return SchemaAnalysisResponse(
        job_id=job_id,
        status=job["status"],
        started_at=job["started_at"],
        completed_at=job.get("completed_at"),
        results=job.get("results", {}),
        error=job.get("error")
    )

# ================================================================
# ENDPOINTS DE CONFIGURACIÓN ETL
# ================================================================

@app.post("/api/v1/generate-config", response_model=ETLConfigResponse)
async def generate_etl_config(request: GenerateConfigRequest):
    """Generar configuración ETL automática basada en análisis AI"""
    
    try:
        # Obtener análisis existente o ejecutar nuevo
        if request.analysis_job_id:
            if request.analysis_job_id not in service_state["active_jobs"]:
                raise HTTPException(status_code=404, detail="Analysis job no encontrado")
            
            analysis_results = service_state["active_jobs"][request.analysis_job_id].get("results", {})
        else:
            # Ejecutar análisis rápido
            analysis_results = {}
            for db_name in request.databases:
                schema = await db_manager.introspect_schema(db_name)
                table_analysis = {}
                for table_name, table_meta in schema.get("tables", {}).items():
                    analysis = await ai_analyzer.analyze_table_context(db_name, table_name, table_meta)
                    table_analysis[table_name] = analysis
                analysis_results[db_name] = {"table_analysis": table_analysis}
        
        # Generar configuración automática
        generated_config = await etl_pipeline.generate_config_from_analysis(
            analysis_results, 
            request.priority_filter,
            request.custom_rules
        )
        
        # Guardar configuración si se solicita
        if request.save_config:
            config_id = await etl_pipeline.save_config(generated_config)
        else:
            config_id = None
        
        return ETLConfigResponse(
            config_id=config_id,
            generated_config=generated_config,
            summary={
                "total_tables": len(generated_config.get("tables", {})),
                "enabled_tables": len([t for t, cfg in generated_config.get("tables", {}).items() if cfg.get("enabled", False)]),
                "strategies": list(set(cfg.get("strategy", "unknown") for cfg in generated_config.get("tables", {}).values())),
                "estimated_docs": sum(cfg.get("estimated_docs", 0) for cfg in generated_config.get("tables", {}).values())
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando configuración ETL: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando configuración: {str(e)}")

@app.get("/api/v1/config", response_model=Dict[str, Any])
async def get_current_config():
    """Obtener configuración ETL actual"""
    return await etl_pipeline.get_current_config()

@app.put("/api/v1/config/{table_name}")
async def update_table_config(table_name: str, config: Dict[str, Any]):
    """Actualizar configuración de tabla específica"""
    try:
        await etl_pipeline.update_table_config(table_name, config)
        return {"status": "updated", "table": table_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# ENDPOINTS DE EJECUCIÓN ETL
# ================================================================

@app.post("/api/v1/etl/sync", response_model=ETLJobResponse)
async def execute_etl_sync(
    request: ETLSyncRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Ejecutar sincronización ETL (incremental o completa)"""
    
    job_id = f"etl_sync_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Registrar job
    service_state["active_jobs"][job_id] = {
        "type": "etl_sync",
        "started_at": datetime.utcnow(),
        "status": "running",
        "config": request.dict()
    }
    
    # Ejecutar ETL en background
    background_tasks.add_task(
        execute_etl_background,
        job_id,
        request
    )
    
    return ETLJobResponse(
        job_id=job_id,
        status="started",
        message="ETL sync iniciado en background",
        started_at=datetime.utcnow()
    )

async def execute_etl_background(job_id: str, request: ETLSyncRequest):
    """Ejecutar ETL en background task"""
    
    try:
        logger.info(f"🚀 Iniciando ETL sync job: {job_id}")
        
        # Ejecutar pipeline ETL
        results = await etl_pipeline.execute_sync(
            databases=request.databases,
            tables=request.tables,
            sync_type=request.sync_type,
            batch_size=request.batch_size,
            force=request.force_sync
        )
        
        # Actualizar estado del job
        service_state["active_jobs"][job_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "results": results,
            "total_extracted": sum(r.get("extracted", 0) for r in results.values()),
            "total_ingested": sum(r.get("ingested", 0) for r in results.values())
        })
        
        # Actualizar estadísticas globales
        service_state["total_syncs"] += 1
        service_state["last_sync"] = datetime.utcnow()
        
        logger.info(f"✅ ETL sync completado: {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en ETL sync {job_id}: {e}")
        
        service_state["active_jobs"][job_id].update({
            "status": "error",
            "completed_at": datetime.utcnow(),
            "error": str(e)
        })
        
        service_state["error_count"] += 1

@app.get("/api/v1/etl/job/{job_id}", response_model=ETLJobStatusResponse)
async def get_etl_job_status(job_id: str):
    """Obtener estado de job ETL específico"""
    
    if job_id not in service_state["active_jobs"]:
        raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado")
    
    job = service_state["active_jobs"][job_id]
    
    return ETLJobStatusResponse(
        job_id=job_id,
        status=job["status"],
        started_at=job["started_at"],
        completed_at=job.get("completed_at"),
        progress=await etl_pipeline.get_job_progress(job_id),
        results=job.get("results", {}),
        error=job.get("error")
    )

# ================================================================
# ENDPOINTS DE MONITOREO Y MÉTRICAS
# ================================================================

@app.get("/api/v1/metrics", response_model=ETLMetricsResponse)
async def get_etl_metrics():
    """Métricas detalladas del servicio ETL"""
    
    return ETLMetricsResponse(
        service_metrics={
            "uptime_hours": round((datetime.utcnow() - service_state["started_at"]).total_seconds() / 3600, 2),
            "total_jobs": len(service_state["active_jobs"]),
            "successful_jobs": len([j for j in service_state["active_jobs"].values() if j["status"] == "completed"]),
            "failed_jobs": service_state["error_count"],
            "success_rate": round(
                (len([j for j in service_state["active_jobs"].values() if j["status"] == "completed"]) / 
                 max(len(service_state["active_jobs"]), 1)) * 100, 2
            )
        },
        database_metrics=await db_manager.get_metrics(),
        pipeline_metrics=await etl_pipeline.get_metrics(),
        quality_metrics=await monitor.get_quality_metrics(),
        performance_metrics=await monitor.get_performance_metrics()
    )

@app.get("/api/v1/quality-report", response_model=QualityReportResponse)
async def get_quality_report():
    """Reporte de calidad detallado"""
    
    return QualityReportResponse(
        overall_score=await monitor.calculate_overall_quality_score(),
        table_scores=await monitor.get_table_quality_scores(),
        quality_issues=await monitor.detect_quality_issues(),
        recommendations=await monitor.generate_quality_recommendations(),
        trends=await monitor.get_quality_trends()
    )

# ================================================================
# ENDPOINTS DE ADMINISTRACIÓN
# ================================================================

@app.post("/api/v1/admin/pause")
async def pause_etl_service():
    """Pausar servicio ETL (detener scheduler)"""
    try:
        await scheduler.pause()
        return {"status": "paused", "message": "ETL Service pausado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/resume") 
async def resume_etl_service():
    """Reanudar servicio ETL"""
    try:
        await scheduler.resume()
        return {"status": "resumed", "message": "ETL Service reanudado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/clear-jobs")
async def clear_completed_jobs():
    """Limpiar jobs completados del estado"""
    completed_jobs = [
        job_id for job_id, job in service_state["active_jobs"].items()
        if job["status"] in ["completed", "error"]
    ]
    
    for job_id in completed_jobs:
        del service_state["active_jobs"][job_id]
    
    return {
        "cleared_jobs": len(completed_jobs),
        "remaining_jobs": len(service_state["active_jobs"])
    }

# ================================================================
# PROMETHEUS METRICS (opcional)
# ================================================================

if config.metrics_enabled:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
    
    # Métricas Prometheus (con protección contra duplicados)
    try:
        etl_jobs_total = Counter('etl_jobs_total', 'Total ETL jobs executed', ['status', 'database'])
        etl_duration_seconds = Histogram('etl_duration_seconds', 'ETL job duration', ['database'])
        etl_documents_ingested = Counter('etl_documents_ingested_total', 'Total documents ingested', ['database', 'table'])
        etl_service_uptime = Gauge('etl_service_uptime_seconds', 'Service uptime in seconds')
    except ValueError as e:
        logger.warning(f"⚠️ Métricas Prometheus ya registradas: {e}")
        etl_jobs_total = etl_duration_seconds = etl_documents_ingested = etl_service_uptime = None
    
    @app.get("/metrics")
    async def prometheus_metrics():
        """Endpoint para métricas de Prometheus"""
        # Actualizar métricas
        etl_service_uptime.set((datetime.utcnow() - service_state["started_at"]).total_seconds())
        
        return generate_latest()

# ================================================================
# MAIN - PUNTO DE ENTRADA
# ================================================================

def main():
    """Punto de entrada principal del servicio ETL"""
    
    # Configurar logging final
    log_level = config.log_level.upper()
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    logger.info(f"🔄 Iniciando ETL Service en puerto {config.service_port}")
    logger.info(f"📊 Configuración: {config.service_name} - {len(config.databases)} bases de datos")
    
    # Ejecutar servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.service_port,
        log_level=log_level.lower(),
        access_log=True,
        reload=config.env == "development"
    )

if __name__ == "__main__":
    main()
