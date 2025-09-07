from __future__ import annotations

from typing import Any, Dict

from services.llm.client import LLMClient
from .base import BaseAgent, AgentResult


class WriterAgent(BaseAgent):
    role: str = "writer"

    def __init__(self) -> None:
        self._llm = LLMClient(agent="writer")

    def run(self, payload: Dict[str, Any]) -> AgentResult:
        # Input: {"sections": [{"title": str, "content": str}], "style": str, "rows": list[dict]}
        sections = payload.get("sections", [])
        style = payload.get("style", "breve")
        rows = payload.get("rows", [])
        body = "\n\n".join([f"## {s.get('title','')}\n{s.get('content','')}" for s in sections])
        # Si hay filas, agregarlas de forma determinística como tabla simple
        if isinstance(rows, list) and rows:
            import json as _json
            preview = _json.dumps(rows[:20], ensure_ascii=False)
            body += f"\n\n## Resultados (parcial)\n{preview}"
        system = (
            "Eres un redactor que SOLO reescribe el contenido proporcionado, en español claro y conciso. "
            "No agregues información nueva ni inventes; no incluyas contexto externo. Devuelve SOLO texto plano."
        )
        user = f"Estilo: {style}\n\nContenido:\n{body}"
        try:
            text = self._llm.complete_json(system, user)
        except Exception:
            # Fallback sin LLM
            text = body[:2000]
        content: Dict[str, Any] = {"text": text}
        trace = {"used_model": "writer"}
        return AgentResult(role=self.role, content=content, trace=trace)


