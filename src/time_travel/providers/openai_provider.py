"""OpenAI provider adapter."""
from __future__ import annotations

import asyncio

from time_travel.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key)

    @property
    def default_model(self) -> str:
        return "gpt-4o"

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await self._client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

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
