from __future__ import annotations

from typing import Any, Dict, List

import os
import requests

from .base import BaseAgent, AgentResult
from services.orch.rag import build_context_from_hits


class KBAgent(BaseAgent):
    role: str = "kb"

    def __init__(self) -> None:
        self._mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:7070")

    def run(self, payload: Dict[str, Any]) -> AgentResult:
        # Input: {"query": str, "top_k": int, "where": dict}
        query = payload.get("query", "")
        top_k = int(payload.get("top_k", 5))
        where = payload.get("where")
        body: Dict[str, Any] = {"query": query, "top_k": top_k}
        if isinstance(where, dict) and where:
            body["where"] = where
        res = requests.post(f"{self._mcp_url}/tools/kb_search", json=body, timeout=10)
        hits = res.json().get("hits", [])
        context = build_context_from_hits(hits)
        content: Dict[str, Any] = {
            "hits": hits,
            "context": context,
        }
        trace = {"kb_hits": len(hits)}
        return AgentResult(role=self.role, content=content, trace=trace)


