"""Métricas de calidad para referencias y resultados de búsqueda.

Este módulo implementa métricas para evaluar:
1. Relevancia de resultados (precision, recall, NDCG)
2. Calidad de referencias (coverage, coherencia)
3. Calidad de contextos (completitud, precisión)
4. Performance del sistema (latencia, throughput)
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import time
from dataclasses import dataclass, field


@dataclass
class SearchQualityMetrics:
    """Métricas de calidad para una búsqueda."""
    
    # Métricas de relevancia
    precision_at_k: float = 0.0  # Precisión en top-K resultados
    recall: float = 0.0  # Recall (cuántos relevantes se recuperaron)
    f1_score: float = 0.0  # F1 score
    
    # Métricas de contexto
    avg_context_length: float = 0.0  # Longitud promedio de contextos
    context_coverage: float = 0.0  # % de términos clave cubiertos
    
    # Métricas de referencias
    num_references: int = 0  # Número de referencias retornadas
    num_with_page: int = 0  # Referencias con número de página
    num_with_url: int = 0  # Referencias con URL navegable
    
    # Métricas de performance
    search_latency_ms: float = 0.0  # Latencia de búsqueda
    total_docs_searched: int = 0  # Total de documentos buscados
    
    # Score compuesto
    overall_quality_score: float = 0.0  # Score 0-100
    
    # Detalles adicionales
    metadata: Dict[str, Any] = field(default_factory=dict)


class QualityMetricsCalculator:
    """Calculador de métricas de calidad."""
    
    def __init__(self):
        """Inicializa el calculador de métricas."""
        self.search_start_time: Optional[float] = None
    
    def start_search_timer(self) -> None:
        """Inicia timer para medir latencia de búsqueda."""
        self.search_start_time = time.time()
    
    def calculate_search_metrics(
        self,
        query: str,
        results: List[Dict[str, Any]],
        relevant_doc_ids: Optional[List[str]] = None
    ) -> SearchQualityMetrics:
        """Calcula métricas de calidad para una búsqueda.
        
        Args:
            query: Consulta realizada
            results: Lista de resultados (hits) devueltos
            relevant_doc_ids: IDs de documentos relevantes (para calcular recall)
            
        Returns:
            SearchQualityMetrics con todas las métricas calculadas
        """
        metrics = SearchQualityMetrics()
        
        if not results:
            return metrics
        
        # Calcular latencia
        if self.search_start_time:
            metrics.search_latency_ms = (time.time() - self.search_start_time) * 1000
            self.search_start_time = None
        
        # Métricas básicas
        metrics.num_references = len(results)
        metrics.total_docs_searched = len(results)
        
        # Contar referencias con página y URL
        for hit in results:
            if hit.get("metadata", {}).get("page"):
                metrics.num_with_page += 1
            if hit.get("document_url"):
                metrics.num_with_url += 1
        
        # Calcular longitud promedio de contextos
        context_lengths = []
        for hit in results:
            context = hit.get("context", "") or hit.get("snippet", "")
            context_lengths.append(len(context))
        
        if context_lengths:
            metrics.avg_context_length = sum(context_lengths) / len(context_lengths)
        
        # Calcular coverage de términos clave
        query_terms = set(query.lower().split())
        if query_terms:
            covered_terms = set()
            for hit in results:
                context = (hit.get("context", "") or hit.get("snippet", "")).lower()
                for term in query_terms:
                    if term in context:
                        covered_terms.add(term)
            
            metrics.context_coverage = len(covered_terms) / len(query_terms)
        
        # Calcular precision y recall si tenemos documentos relevantes
        if relevant_doc_ids:
            retrieved_ids = {hit["doc_id"] for hit in results}
            relevant_ids = set(relevant_doc_ids)
            
            true_positives = len(retrieved_ids & relevant_ids)
            
            if retrieved_ids:
                metrics.precision_at_k = true_positives / len(retrieved_ids)
            
            if relevant_ids:
                metrics.recall = true_positives / len(relevant_ids)
            
            if metrics.precision_at_k + metrics.recall > 0:
                metrics.f1_score = 2 * (metrics.precision_at_k * metrics.recall) / \
                                  (metrics.precision_at_k + metrics.recall)
        
        # Calcular score de calidad global (0-100)
        metrics.overall_quality_score = self._calculate_overall_score(metrics)
        
        # Metadata adicional
        metrics.metadata = {
            "query": query,
            "num_results": len(results),
            "avg_score": sum(hit.get("score", 0) for hit in results) / len(results) if results else 0,
            "top_score": results[0].get("score", 0) if results else 0,
        }
        
        return metrics
    
    def _calculate_overall_score(self, metrics: SearchQualityMetrics) -> float:
        """Calcula score de calidad global (0-100).
        
        Componentes:
        - 30% Relevancia (precision/recall/f1)
        - 25% Calidad de contextos (longitud, coverage)
        - 25% Calidad de referencias (página, URL)
        - 20% Performance (latencia)
        """
        score = 0.0
        
        # Componente de relevancia (30%)
        if metrics.f1_score > 0:
            score += metrics.f1_score * 30
        elif metrics.precision_at_k > 0:
            score += metrics.precision_at_k * 30
        else:
            # Si no tenemos ground truth, asumimos relevancia basada en scores
            score += min(30, metrics.num_references * 6)  # Max 5 refs = 30 puntos
        
        # Componente de contextos (25%)
        if metrics.avg_context_length > 0:
            # Ideal: 1200 chars
            context_score = min(1.0, metrics.avg_context_length / 1200) * 12.5
            score += context_score
        
        if metrics.context_coverage > 0:
            score += metrics.context_coverage * 12.5
        
        # Componente de referencias (25%)
        if metrics.num_references > 0:
            page_ratio = metrics.num_with_page / metrics.num_references
            url_ratio = metrics.num_with_url / metrics.num_references
            score += (page_ratio * 12.5) + (url_ratio * 12.5)
        
        # Componente de performance (20%)
        if metrics.search_latency_ms > 0:
            # Ideal: < 100ms = 20 puntos, 1000ms = 10 puntos, > 2000ms = 0 puntos
            if metrics.search_latency_ms < 100:
                score += 20
            elif metrics.search_latency_ms < 1000:
                score += 20 - ((metrics.search_latency_ms - 100) / 900 * 10)
            elif metrics.search_latency_ms < 2000:
                score += 10 - ((metrics.search_latency_ms - 1000) / 1000 * 10)
        
        return min(100.0, score)
    
    def generate_report(self, metrics: SearchQualityMetrics) -> str:
        """Genera reporte legible de métricas.
        
        Args:
            metrics: Métricas calculadas
            
        Returns:
            String con reporte formateado
        """
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE CALIDAD DE BÚSQUEDA")
        report.append("=" * 60)
        report.append("")
        
        # Resumen ejecutivo
        report.append(f"📊 SCORE GLOBAL: {metrics.overall_quality_score:.1f}/100")
        report.append("")
        
        # Métricas de relevancia
        if metrics.precision_at_k > 0 or metrics.recall > 0:
            report.append("📍 RELEVANCIA:")
            report.append(f"  Precision@K: {metrics.precision_at_k:.2%}")
            report.append(f"  Recall:      {metrics.recall:.2%}")
            report.append(f"  F1 Score:    {metrics.f1_score:.2%}")
            report.append("")
        
        # Métricas de contexto
        report.append("📝 CONTEXTOS:")
        report.append(f"  Longitud promedio: {metrics.avg_context_length:.0f} chars")
        report.append(f"  Coverage términos: {metrics.context_coverage:.0%}")
        report.append("")
        
        # Métricas de referencias
        report.append("🔗 REFERENCIAS:")
        report.append(f"  Total referencias: {metrics.num_references}")
        report.append(f"  Con página:        {metrics.num_with_page} ({metrics.num_with_page/metrics.num_references:.0%})" if metrics.num_references > 0 else "  Con página:        0")
        report.append(f"  Con URL:           {metrics.num_with_url} ({metrics.num_with_url/metrics.num_references:.0%})" if metrics.num_references > 0 else "  Con URL:           0")
        report.append("")
        
        # Métricas de performance
        report.append("⚡ PERFORMANCE:")
        report.append(f"  Latencia: {metrics.search_latency_ms:.1f}ms")
        report.append(f"  Documentos buscados: {metrics.total_docs_searched}")
        report.append("")
        
        # Metadata adicional
        if metrics.metadata:
            report.append("ℹ️  INFORMACIÓN ADICIONAL:")
            for key, value in metrics.metadata.items():
                report.append(f"  {key}: {value}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


# Función de conveniencia
def evaluate_search_quality(
    query: str,
    results: List[Dict[str, Any]],
    relevant_doc_ids: Optional[List[str]] = None,
    print_report: bool = False
) -> SearchQualityMetrics:
    """Evalúa la calidad de resultados de búsqueda.
    
    Args:
        query: Consulta realizada
        results: Resultados de búsqueda
        relevant_doc_ids: IDs de documentos relevantes (opcional)
        print_report: Si imprimir reporte
        
    Returns:
        SearchQualityMetrics con métricas calculadas
    """
    calculator = QualityMetricsCalculator()
    metrics = calculator.calculate_search_metrics(query, results, relevant_doc_ids)
    
    if print_report:
        print(calculator.generate_report(metrics))
    
    return metrics


if __name__ == "__main__":
    # Test básico
    mock_results = [
        {
            "doc_id": "manual_rational_p23",
            "score": 0.95,
            "context": "Error S_55: El motor del ventilador no alcanza las revoluciones especificadas. Causa: Bloqueo mecánico o fallo eléctrico. Solución: Verificar conexiones y estado del motor." * 5,
            "document_url": "https://example.com/manual.pdf#page=23",
            "metadata": {"page": 23, "brand": "RATIONAL"}
        },
        {
            "doc_id": "manual_rational_p45",
            "score": 0.88,
            "context": "Diagnóstico de fallas del sistema de ventilación. Los problemas más comunes incluyen..." * 4,
            "document_url": "https://example.com/manual.pdf#page=45",
            "metadata": {"page": 45, "brand": "RATIONAL"}
        },
        {
            "doc_id": "troubleshooting_guide",
            "score": 0.75,
            "context": "Guía general de resolución de problemas para equipos industriales." * 3,
            "document_url": "/view-document/troubleshooting_guide",
            "metadata": {}
        }
    ]
    
    metrics = evaluate_search_quality(
        query="error ventilador motor",
        results=mock_results,
        print_report=True
    )
    
    print(f"\n✅ Score global: {metrics.overall_quality_score:.1f}/100")


