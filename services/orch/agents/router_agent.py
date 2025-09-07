from __future__ import annotations

from typing import Any, Dict, List

from services.llm.client import LLMClient
from .base import BaseAgent, AgentResult


class RouterAgent(BaseAgent):
    role: str = "router"

    def __init__(self) -> None:
        self._llm = LLMClient(agent="router")

    def run(self, payload: Dict[str, Any]) -> AgentResult:
        # Input esperado: {"query": str, "context": { opcional }}
        query = payload.get("query", "")

        system = (
            "Eres un enrutador de consultas. Devuelve SOLO JSON con el siguiente esquema: "
            "{\n"
            "  \"intent\": \"kb|db|mixed\",\n"
            "  \"reasons\": [\"string\"],\n"
            "  \"next\": [\"kb_search\", \"db_query\"]\n"
            "}. Reglas: 1) No inventes, 2) Si no estás seguro usa 'mixed'."
        )
        user = f"Consulta: {query}"
        try:
            raw = self._llm.complete_json(system, user)
        except Exception:
            raw = '{"intent":"kb","reasons":["llm_error_or_disabled"],"next":["kb_search"]}'
        content: Dict[str, Any] = {"raw": raw}
        trace = {"used_model": "router"}
        return AgentResult(role=self.role, content=content, trace=trace)


