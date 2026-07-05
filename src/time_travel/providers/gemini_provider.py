"""Gemini provider adapter."""
from __future__ import annotations

import asyncio
from typing import Any

from time_travel.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        from google import genai
        self._client = genai.Client(api_key=api_key)

    @property
    def default_model(self) -> str:
        return "gemini-2.0-flash"

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        config: dict[str, Any] = {"max_output_tokens": max_tokens}
        if system:
            config["system_instruction"] = system
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=model or self.default_model,
            contents=prompt,
            config=config,  # type: ignore[arg-type]
        )
        return response.text or ""

    async def complete_parallel(
        self,
        calls: list[dict[str, str]],
    ) -> list[str]:
        tasks = [
            self.complete(
                prompt=c["prompt"],
                system=c.get("system"),
                model=c.get("model"),
                max_tokens=int(c.get("max_tokens", 4096)),
            )
            for c in calls
        ]
        return list(await asyncio.gather(*tasks))
