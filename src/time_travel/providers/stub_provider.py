"""Stub provider — returns canned strings for CI tests. No API key needed."""
from __future__ import annotations

from time_travel.providers.base import LLMProvider

_CANNED: dict[str, str] = {
    "user_pov": (
        '{"thought_getting": "A fast product", "would_forgive": "Rough edges", '
        '"untrustworthy": "Data loss", "predictable_complaints": "Slow onboarding"}'
    ),
    "default": "This is a stub response for testing purposes.",
}


class StubProvider(LLMProvider):
    def __init__(self, canned: dict[str, str] | None = None) -> None:
        self._canned = canned or _CANNED

    @property
    def default_model(self) -> str:
        return "stub-1.0"

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        prompt_lower = prompt.lower()
        for key, value in self._canned.items():
            if key in prompt_lower:
                return value
        return self._canned.get("default", "stub response")

    async def complete_parallel(
        self,
        calls: list[dict[str, str]],
    ) -> list[str]:
        results = []
        for c in calls:
            result = await self.complete(
                prompt=c["prompt"],
                system=c.get("system"),
                model=c.get("model"),
                max_tokens=int(c.get("max_tokens", 4096)),
            )
            results.append(result)
        return results
