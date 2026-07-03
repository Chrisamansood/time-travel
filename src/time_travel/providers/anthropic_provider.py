"""Anthropic provider adapter with prompt caching support."""
from __future__ import annotations

import asyncio

from time_travel.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        from anthropic import AsyncAnthropic
        self._client = AsyncAnthropic(api_key=api_key)

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-20250514"

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        kwargs: dict = {
            "model": model or self.default_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = [
                {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
            ]
        response = await self._client.messages.create(**kwargs)
        return response.content[0].text

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
