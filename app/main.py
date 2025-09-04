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
from pydantic import BaseModel
from services.rules.soporte import generar_pasos_soporte
from services.predictor.heuristic import infer_from_hits, suggest_parts_and_tools
from services.orch.rag import predict_with_llm
from services.validation.formulario import validar_formulario as validar_formulario_payload


APP_TITLE = "FixeatAI Microservicio IA"
APP_VERSION = "0.1.0"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:7070")
TRACE_HEADER = os.getenv("X_TRACE_ID_HEADER", "X-Trace-Id")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"


app = FastAPI(title=APP_TITLE, version=APP_VERSION)


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
    """Retorna diagnóstico y repuestos sugeridos (mock).

    Integra con el servidor MCP para recuperar contexto de KB (si está disponible).
    """

    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/kb_search",
            json={"query": req.descripcion_problema, "top_k": 3},
            timeout=5,
        )
        hits = response.json().get("hits", [])
    except Exception:
        hits = []

    if USE_LLM:
        data = predict_with_llm(MCP_SERVER_URL, req.descripcion_problema, req.equipo, top_k=5)
    else:
        # Heurística basada en hits de la KB (MVP no-LLM)
        preds = infer_from_hits(hits)
        sugg = suggest_parts_and_tools(preds)
        data = {
            "fallas_probables": preds,
            **sugg,
            "fuentes": [h.get("doc_id") for h in hits],
        }
    log_event(logging.INFO, x_trace_id, "predict_fallas", num_hits=len(hits))
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
    """Devuelve pasos recomendados de diagnóstico/reparación (mock)."""

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
    """Valida coherencia y sugiere correcciones (mock)."""

    data = validar_formulario_payload(req.model_dump())
    log_event(logging.INFO, x_trace_id, "validar_formulario", es_valido=data.get("es_valido"))
    return build_response(
        data=data, message="Validación completada", code="OK", trace_id=x_trace_id
    )


@app.get("/health")
def health() -> dict[str, Any]:
    """Endpoint de salud mínimo."""

    return {"status": "ok"}


