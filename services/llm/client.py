from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import json

from openai import OpenAI


class LLMClient:
    def __init__(self, agent: Optional[str] = None) -> None:
        """Cliente LLM con soporte de configuración por agente.

        - Si se define `LLM_AGENTS` (JSON en env), busca la sección del agente por nombre
          y permite configurar `model`, `base_url`, `temperature`, `max_tokens`, `api_key`.
        - Fallback a variables globales (`OPENAI_API_KEY`, `LLM_MODEL`, etc.).
        - Para servidores OpenAI‑compatibles locales, si no hay API key, usa una dummy.
        """

        # Cargar configuración de agentes desde env
        agents_cfg: Dict[str, Any] = {}
        raw_agents = os.getenv("LLM_AGENTS")
        if raw_agents:
            try:
                agents_cfg = json.loads(raw_agents)
            except Exception:
                agents_cfg = {}

        cfg: Dict[str, Any] = agents_cfg.get(agent or "", {}) if isinstance(agents_cfg, dict) else {}

        model = cfg.get("model") or os.getenv("LLM_MODEL", "gpt-4o-mini")
        temperature = float(str(cfg.get("temperature", os.getenv("LLM_TEMPERATURE", "0.1"))))
        max_tokens = int(str(cfg.get("max_tokens", os.getenv("LLM_MAX_TOKENS", "800"))))
        base_url = cfg.get("base_url")

        # API key: preferir la del agente, luego global, luego dummy local
        api_key = cfg.get("api_key") or os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_LOCAL_API_KEY") or "sk-local"
        if not api_key:
            raise RuntimeError("No se encontró API key para el cliente LLM")

        if base_url:
            self._client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self._client = OpenAI(api_key=api_key)

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or "{}"


