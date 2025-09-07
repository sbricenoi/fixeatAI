from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AgentResult:
    role: str
    content: Dict[str, Any]
    trace: Dict[str, Any]


class BaseAgent:
    role: str = "agent"

    def run(self, payload: Dict[str, Any]) -> AgentResult:  # pragma: no cover - stub
        raise NotImplementedError


