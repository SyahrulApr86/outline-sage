"""Klien vLLM (OpenAI-compatible) untuk generasi jawaban streaming (TSD-002 bagian 6, LLM Client)."""
from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import json as jsonlib


class LLMClient:
    def __init__(self, base_url: str, model_name: str, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout = timeout

    async def stream_chat(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        payload = {"model": self._model_name, "messages": messages, "stream": True}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream("POST", f"{self._base_url}/chat/completions", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data = line[len("data: ") :]
                    if data.strip() == "[DONE]":
                        break
                    chunk = jsonlib.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
