from __future__ import annotations

import os
from typing import Any, Dict, List

from openai import OpenAI


class LLMClient:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY no configurada")
        self._client = OpenAI(api_key=api_key)
        self._model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self._temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self._max_tokens = int(os.getenv("LLM_MAX_TOKENS", "800"))

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


