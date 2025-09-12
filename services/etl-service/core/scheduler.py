"""
ETL Scheduler - Programador de tareas ETL automáticas
Maneja ejecución programada de sincronizaciones
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime, time, timedelta
import schedule

from .config import ETLConfig
from .pipeline import ETLPipeline

logger = logging.getLogger("etl-service.scheduler")


class ETLScheduler:
    """Programador de tareas ETL"""
    
    def __init__(self, config: ETLConfig, pipeline: ETLPipeline):
        self.config = config
        self.pipeline = pipeline
        
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.schedule = schedule
        
        logger.info("🕐 ETLScheduler inicializado")
    
    async def start(self) -> bool:
        """Iniciar scheduler automático"""
        
        if self.running:
            logger.warning("⚠️ Scheduler ya está ejecutándose")
            return False
        
        try:
            # Configurar tareas programadas
            self._setup_schedules()
            
            # Iniciar loop del scheduler
            self.running = True
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            logger.info("✅ ETL Scheduler iniciado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando scheduler: {e}")
            self.running = False
            return False
    
    async def stop(self):
        """Detener scheduler"""
        
        self.running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Limpiar tareas programadas
        self.schedule.clear()
        
        logger.info("🛑 ETL Scheduler detenido")
    
    async def pause(self):
        """Pausar scheduler temporalmente"""
        self.running = False
        logger.info("⏸️ ETL Scheduler pausado")
    
    async def resume(self):
        """Reanudar scheduler"""
        if not self.running and not self.scheduler_task:
            await self.start()
        else:
            self.running = True
            logger.info("▶️ ETL Scheduler reanudado")
    
    def _setup_schedules(self):
        """Configurar tareas programadas"""
        
        # Limpiar tareas previas
        self.schedule.clear()
        
        # Sincronización incremental cada X horas
        incremental_hours = self.config.incremental_hours
        self.schedule.every(incremental_hours).hours.do(self._schedule_incremental_sync)
        
        # Sincronización completa diaria
        full_sync_time = self.config.full_sync_time
        self.schedule.every().day.at(full_sync_time).do(self._schedule_full_sync)
        
        # Limpieza de logs/métricas semanal (domingo a las 3 AM)
        self.schedule.every().sunday.at("03:00").do(self._schedule_maintenance)
        
        logger.info(f"📅 Tareas programadas: Incremental cada {incremental_hours}h, Completa a las {full_sync_time}")
    
    async def _scheduler_loop(self):
        """Loop principal del scheduler"""
        
        logger.info("🔄 Iniciando loop del scheduler")
        
        while self.running:
            try:
                # Ejecutar tareas pendientes
                self.schedule.run_pending()
                
                # Esperar 1 minuto antes de revisar de nuevo
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                logger.info("✅ Scheduler loop cancelado")
                break
            except Exception as e:
                logger.error(f"❌ Error en scheduler loop: {e}")
                await asyncio.sleep(60)  # Continuar después de error
    
    def _schedule_incremental_sync(self):
        """Programar sincronización incremental"""
        logger.info("📋 Programando sincronización incremental")
        
        # Crear tarea asíncrona para la sincronización
        asyncio.create_task(self._execute_incremental_sync())
    
    def _schedule_full_sync(self):
        """Programar sincronización completa"""
        logger.info("📋 Programando sincronización completa")
        
        # Crear tarea asíncrona para la sincronización
        asyncio.create_task(self._execute_full_sync())
    
    def _schedule_maintenance(self):
        """Programar tareas de mantenimiento"""
        logger.info("📋 Programando tareas de mantenimiento")
        
        asyncio.create_task(self._execute_maintenance())
    
    async def _execute_incremental_sync(self):
        """Ejecutar sincronización incremental"""
        
        try:
            logger.info("🔄 Iniciando sincronización incremental programada")
            
            # Ejecutar ETL incremental
            results = await self.pipeline.execute_sync(
                sync_type="incremental",
                force=False
            )
            
            # Log resultados
            total_ingested = sum(r.get("ingested", 0) for r in results.values() if isinstance(r, dict))
            total_errors = sum(len(r.get("errors", [])) for r in results.values() if isinstance(r, dict))
            
            if total_errors == 0:
                logger.info(f"✅ Sincronización incremental completada: {total_ingested} documentos ingresados")
            else:
                logger.warning(f"⚠️ Sincronización incremental completada con {total_errors} errores: {total_ingested} documentos ingresados")
            
        except Exception as e:
            logger.error(f"❌ Error en sincronización incremental programada: {e}")
    
    async def _execute_full_sync(self):
        """Ejecutar sincronización completa"""
        
        try:
            logger.info("🔄 Iniciando sincronización completa programada")
            
            # Ejecutar ETL completo
            results = await self.pipeline.execute_sync(
                sync_type="full",
                force=True
            )
            
            # Log resultados
            total_ingested = sum(r.get("ingested", 0) for r in results.values() if isinstance(r, dict))
            total_errors = sum(len(r.get("errors", [])) for r in results.values() if isinstance(r, dict))
            
            if total_errors == 0:
                logger.info(f"✅ Sincronización completa exitosa: {total_ingested} documentos ingresados")
            else:
                logger.warning(f"⚠️ Sincronización completa con {total_errors} errores: {total_ingested} documentos ingresados")
            
        except Exception as e:
            logger.error(f"❌ Error en sincronización completa programada: {e}")
    
    async def _execute_maintenance(self):
        """Ejecutar tareas de mantenimiento"""
        
        try:
            logger.info("🧹 Iniciando tareas de mantenimiento programadas")
            
            # Limpiar logs antiguos (ejemplo)
            # TODO: Implementar limpieza real de logs/métricas
            
            # Optimizar configuraciones basadas en métricas
            # TODO: Implementar optimización automática
            
            logger.info("✅ Tareas de mantenimiento completadas")
            
        except Exception as e:
            logger.error(f"❌ Error en tareas de mantenimiento: {e}")
    
    def is_running(self) -> bool:
        """Verificar si el scheduler está ejecutándose"""
        return self.running and self.scheduler_task is not None and not self.scheduler_task.done()
    
    def get_next_incremental(self) -> Optional[datetime]:
        """Obtener fecha/hora de próxima sincronización incremental"""
        
        try:
            # Buscar próximo job incremental
            for job in self.schedule.jobs:
                if hasattr(job, 'job_func') and job.job_func == self._schedule_incremental_sync:
                    next_run = job.next_run
                    if next_run:
                        return next_run
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo próxima sincronización incremental: {e}")
            return None
    
    def get_next_full_sync(self) -> Optional[datetime]:
        """Obtener fecha/hora de próxima sincronización completa"""
        
        try:
            # Buscar próximo job de sync completo
            for job in self.schedule.jobs:
                if hasattr(job, 'job_func') and job.job_func == self._schedule_full_sync:
                    next_run = job.next_run
                    if next_run:
                        return next_run
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo próxima sincronización completa: {e}")
            return None
    
    def get_schedule_info(self) -> Dict[str, Any]:
        """Obtener información completa del schedule"""
        
        return {
            "running": self.is_running(),
            "total_jobs": len(self.schedule.jobs),
            "incremental_hours": self.config.incremental_hours,
            "full_sync_time": self.config.full_sync_time,
            "next_incremental": self.get_next_incremental(),
            "next_full_sync": self.get_next_full_sync(),
            "jobs": [
                {
                    "job_func": getattr(job, 'job_func', 'unknown').__name__ if hasattr(job, 'job_func') else 'unknown',
                    "next_run": job.next_run,
                    "interval": getattr(job, 'interval', None)
                }
                for job in self.schedule.jobs
            ]
        }


# ================================================================
# EJEMPLO DE USO
# ================================================================

if __name__ == "__main__":
    import asyncio
    from .config import ETLConfig
    from .database import DatabaseManager
    from .ai_analyzer import AISchemaAnalyzer
    from .pipeline import ETLPipeline
    
    async def test_scheduler():
        # Inicializar componentes
        config = ETLConfig()
        db_manager = DatabaseManager(config)
        ai_analyzer = AISchemaAnalyzer(config)
        pipeline = ETLPipeline(config, db_manager, ai_analyzer)
        
        # Crear scheduler
        scheduler = ETLScheduler(config, pipeline)
        
        # Iniciar scheduler
        await scheduler.start()
        
        # Mostrar info del schedule
        schedule_info = scheduler.get_schedule_info()
        print("Schedule info:", schedule_info)
        
        # Ejecutar por 30 segundos
        await asyncio.sleep(30)
        
        # Detener scheduler
        await scheduler.stop()
        
        print("Test completado")
    
    asyncio.run(test_scheduler())
