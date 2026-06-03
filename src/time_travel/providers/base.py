"""Abstract base class for LLM provider adapters.

All provider adapters (anthropic_provider, openai_provider, gemini_provider)
implement this interface. The orchestrator calls only these two methods —
it has no knowledge of which provider is active.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface for an LLM provider adapter.

    Usage:
        provider = AnthropicProvider(api_key=os.environ["ANTHROPIC_API_KEY"])
        result = await provider.complete("What's the risk here?")
        results = await provider.complete_parallel([
            {"prompt": "persona A prompt"},
            {"prompt": "persona B prompt"},
        ])
    """

    @property
    @abstractmethod
    def default_model(self) -> str:
        """The model identifier used when --model is not specified."""
        ...

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        """Run one completion and return the response text.

        Args:
            prompt: The user-turn content.
            system: Optional system prompt.
            model: Model override. Uses self.default_model if None.
            max_tokens: Maximum tokens in the response.

        Returns:
            The model's response as a plain string.
        """
        ...

    @abstractmethod
    async def complete_parallel(
        self,
        calls: list[dict[str, str]],
    ) -> list[str]:
        """Run multiple completions in parallel and return results in order.

        Args:
            calls: List of dicts, each with:
                   "prompt" (required), "system" (optional), "model" (optional),
                   "max_tokens" (optional).

        Returns:
            List of response strings, same length and order as `calls`.
        """
        ...
