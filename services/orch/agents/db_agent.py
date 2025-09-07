from __future__ import annotations

from typing import Any, Dict, List
import os
import requests

from .base import BaseAgent, AgentResult
from services.llm.client import LLMClient
from services.db.mysql import MySQLClient


class DBAgent(BaseAgent):
    role: str = "db"

    def __init__(self) -> None:
        self._mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:7070")
        self._llm = LLMClient(agent="db")
        self._mysql: MySQLClient | None = None
        self._backend: str = "stub"
        self._init_error: str | None = None
        try:
            self._mysql = MySQLClient()
            self._backend = "mysql"
        except Exception:
            # Guardar el error de inicialización para diagnóstico
            import traceback
            self._mysql = None
            self._backend = "stub"
            self._init_error = traceback.format_exc(limit=1)

    def run(self, payload: Dict[str, Any]) -> AgentResult:
        # Input: {"sql": str, "params": list}
        used_schema = None
        if "question" in payload:
            # NL2SQL con LLM y esquema lógico simple
            question = payload.get("question", "")
            # Construir hint del esquema: preferir introspección real, sino fallback env
            schema = None
            if self._mysql is not None:
                try:
                    introspected = self._mysql.introspect_schema()
                    schema = MySQLClient.format_schema_for_prompt(introspected)
                    used_schema = schema
                except Exception:
                    schema = None
            if not schema:
                schema = os.getenv("DB_SCHEMA_HINT", "inventario(sku,stock,bodega); visitas(ticket_id,equipo_model,issue)")
                used_schema = schema
            system = (
                "Eres un generador de SQL para MySQL. Devuelve SOLO un SELECT válido, sin texto extra ni fences. "
                "Usa EXCLUSIVAMENTE tablas y columnas del esquema provisto. Si un campo no existe, elimina ese filtro o sustitúyelo por uno disponible. "
                "Incluye LIMIT 100 si no hay límite. No uses comentarios ni CTEs."
            )
            user = f"Esquema: {schema}\nPregunta: {question}\nResponde solo con un SELECT."
            try:
                sql_raw = self._llm.complete_json(system, user)
            except Exception:
                sql_raw = "select sku, stock, bodega from inventario where stock < 5"
            sql_clean = self._clean_sql(sql_raw)
            payload = {"sql": sql_clean}

        body = {"sql": payload.get("sql", ""), "params": payload.get("params")}

        rows: List[Dict[str, Any]] = []
        exec_error: str | None = None
        if self._mysql is not None:
            try:
                sql_to_run = self._ensure_limit(body["sql"])
                rows = self._mysql.query(sql_to_run, body.get("params"))
            except Exception as e:
                rows = []
                exec_error = str(e)
        else:
            # Fallback a tool demo en MCP
            res = requests.post(f"{self._mcp_url}/tools/db_query", json=body, timeout=10)
            data = res.json()
            rows = data.get("rows", [])

        content: Dict[str, Any] = {
            "rows": rows,
            "count": len(rows),
            "sql": body.get("sql", ""),
            "schema": used_schema,
            "backend": self._backend,
        }
        if self._init_error and self._backend == "stub":
            content["connect_error"] = self._init_error
        if exec_error:
            content["error"] = exec_error
        trace = {"db_query": body.get("sql", "")[:240]}
        return AgentResult(role=self.role, content=content, trace=trace)

    @staticmethod
    def _clean_sql(sql_text: str) -> str:
        # Remover fences ``` y etiquetas de lenguaje
        txt = str(sql_text or "").strip()
        if "```" in txt:
            try:
                start = txt.index("```") + 3
                rest = txt[start:]
                if rest.startswith("sql"):
                    rest = rest[3:]
                end = rest.find("```")
                if end != -1:
                    txt = rest[:end]
                else:
                    txt = rest
            except Exception:
                pass
        # Tomar primera sentencia SELECT
        lower = txt.lower()
        sel_idx = lower.find("select")
        if sel_idx != -1:
            stmt = txt[sel_idx:]
        else:
            stmt = txt
        # Cortar en el primer ';' si existe
        semi = stmt.find(";")
        if semi != -1:
            stmt = stmt[:semi]
        return stmt.strip()

    @staticmethod
    def _ensure_limit(sql_text: str) -> str:
        low = (sql_text or "").lower()
        if " limit " in low:
            return sql_text
        return sql_text.rstrip(" ;") + " LIMIT 100"


