"""Aplicación FastAPI del microservicio IA.

Expone endpoints mock que siguen el estándar de respuesta con
traceId, code, message y data. Integra (demo) con un servidor MCP
local para realizar búsquedas en la KB mediante la tool kb_search.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Optional
import json
import logging

import requests
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.rules.soporte import generar_pasos_soporte
from services.predictor.heuristic import infer_from_hits, suggest_parts_and_tools
from services.orch.rag import predict_with_llm
from services.validation.formulario import validar_formulario as validar_formulario_payload
from services.orch.validate import validate_with_llm
from services.orch.ops_analyst import analyze_ops, analyze_ops_from_kb
from services.orch.agents import RouterAgent, KBAgent, DBAgent, WriterAgent
from services.kb.relevance_scorer import rank_documents_by_relevance
from services.orch.llm_reranker import rerank_with_llm


APP_TITLE = "FixeatAI Microservicio IA"
APP_VERSION = "0.1.0"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:7070")
TRACE_HEADER = os.getenv("X_TRACE_ID_HEADER", "X-Trace-Id")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"


app = FastAPI(title=APP_TITLE, version=APP_VERSION)

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
    payload = {"traceId": trace_id, "event": event, **kwargs}
    logging.log(level, json.dumps(payload, ensure_ascii=False))


class PredictRequest(BaseModel):
    cliente: dict
    equipo: dict
    descripcion_problema: str
    tecnico: dict


@app.post("/api/v1/predict-fallas")
def predict_fallas(
    req: PredictRequest,
    x_trace_id: Optional[str] = Header(default=None, alias=TRACE_HEADER),
) -> dict[str, Any]:
    """Retorna diagnóstico y repuestos sugeridos con contextos ampliados.

    Integra con el servidor MCP para recuperar contexto de KB con información extendida.
    Usa kb_search_extended para obtener contextos de 2000+ caracteres y metadata enriquecida.
    """

    if USE_LLM:
        data = predict_with_llm(MCP_SERVER_URL, req.descripcion_problema, req.equipo, top_k=10)
        
        # Usar los hits que ya recuperó predict_with_llm (más confiables que una búsqueda separada)
        hits = data.pop("_raw_hits", [])
        
        # GARANTIZAR que SIEMPRE haya contextos en la respuesta
        # Si predict_with_llm no los generó o no hay hits, hacer búsqueda directa
        if not hits or "contextos" not in data or not data.get("contextos"):
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

        # APLICAR LLM RE-RANKER: El LLM analiza los documentos y determina cuál es MÁS relevante
        # Este es el flujo que el usuario solicitó:
        # 1. KB Search retorna candidatos (15-20 docs)
        # 2. LLM analiza TODOS los documentos con contexto semántico completo
        # 3. LLM determina relevancia REAL de cada documento (0-100)
        # 4. LLM explica POR QUÉ cada documento es relevante
        # 5. Retornamos ordenado por análisis del LLM
        if hits:
            # Extraer marca y modelo para contexto
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
                top_k=10  # Retornar top 10 después del análisis del LLM
            )
            
            # Construir contextos con información del LLM re-ranker
            data["contextos"] = [
                {
                    "fuente": hit["doc_id"],
                    "score": hit["score"],  # Score original de búsqueda
                    "relevance_score": hit.get("llm_relevance_score", 0),  # Score del LLM (0-100)
                    "confidence_label": hit.get("llm_confidence", "Media"),  # Del LLM
                    "llm_explanation": hit.get("llm_explanation", ""),  # Por qué es relevante (del LLM)
                    "contexto": hit.get("context", hit.get("snippet", ""))[:1500],
                    "document_url": hit.get("document_url"),
                    "metadata": {
                        "page": hit.get("metadata", {}).get("page"),
                        "source": hit.get("metadata", {}).get("source"),
                        "brand": hit.get("metadata", {}).get("brand"),
                        "model": hit.get("metadata", {}).get("model"),
                    },
                }
                for hit in ranked_hits  # Ya viene ordenado del LLM
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
            
            # Actualizar también las fuentes para que coincidan con los contextos
            if "fuentes" not in data or not data["fuentes"]:
                data["fuentes"] = [hit["doc_id"] for hit in ranked_hits[:10]]
        else:
            # Fallback: lista vacía pero con estructura válida
            print(f"⚠️  ADVERTENCIA: No se encontraron documentos para '{req.descripcion_problema}'")
            data["contextos"] = []
            if "fuentes" not in data:
                data["fuentes"] = []
    else:
        # Modo sin LLM: hacer búsqueda directa
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
        
        # Heurística basada en hits de la KB (MVP no-LLM)
        preds = infer_from_hits(hits, req.descripcion_problema)
        data = {
            "fallas_probables": preds,
            "fuentes": [h.get("doc_id") for h in hits],
            "feedback_coherencia": "Respuesta basada en análisis heurístico",
            "contextos": [
                {
                    "fuente": hit["doc_id"],
                    "score": hit["score"],
                    "contexto": hit.get("context", hit.get("snippet", ""))[:1500],
                    "document_url": hit.get("document_url"),  # URL navegable (NUEVO en Fase 2)
                    "metadata": {
                        "page": hit.get("metadata", {}).get("page"),
                        "source": hit.get("metadata", {}).get("source"),
                    }
                }
                for hit in hits[:10]
            ]
        }
    
    log_event(logging.INFO, x_trace_id, "predict_fallas", num_hits=len(hits), llm_used=USE_LLM)
    return build_response(data=data, message="Predicción generada", code="OK", trace_id=x_trace_id)


class SoporteRequest(BaseModel):
    cliente: dict
    equipo: dict
    descripcion_problema: str


@app.post("/api/v1/soporte-tecnico")
def soporte_tecnico(
    req: SoporteRequest,
    x_trace_id: Optional[str] = Header(default=None, alias=TRACE_HEADER),
) -> dict[str, Any]:
    """Devuelve pasos recomendados de diagnóstico/reparación.

    - Si USE_LLM=true: usa RAG+LLM (mismo orquestador que predict-fallas) y retorna pasos + fuentes + signals
    - Si USE_LLM=false: usa reglas heurísticas locales
    """

    if USE_LLM:
        data_llm = predict_with_llm(MCP_SERVER_URL, req.descripcion_problema, req.equipo, top_k=10)
        
        # Extraer hits para construir contextos
        hits = data_llm.pop("_raw_hits", [])
        
        # GARANTIZAR que siempre haya contextos
        if not hits:
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
            except Exception as e:
                print(f"❌ Error obteniendo contextos para soporte: {e}")
                hits = []
        
        # Aplicar LLM Re-Ranker para soporte técnico también
        contextos = []
        if hits:
            # Extraer marca y modelo
            marca = req.equipo.get("marca") or req.equipo.get("brand") if req.equipo else None
            modelo = req.equipo.get("modelo") or req.equipo.get("model") if req.equipo else None
            
            # LLM re-ranking
            ranked_hits = rerank_with_llm(
                query=req.descripcion_problema,
                candidates=hits,
                marca=marca,
                modelo=modelo,
                top_k=10
            )
            
            contextos = [
                {
                    "fuente": hit["doc_id"],
                    "score": hit["score"],
                    "relevance_score": hit.get("llm_relevance_score", 0),
                    "confidence_label": hit.get("llm_confidence", "Media"),
                    "llm_explanation": hit.get("llm_explanation", ""),
                    "contexto": hit.get("context", hit.get("snippet", ""))[:1500],
                    "document_url": hit.get("document_url"),
                    "metadata": {
                        "page": hit.get("metadata", {}).get("page"),
                        "source": hit.get("metadata", {}).get("source"),
                        "brand": hit.get("metadata", {}).get("brand"),
                        "model": hit.get("metadata", {}).get("model"),
                    },
                }
                for hit in ranked_hits
            ]
        
        pasos = data_llm.get("pasos", [])
        payload = {
            "pasos": pasos,
            "fuentes": data_llm.get("fuentes", []),
            "signals": data_llm.get("signals", {}),
            "contextos": contextos  # SIEMPRE incluir contextos
        }
        log_event(logging.INFO, x_trace_id, "soporte_tecnico_llm", pasos=len(pasos))
        return build_response(
            data=payload, message="Secuencia generada (LLM)", code="OK", trace_id=x_trace_id
        )

    pasos = generar_pasos_soporte(req.equipo, req.descripcion_problema)
    log_event(logging.INFO, x_trace_id, "soporte_tecnico", pasos=len(pasos))
    return build_response(
        data={"pasos": pasos}, message="Secuencia generada", code="OK", trace_id=x_trace_id
    )


class QARequest(BaseModel):
    pregunta: str
    equipo: dict | None = None


@app.post("/api/v1/qa")
def qa(
    req: QARequest,
    x_trace_id: Optional[str] = Header(default=None, alias=TRACE_HEADER),
) -> dict[str, Any]:
    if not USE_LLM:
        return build_response(
            data={"respuesta": "LLM deshabilitado (USE_LLM=false)", "fuentes": []},
            message="LLM deshabilitado",
            code="OK",
            trace_id=x_trace_id,
        )
    data = predict_with_llm(MCP_SERVER_URL, req.pregunta, req.equipo or {}, top_k=5)
    return build_response(data=data, message="QA generado", code="OK", trace_id=x_trace_id)


class ValidarRequest(BaseModel):
    cliente: dict
    equipo: dict
    descripcion_problema: str
    campos_formulario: dict


@app.post("/api/v1/validar-formulario")
def validar_formulario(
    req: ValidarRequest,
    x_trace_id: Optional[str] = Header(default=None, alias=TRACE_HEADER),
) -> dict[str, Any]:
    """Valida coherencia y sugiere correcciones.

    - Si USE_LLM=true: valida y mejora redacción con LLM (agrega `descripcion_mejorada`).
    - Si USE_LLM=false: usa reglas locales.
    """

    if USE_LLM:
        data = validate_with_llm(req.model_dump())
    else:
        data = validar_formulario_payload(req.model_dump())
    log_event(logging.INFO, x_trace_id, "validar_formulario", es_valido=data.get("es_valido"))
    return build_response(
        data=data, message="Validación completada", code="OK", trace_id=x_trace_id
    )


@app.get("/health")
def health() -> dict[str, Any]:
    """Endpoint de salud mínimo."""

    return {"status": "ok"}


class OpsAnaliticaRequest(BaseModel):
    # Modo 1 (recomendado): prompt + filtros para recuperar de KB
    prompt: str | None = None
    filtros: dict | None = None  # se mapea a where en kb_search
    top_k: int | None = 20

    # Modo 2 (alternativo): datos crudos si se desea forzar análisis local
    visitas: list[dict] | None = None
    inventario: list[dict] | None = None
    equipos: list[dict] | None = None
    tickets: list[dict] | None = None


@app.post("/api/v1/ops-analitica")
def ops_analitica(
    req: OpsAnaliticaRequest,
    x_trace_id: Optional[str] = Header(default=None, alias=TRACE_HEADER),
) -> dict[str, Any]:
    """Analista de operaciones: produce alertas, accionables y métricas.

    - Si USE_LLM=true: usa LLM con señales heurísticas.
    - Si USE_LLM=false: responde con heurística mínima indicando low_evidence.
    """

    payload = req.model_dump()
    if USE_LLM and (req.prompt or req.filtros):
        data = analyze_ops_from_kb(MCP_SERVER_URL, req.prompt or "analiza operaciones", req.filtros, top_k=req.top_k or 20)
    elif USE_LLM:
        data = analyze_ops(payload)
    else:
        data = {
            "alertas": [],
            "accionables": [],
            "metricas": {},
            "recomendaciones": ["Habilitar LLM (USE_LLM=true) o enviar prompt para análisis desde KB"],
            "signals": {"low_evidence": True},
        }
    log_event(logging.INFO, x_trace_id, "ops_analitica", visitas=len(payload.get("visitas") or []))
    return build_response(data=data, message="Análisis de operaciones", code="OK", trace_id=x_trace_id)


class OrquestarRequest(BaseModel):
    query: str
    filtros: dict | None = None
    style: str | None = "breve"
    sql: str | None = None


@app.post("/api/v1/orquestar")
def orquestar(req: OrquestarRequest, x_trace_id: Optional[str] = Header(default=None, alias=TRACE_HEADER)) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    router = RouterAgent()
    kb = KBAgent()
    db = DBAgent()
    writer = WriterAgent()

    try:
        route = router.run({"query": req.query})
    except Exception as e:
        route = None
        errors.append({"agent": "router", "error": str(e)})
    intent_raw = (route.content.get("raw", "") if route else "")
    # Determinar intención estructurada si es posible
    intent_val: str | None = None
    try:
        parsed = json.loads(intent_raw) if intent_raw else {}
        if isinstance(parsed, dict):
            intent_val = str(parsed.get("intent")) if parsed.get("intent") else None
    except Exception:
        intent_val = None

    # Decidir uso de agentes según intención
    need_db = (intent_val in ("db", "mixed")) or (intent_val is None and ("db" in intent_raw or "mixed" in intent_raw))
    need_kb = (intent_val in ("kb", "mixed")) or (intent_val is None and ("kb" in intent_raw or "mixed" in intent_raw))

    kb_where = None
    if req.filtros and isinstance(req.filtros, dict) and req.filtros:
        kb_where = req.filtros

    kb_res = None
    if need_kb:
        try:
            kb_res = kb.run({"query": req.query, "top_k": 8, "where": kb_where})
        except Exception as e:
            kb_res = None
            errors.append({"agent": "kb", "error": str(e)})

    db_rows: list[dict] = []
    db_sql: str | None = None
    db_backend: str | None = None
    db_error: str | None = None
    db_connect_error: str | None = None
    if need_db:
        try:
            # Si viene SQL explícito, ejecutarlo; si no, NL2SQL
            if req.sql:
                db_res = db.run({"sql": req.sql})
            else:
                db_res = db.run({"question": req.query})
            db_rows = db_res.content.get("rows", [])
            db_sql = db_res.content.get("sql")
            db_backend = db_res.content.get("backend")
            db_error = db_res.content.get("error")
            db_connect_error = db_res.content.get("connect_error")
        except Exception as e:
            errors.append({"agent": "db", "error": str(e)})

    sections = []
    if need_kb and kb_res:
        sections.append({"title": "Contexto KB", "content": (kb_res.content.get("context", "") if kb_res else "")[:3000]})
    if need_db and db_rows:
        sections.append({"title": "Datos DB", "content": json.dumps(db_rows, ensure_ascii=False)[:2000]})
    sections.append({"title": "Consulta", "content": req.query})
    try:
        out = writer.run({"sections": sections, "style": req.style or "breve", "rows": db_rows})
        respuesta = out.content.get("text", "")
    except Exception as e:
        errors.append({"agent": "writer", "error": str(e)})
        respuesta = (sections[0]["content"] + "\n\n" + sections[2]["content"])[:2000]

    data = {
        "router": (route.content if route else {}),
        "kb": {"hits": len(kb_res.content.get("hits", []))} if kb_res else {"hits": 0},
        "db": {"rows": len(db_rows), "sql": db_sql, "backend": db_backend, "error": db_error, "connect_error": db_connect_error},
        "respuesta": respuesta,
        "errors": errors,
    }
    return build_response(data=data, message="Orquestación completada", code=("OK" if not errors else "PARTIAL"), trace_id=x_trace_id)


