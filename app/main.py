"""Aplicación FastAPI del microservicio IA - Predictor de Fallas.

API REST para diagnóstico inteligente de fallas en equipos de cocina industrial.
Usa RAG (Retrieval-Augmented Generation) con LLM y Knowledge Base vectorial.
"""

from __future__ import annotations

import os
import re
import uuid
from typing import Any, Optional
import json
import logging

import requests
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.predictor.heuristic import infer_from_hits
from services.orch.rag import predict_with_llm
from services.orch.llm_reranker import rerank_with_llm


APP_TITLE = "FixeatAI - Predictor de Fallas"
APP_VERSION = "0.2.0"
APP_DESCRIPTION = "Sistema inteligente de diagnóstico de fallas con RAG y LLM"

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:7070")
TRACE_HEADER = os.getenv("X_TRACE_ID_HEADER", "X-Trace-Id")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"


app = FastAPI(
    title=APP_TITLE, 
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# CORS
_cors_env = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
_allow_origins = ["*"] if _cors_env == "*" else [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _clean_url(url: Optional[str]) -> Optional[str]:
    """Retorna URL limpia con endpoint regional S3 correcto, sin parámetros de firma."""
    if not url:
        return url
    fragment = ""
    if "#" in url:
        url, fragment = url.split("#", 1)
        fragment = "#" + fragment
    if "?" in url:
        url = url.split("?")[0]
    # Normalizar al endpoint regional correcto (evita redirects 301 que la app móvil no sigue)
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
    url = re.sub(r"\.s3(?:\.[\w-]+)?\.amazonaws\.com", f".s3.{region}.amazonaws.com", url)
    return url + fragment


def build_response(
    data: Any,
    message: str = "OK",
    code: str = "OK",
    trace_id: Optional[str] = None,
) -> dict[str, Any]:
    """Construye la respuesta estándar del microservicio.

    Incluye traceId, code, message y data, según política del proyecto.
    """
    return {
        "traceId": trace_id or str(uuid.uuid4()),
        "code": code,
        "message": message,
        "data": data,
    }


def log_event(level: int, trace_id: Optional[str], event: str, **kwargs: Any) -> None:
    """Log estructurado de eventos."""
    payload = {"traceId": trace_id, "event": event, **kwargs}
    logging.log(level, json.dumps(payload, ensure_ascii=False))


class PredictRequest(BaseModel):
    """Request model para predicción de fallas."""
    cliente: dict
    equipo: dict
    descripcion_problema: str
    tecnico: dict


@app.post("/api/v1/predict-fallas")
def predict_fallas(
    req: PredictRequest,
    x_trace_id: Optional[str] = Header(default=None, alias=TRACE_HEADER),
) -> dict[str, Any]:
    """🔧 Predictor de Fallas Principal (CORE).

    Retorna diagnóstico inteligente con:
    - Fallas probables con confidence score
    - Repuestos específicos sugeridos
    - Herramientas necesarias
    - Pasos detallados (seguridad, diagnóstico, reparación)
    - Contextos citables del Knowledge Base

    Flujo:
    1. Búsqueda híbrida en KB (semántica + keywords)
    2. LLM Re-Ranker para ordenar por relevancia
    3. Análisis con GPT-4o-mini usando RAG
    4. Respuesta estructurada con protocolos de seguridad
    """
    if USE_LLM:
        # Modo LLM: RAG Pipeline completo
        data = predict_with_llm(MCP_SERVER_URL, req.descripcion_problema, req.equipo, top_k=10)
        
        # Usar los hits que ya recuperó predict_with_llm
        hits = data.pop("_raw_hits", [])
        
        # Fallback: buscar contextos solo si predict_with_llm no devolvió hits
        if not hits:
            print(f"⚠️  No hay hits disponibles, haciendo búsqueda directa de contextos...")
            try:
                response = requests.post(
                    f"{MCP_SERVER_URL}/tools/kb_search_hybrid",
                    json={
                        "query": req.descripcion_problema,
                        "top_k": 10,
                        "semantic_weight": 0.3,
                        "keyword_weight": 0.7,
                        "context_chars": 2000
                    },
                    timeout=15,
                )
                hits = response.json().get("hits", [])
                print(f"✅ Búsqueda directa: {len(hits)} hits encontrados")
            except Exception as e:
                print(f"❌ Error en búsqueda directa de contextos: {e}")
                hits = []

        # APLICAR LLM RE-RANKER
        if hits:
            marca = req.equipo.get("marca") or req.equipo.get("brand") if req.equipo else None
            modelo = req.equipo.get("modelo") or req.equipo.get("model") if req.equipo else None
            
            print(f"🤖 Aplicando LLM Re-Ranker (query: '{req.descripcion_problema[:50]}...')")
            print(f"   Equipo: {marca or 'N/A'} {modelo or 'N/A'}")
            print(f"   Candidatos: {len(hits)} documentos")
            
            # LLM analiza y ordena por relevancia REAL
            ranked_hits = rerank_with_llm(
                query=req.descripcion_problema,
                candidates=hits,
                marca=marca,
                modelo=modelo,
                top_k=10
            )
            
            # Construir contextos con información del LLM re-ranker
            data["contextos"] = [
                {
                    "fuente": re.sub(r"_page_\d+_chunk_\d+$", "", hit["doc_id"]),
                    "score": round(min(hit["score"], 1.0), 4),
                    "relevance_score": hit.get("llm_relevance_score", 0),
                    "confidence_label": hit.get("llm_confidence", "Media"),
                    "llm_explanation": hit.get("llm_explanation", ""),
                    "contexto": hit.get("context", hit.get("snippet", ""))[:1500],
                    "document_url": _clean_url(hit.get("document_url")),
                    "metadata": {
                        "page": hit.get("metadata", {}).get("page"),
                        "source": hit.get("metadata", {}).get("source"),
                        "brand": hit.get("metadata", {}).get("brand"),
                        "model": hit.get("metadata", {}).get("model"),
                        "source_file": hit.get("metadata", {}).get("source_file"),
                        "chunk_type": hit.get("metadata", {}).get("chunk_type"),
                    },
                }
                for hit in ranked_hits
            ]
            
            # Log de top 3 para debugging
            print(f"📊 Top 3 documentos según LLM:")
            for i, ctx in enumerate(data["contextos"][:3], 1):
                relevance = ctx.get('relevance_score', 0)
                emoji = "🎯" if relevance >= 80 else "⭐" if relevance >= 60 else "📄"
                print(f"  {emoji} {i}. {ctx['fuente'][:60]}")
                print(f"     Relevancia LLM: {relevance}% ({ctx['confidence_label']})")
                if ctx.get('llm_explanation'):
                    print(f"     Razón: {ctx['llm_explanation'][:80]}...")

            # Sincronizar fuentes con los contextos re-rankeados (URLs limpias)
            data["fuentes"] = [
                ctx["document_url"] or ctx["fuente"]
                for ctx in data["contextos"]
                if ctx.get("document_url") or ctx.get("fuente")
            ]

            # Detectar cuando el re-ranker indica que ningún documento es relevante
            max_relevance = max(
                (ctx.get("relevance_score", 0) for ctx in data["contextos"]), default=0
            )
            if max_relevance < 50:
                data["signals"]["low_evidence"] = True
                brand_info = f"{marca or ''} {modelo or ''}".strip()
                data["feedback_coherencia"] = (
                    f"No se encontraron documentos específicos para {brand_info or 'el equipo consultado'} "
                    "en la base de conocimiento. El diagnóstico es genérico y puede no ser preciso para este equipo."
                )
                for falla in data.get("fallas_probables", []):
                    falla["confidence"] = min(falla.get("confidence", 0.3), 0.35)
                print(f"⚠️  low_evidence detectado por re-ranker: max_relevance={max_relevance}%")
        else:
            # Fallback: lista vacía pero con estructura válida
            print(f"⚠️  ADVERTENCIA: No se encontraron documentos para '{req.descripcion_problema}'")
            data["contextos"] = []
            if "fuentes" not in data:
                data["fuentes"] = []
    else:
        # Modo sin LLM: heurística basada en KB
        hits = []
        try:
            response = requests.post(
                f"{MCP_SERVER_URL}/tools/kb_search_extended",
                json={
                    "query": req.descripcion_problema, 
                    "top_k": 10,
                    "context_chars": 2000
                },
                timeout=5,
            )
            hits = response.json().get("hits", [])
        except Exception as e:
            print(f"Warning: No se pudo obtener hits de KB: {e}")
            hits = []
        
        # Heurística basada en hits de la KB
        preds = infer_from_hits(hits, req.descripcion_problema)
        data = {
            "fallas_probables": preds,
            "fuentes": [h.get("doc_id") for h in hits],
            "feedback_coherencia": "Respuesta basada en análisis heurístico",
            "contextos": [
                {
                    "fuente": hit["doc_id"],
                    "score": round(min(hit["score"], 1.0), 4),
                    "contexto": hit.get("context", hit.get("snippet", ""))[:1500],
                    "document_url": hit.get("document_url"),
                    "metadata": {
                        "page": hit.get("metadata", {}).get("page"),
                        "source": hit.get("metadata", {}).get("source"),
                    }
                }
                for hit in hits[:10]
            ]
        }
    
    # Limpiar referencias internas [source:...] del rationale
    for falla in data.get("fallas_probables", []):
        if "rationale" in falla:
            falla["rationale"] = re.sub(r"\s*\[source:[^\]]+\]", "", falla["rationale"]).strip()

    log_event(logging.INFO, x_trace_id, "predict_fallas", num_hits=len(hits), llm_used=USE_LLM)
    return build_response(data=data, message="Predicción generada", code="OK", trace_id=x_trace_id)


@app.get("/health")
def health() -> dict[str, Any]:
    """✅ Health check endpoint."""
    return {"status": "ok", "service": "fixeat-ai-predictor", "version": APP_VERSION}


@app.get("/")
def root() -> dict[str, Any]:
    """📋 Root endpoint con información del servicio."""
    return {
        "service": APP_TITLE,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "endpoints": {
            "predict": "/api/v1/predict-fallas",
            "health": "/health",
            "docs": "/docs"
        },
        "mcp_server": MCP_SERVER_URL,
        "llm_enabled": USE_LLM
    }
