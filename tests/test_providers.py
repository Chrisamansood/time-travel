"""Contract tests for provider adapters — all use mocked clients, no live API calls."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from time_travel.providers.base import LLMProvider
from time_travel.providers.stub_provider import StubProvider


# ── stub provider tests ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_stub_complete_returns_string():
    provider = StubProvider()
    result = await provider.complete("Tell me about user_pov")
    assert isinstance(result, str)
    assert "thought_getting" in result


@pytest.mark.asyncio
async def test_stub_complete_default_response():
    provider = StubProvider()
    result = await provider.complete("something random")
    assert result == "This is a stub response for testing purposes."


@pytest.mark.asyncio
async def test_stub_complete_parallel():
    provider = StubProvider()
    results = await provider.complete_parallel([
        {"prompt": "Tell me about user_pov"},
        {"prompt": "random prompt"},
    ])
    assert len(results) == 2
    assert "thought_getting" in results[0]
    assert results[1] == "This is a stub response for testing purposes."


@pytest.mark.asyncio
async def test_stub_custom_canned():
    provider = StubProvider(canned={"hello": "world", "default": "fallback"})
    assert await provider.complete("say hello") == "world"
    assert await provider.complete("unknown") == "fallback"


def test_stub_default_model():
    provider = StubProvider()
    assert provider.default_model == "stub-1.0"


def test_stub_is_llm_provider():
    assert isinstance(StubProvider(), LLMProvider)


# ── anthropic provider tests (mocked) ────────────────────────────────────────

@pytest.mark.asyncio
async def test_anthropic_complete_sends_prompt_caching():
    from time_travel.providers.anthropic_provider import AnthropicProvider

    provider = object.__new__(AnthropicProvider)
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="test response")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    provider._client = mock_client

    result = await provider.complete("test prompt", system="system prompt")
    assert result == "test response"

    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}


@pytest.mark.asyncio
async def test_anthropic_complete_no_system():
    from time_travel.providers.anthropic_provider import AnthropicProvider

    provider = object.__new__(AnthropicProvider)
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="response")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    provider._client = mock_client

    await provider.complete("test prompt")
    call_kwargs = mock_client.messages.create.call_args[1]
    assert "system" not in call_kwargs


@pytest.mark.asyncio
async def test_anthropic_parallel_uses_gather():
    from time_travel.providers.anthropic_provider import AnthropicProvider

    provider = object.__new__(AnthropicProvider)
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="r")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    provider._client = mock_client

    results = await provider.complete_parallel([
        {"prompt": "a"},
        {"prompt": "b"},
        {"prompt": "c"},
    ])
    assert len(results) == 3
    assert mock_client.messages.create.call_count == 3


def test_anthropic_default_model():
    from time_travel.providers.anthropic_provider import AnthropicProvider
    provider = object.__new__(AnthropicProvider)
    assert "claude" in provider.default_model


# ── openai provider tests (mocked) ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_openai_complete_with_system():
    from time_travel.providers.openai_provider import OpenAIProvider

    provider = object.__new__(OpenAIProvider)
    mock_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "openai response"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    provider._client = mock_client

    result = await provider.complete("prompt", system="sys")
    assert result == "openai response"

    call_kwargs = mock_client.chat.completions.create.call_args[1]
    assert call_kwargs["messages"][0]["role"] == "system"
    assert call_kwargs["messages"][1]["role"] == "user"


@pytest.mark.asyncio
async def test_openai_parallel():
    from time_travel.providers.openai_provider import OpenAIProvider

    provider = object.__new__(OpenAIProvider)
    mock_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "r"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    provider._client = mock_client

    results = await provider.complete_parallel([{"prompt": "a"}, {"prompt": "b"}])
    assert len(results) == 2


# ── gemini provider tests (mocked) ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_gemini_complete():
    from time_travel.providers.gemini_provider import GeminiProvider

    provider = object.__new__(GeminiProvider)
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "gemini response"
    mock_client.models.generate_content = MagicMock(return_value=mock_response)
    provider._client = mock_client

    result = await provider.complete("prompt", system="sys")
    assert result == "gemini response"


def test_gemini_default_model():
    from time_travel.providers.gemini_provider import GeminiProvider
    provider = object.__new__(GeminiProvider)
    assert "gemini" in provider.default_model
