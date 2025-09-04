# syntax=docker/dockerfile:1.7
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copiar metadatos y dependencias
COPY pyproject.toml /app/

# Instalar deps (modo no editable dentro de imagen)
RUN pip install --upgrade pip && pip install .

# Copiar código
COPY app /app/app
COPY services /app/services
COPY mcp /app/mcp

EXPOSE 8000 7000

# Entrypoint dinámico: usar ENV ROLE=api|mcp
ENV ROLE=api \
    MCP_SERVER_URL=http://localhost:7000 \
    X_TRACE_ID_HEADER=X-Trace-Id

CMD ["/bin/sh", "-c", "if [ \"$ROLE\" = \"mcp\" ]; then uvicorn mcp.server_demo:app --host 0.0.0.0 --port 7000; else uvicorn app.main:app --host 0.0.0.0 --port 8000; fi"]


