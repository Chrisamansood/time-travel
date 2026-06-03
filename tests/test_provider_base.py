"""Tests for the LLMProvider abstract base class.

Tests verify the interface contract using a minimal concrete subclass.
No real LLM calls happen here.
"""
from __future__ import annotations

import asyncio

import pytest

# ── minimal concrete implementation for tests ──────────────────────────────────

class ConcreteProvider:
    """Inline concrete provider — zero dependencies on Plan B adapters."""

    @property
    def default_model(self) -> str:
        return "test-model-v1"

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        return f"reply:{prompt[:20]}"

    async def complete_parallel(self, calls: list[dict]) -> list[str]:
        return [await self.complete(c["prompt"]) for c in calls]


def get_abc():
    from time_travel.providers.base import LLMProvider
    return LLMProvider


# ── tests ───────────────────────────────────────────────────────────────────────

def test_cannot_instantiate_abc_directly():
    LLMProvider = get_abc()
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        LLMProvider()


def test_concrete_subclass_satisfies_interface():
    LLMProvider = get_abc()

    class GoodProvider(LLMProvider):
        @property
        def default_model(self) -> str:
            return "good-model"

        async def complete(self, prompt, system=None, model=None, max_tokens=4096) -> str:
            return "ok"

        async def complete_parallel(self, calls: list[dict]) -> list[str]:
            return ["ok" for _ in calls]

    p = GoodProvider()
    assert p.default_model == "good-model"


def test_concrete_subclass_missing_complete_raises():
    LLMProvider = get_abc()

    with pytest.raises(TypeError):
        class BadProvider(LLMProvider):
            @property
            def default_model(self) -> str:
                return "m"
            # missing complete and complete_parallel

        BadProvider()


def test_complete_returns_string():
    p = ConcreteProvider()
    result = asyncio.run(p.complete("hello world"))
    assert isinstance(result, str)
    assert "reply:" in result


def test_complete_parallel_returns_list_of_strings():
    p = ConcreteProvider()
    calls = [
        {"prompt": "prompt one", "system": None},
        {"prompt": "prompt two", "system": None},
        {"prompt": "prompt three", "system": None},
    ]
    results = asyncio.run(p.complete_parallel(calls))
    assert len(results) == 3
    assert all(isinstance(r, str) for r in results)


def test_complete_parallel_preserves_order():
    """Results must map 1:1 to calls by position."""
    class IndexProvider:
        @property
        def default_model(self) -> str:
            return "m"
        async def complete(self, prompt, **_) -> str:
            return prompt
        async def complete_parallel(self, calls: list[dict]) -> list[str]:
            return [await self.complete(c["prompt"]) for c in calls]

    p = IndexProvider()
    calls = [{"prompt": f"call-{i}"} for i in range(5)]
    results = asyncio.run(p.complete_parallel(calls))
    assert results == [f"call-{i}" for i in range(5)]
