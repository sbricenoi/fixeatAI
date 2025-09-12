"""
AI Schema Analyzer - Wrapper simple que usa Enhanced AI Analyzer
Mantiene compatibilidad con main.py
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any

from .enhanced_ai_analyzer import EnhancedAISchemaAnalyzer
from .config import ETLConfig

logger = logging.getLogger("etl-service.ai-analyzer")


class AISchemaAnalyzer:
    """Wrapper para Enhanced AI Analyzer que mantiene compatibilidad"""
    
    def __init__(self, config: ETLConfig):
        self.enhanced_analyzer = EnhancedAISchemaAnalyzer(config)
        logger.info("🤖 AISchemaAnalyzer inicializado (usando Enhanced AI Analyzer)")
    
    async def initialize(self) -> bool:
        """Inicializar analizador"""
        return await self.enhanced_analyzer.initialize()
    
    async def analyze_table_context(self, database_name: str, table_name: str, table_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar contexto de tabla (usa Enhanced AI)"""
        return await self.enhanced_analyzer.analyze_table_context_enhanced(database_name, table_name, table_meta)
    
    async def infer_business_context(self, schema: Dict[str, Any], database_name: str = "default") -> Dict[str, Any]:
        """Inferir contexto de negocio"""
        return await self.enhanced_analyzer.infer_business_context_enhanced(schema, database_name)
    
    async def generate_etl_recommendations(self, table_analyses: Dict[str, Any], database_name: str = "default") -> List[Dict[str, Any]]:
        """Generar recomendaciones ETL"""
        return await self.enhanced_analyzer.generate_etl_recommendations_enhanced(table_analyses, database_name)
    
    def health_check(self) -> bool:
        """Health check del analizador"""
        return self.enhanced_analyzer.health_check()


# Alias para compatibilidad
SchemaAnalyzer = AISchemaAnalyzer
