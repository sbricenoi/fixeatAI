"""
ETL Monitor - Sistema de monitoreo y métricas para ETL Service
Recopila métricas de calidad, rendimiento y estado del sistema
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .config import ETLConfig

logger = logging.getLogger("etl-service.monitor")


@dataclass
class QualityMetric:
    """Métrica de calidad de datos"""
    timestamp: datetime
    table_name: str
    database_name: str
    quality_score: float
    issues_detected: int
    documents_processed: int


@dataclass 
class PerformanceMetric:
    """Métrica de rendimiento"""
    timestamp: datetime
    operation_type: str
    duration_seconds: float
    records_processed: int
    throughput_per_second: float


class ETLMonitor:
    """Monitor de métricas y calidad del ETL"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        
        # Almacenamiento de métricas en memoria
        self.quality_metrics: List[QualityMetric] = []
        self.performance_metrics: List[PerformanceMetric] = []
        
        # Contadores globales
        self.global_stats = {
            "total_extractions": 0,
            "total_transformations": 0,
            "total_ingestions": 0,
            "total_errors": 0,
            "start_time": datetime.utcnow()
        }
        
        logger.info("📊 ETLMonitor inicializado")
    
    def record_quality_metric(self, table_name: str, database_name: str, 
                             quality_score: float, issues_detected: int = 0,
                             documents_processed: int = 0):
        """Registrar métrica de calidad"""
        
        metric = QualityMetric(
            timestamp=datetime.utcnow(),
            table_name=table_name,
            database_name=database_name,
            quality_score=quality_score,
            issues_detected=issues_detected,
            documents_processed=documents_processed
        )
        
        self.quality_metrics.append(metric)
        
        # Mantener solo últimas 1000 métricas
        if len(self.quality_metrics) > 1000:
            self.quality_metrics = self.quality_metrics[-1000:]
        
        logger.debug(f"📊 Métrica de calidad registrada: {table_name} = {quality_score}")
    
    def record_performance_metric(self, operation_type: str, duration_seconds: float,
                                 records_processed: int = 0):
        """Registrar métrica de rendimiento"""
        
        throughput = records_processed / duration_seconds if duration_seconds > 0 else 0
        
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            operation_type=operation_type,
            duration_seconds=duration_seconds,
            records_processed=records_processed,
            throughput_per_second=throughput
        )
        
        self.performance_metrics.append(metric)
        
        # Mantener solo últimas 1000 métricas
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
        
        # Actualizar contadores globales
        if operation_type == "extraction":
            self.global_stats["total_extractions"] += 1
        elif operation_type == "transformation":
            self.global_stats["total_transformations"] += 1
        elif operation_type == "ingestion":
            self.global_stats["total_ingestions"] += 1
        
        logger.debug(f"⏱️ Métrica de rendimiento registrada: {operation_type} = {duration_seconds}s")
    
    def record_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Registrar error"""
        
        self.global_stats["total_errors"] += 1
        
        # TODO: Implementar almacenamiento detallado de errores
        logger.error(f"❌ Error registrado [{error_type}]: {error_message}")
    
    async def get_quality_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de calidad"""
        
        if not self.quality_metrics:
            return {
                "overall_quality_score": 0.0,
                "total_issues": 0,
                "total_documents": 0,
                "table_scores": {},
                "recent_metrics": []
            }
        
        # Calcular score general
        total_score = sum(m.quality_score for m in self.quality_metrics)
        overall_score = total_score / len(self.quality_metrics)
        
        # Métricas por tabla
        table_scores = {}
        for metric in self.quality_metrics:
            table_key = f"{metric.database_name}.{metric.table_name}"
            if table_key not in table_scores:
                table_scores[table_key] = []
            table_scores[table_key].append(metric.quality_score)
        
        # Promediar por tabla
        for table_key in table_scores:
            scores = table_scores[table_key]
            table_scores[table_key] = sum(scores) / len(scores)
        
        # Métricas recientes (último día)
        recent_cutoff = datetime.utcnow() - timedelta(days=1)
        recent_metrics = [
            {
                "timestamp": m.timestamp.isoformat(),
                "table": f"{m.database_name}.{m.table_name}",
                "quality_score": m.quality_score,
                "issues": m.issues_detected,
                "documents": m.documents_processed
            }
            for m in self.quality_metrics
            if m.timestamp >= recent_cutoff
        ]
        
        return {
            "overall_quality_score": round(overall_score, 2),
            "total_issues": sum(m.issues_detected for m in self.quality_metrics),
            "total_documents": sum(m.documents_processed for m in self.quality_metrics),
            "table_scores": table_scores,
            "recent_metrics": recent_metrics[-20:]  # Últimas 20
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        
        if not self.performance_metrics:
            return {
                "avg_extraction_time": 0.0,
                "avg_transformation_time": 0.0,
                "avg_ingestion_time": 0.0,
                "total_throughput": 0.0,
                "recent_operations": []
            }
        
        # Agrupar por tipo de operación
        operations = {}
        for metric in self.performance_metrics:
            op_type = metric.operation_type
            if op_type not in operations:
                operations[op_type] = []
            operations[op_type].append(metric)
        
        # Calcular promedios
        avg_times = {}
        for op_type, metrics in operations.items():
            avg_times[f"avg_{op_type}_time"] = sum(m.duration_seconds for m in metrics) / len(metrics)
        
        # Throughput total
        total_records = sum(m.records_processed for m in self.performance_metrics)
        total_time = sum(m.duration_seconds for m in self.performance_metrics)
        total_throughput = total_records / total_time if total_time > 0 else 0
        
        # Operaciones recientes
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_operations = [
            {
                "timestamp": m.timestamp.isoformat(),
                "operation": m.operation_type,
                "duration": m.duration_seconds,
                "records": m.records_processed,
                "throughput": m.throughput_per_second
            }
            for m in self.performance_metrics
            if m.timestamp >= recent_cutoff
        ]
        
        return {
            **avg_times,
            "total_throughput": round(total_throughput, 2),
            "recent_operations": recent_operations[-20:],  # Últimas 20
            "global_stats": self.global_stats.copy()
        }
    
    async def calculate_overall_quality_score(self) -> float:
        """Calcular score de calidad general"""
        
        if not self.quality_metrics:
            return 0.0
        
        # Score ponderado por documentos procesados
        total_weighted_score = 0.0
        total_documents = 0
        
        for metric in self.quality_metrics:
            weight = metric.documents_processed if metric.documents_processed > 0 else 1
            total_weighted_score += metric.quality_score * weight
            total_documents += weight
        
        return total_weighted_score / total_documents if total_documents > 0 else 0.0
    
    async def get_table_quality_scores(self) -> Dict[str, float]:
        """Obtener scores de calidad por tabla"""
        
        table_scores = {}
        
        for metric in self.quality_metrics:
            table_key = f"{metric.database_name}.{metric.table_name}"
            
            if table_key not in table_scores:
                table_scores[table_key] = []
            
            table_scores[table_key].append(metric.quality_score)
        
        # Calcular promedio por tabla
        for table_key in table_scores:
            scores = table_scores[table_key]
            table_scores[table_key] = sum(scores) / len(scores)
        
        return table_scores
    
    async def detect_quality_issues(self) -> List[Dict[str, Any]]:
        """Detectar problemas de calidad"""
        
        issues = []
        
        # Detectar tablas con calidad baja
        table_scores = await self.get_table_quality_scores()
        low_quality_threshold = self.config.quality_threshold
        
        for table, score in table_scores.items():
            if score < low_quality_threshold:
                issues.append({
                    "type": "low_quality_table",
                    "severity": "high" if score < 0.5 else "medium",
                    "table": table,
                    "score": score,
                    "threshold": low_quality_threshold,
                    "recommendation": f"Revisar configuración de extracción/transformación para {table}"
                })
        
        # Detectar alta cantidad de issues
        recent_metrics = [m for m in self.quality_metrics if m.timestamp >= datetime.utcnow() - timedelta(hours=24)]
        
        if recent_metrics:
            avg_issues = sum(m.issues_detected for m in recent_metrics) / len(recent_metrics)
            
            if avg_issues > 10:  # Más de 10 issues promedio por tabla
                issues.append({
                    "type": "high_issue_rate",
                    "severity": "medium",
                    "avg_issues": avg_issues,
                    "recommendation": "Revisar configuraciones de calidad y validación de datos"
                })
        
        return issues
    
    async def generate_quality_recommendations(self) -> List[str]:
        """Generar recomendaciones de calidad"""
        
        recommendations = []
        
        # Analizar métricas recientes
        recent_metrics = [m for m in self.quality_metrics if m.timestamp >= datetime.utcnow() - timedelta(days=7)]
        
        if not recent_metrics:
            recommendations.append("Ejecutar ETL para generar métricas de calidad")
            return recommendations
        
        # Analizar tendencias
        avg_quality = sum(m.quality_score for m in recent_metrics) / len(recent_metrics)
        
        if avg_quality < 0.7:
            recommendations.append("Calidad general baja: revisar configuraciones de transformación IA")
        
        if avg_quality < 0.5:
            recommendations.append("Calidad crítica: verificar documentación de BD y ajustar prompts IA")
        
        # Analizar issues
        total_issues = sum(m.issues_detected for m in recent_metrics)
        
        if total_issues > 100:
            recommendations.append("Alto número de issues detectados: revisar filtros de calidad")
        
        # Analizar rendimiento
        if self.performance_metrics:
            recent_perf = [m for m in self.performance_metrics if m.timestamp >= datetime.utcnow() - timedelta(days=1)]
            
            if recent_perf:
                avg_duration = sum(m.duration_seconds for m in recent_perf) / len(recent_perf)
                
                if avg_duration > 300:  # Más de 5 minutos promedio
                    recommendations.append("Rendimiento lento: considerar ajustar batch_size o optimizar queries")
        
        if not recommendations:
            recommendations.append("Sistema funcionando dentro de parámetros normales")
        
        return recommendations
    
    async def get_quality_trends(self) -> List[Dict[str, Any]]:
        """Obtener tendencias de calidad en el tiempo"""
        
        # Agrupar métricas por día
        daily_metrics = {}
        
        for metric in self.quality_metrics:
            date_key = metric.timestamp.date().isoformat()
            
            if date_key not in daily_metrics:
                daily_metrics[date_key] = []
            
            daily_metrics[date_key].append(metric)
        
        # Calcular tendencias diarias
        trends = []
        
        for date_str, metrics in sorted(daily_metrics.items()):
            avg_quality = sum(m.quality_score for m in metrics) / len(metrics)
            total_docs = sum(m.documents_processed for m in metrics)
            total_issues = sum(m.issues_detected for m in metrics)
            
            trends.append({
                "date": date_str,
                "quality_score": round(avg_quality, 2),
                "documents_processed": total_docs,
                "issues_detected": total_issues,
                "tables_processed": len(set(f"{m.database_name}.{m.table_name}" for m in metrics))
            })
        
        return trends[-30:]  # Últimos 30 días
    
    def export_metrics(self, file_path: Optional[str] = None) -> str:
        """Exportar métricas a archivo JSON"""
        
        if file_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_path = f"metrics_export_{timestamp}.json"
        
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "global_stats": self.global_stats,
            "quality_metrics": [asdict(m) for m in self.quality_metrics],
            "performance_metrics": [asdict(m) for m in self.performance_metrics]
        }
        
        # Convertir datetime a string para JSON
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=datetime_handler, ensure_ascii=False)
        
        logger.info(f"📊 Métricas exportadas a: {file_path}")
        return file_path


# ================================================================
# EJEMPLO DE USO
# ================================================================

if __name__ == "__main__":
    import asyncio
    from .config import ETLConfig
    
    async def test_monitor():
        config = ETLConfig()
        monitor = ETLMonitor(config)
        
        # Simular algunas métricas
        monitor.record_quality_metric("services", "production_db", 8.5, 2, 100)
        monitor.record_quality_metric("equipments", "production_db", 9.2, 0, 50)
        monitor.record_performance_metric("extraction", 45.2, 100)
        monitor.record_performance_metric("transformation", 12.8, 95)
        
        # Obtener métricas
        quality_metrics = await monitor.get_quality_metrics()
        performance_metrics = await monitor.get_performance_metrics()
        
        print("Quality metrics:", quality_metrics)
        print("Performance metrics:", performance_metrics)
        
        # Detectar issues
        issues = await monitor.detect_quality_issues()
        print("Quality issues:", issues)
        
        # Generar recomendaciones
        recommendations = await monitor.generate_quality_recommendations()
        print("Recommendations:", recommendations)
    
    asyncio.run(test_monitor())
