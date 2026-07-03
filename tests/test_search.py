"""Contract tests for the search module — Tavily adapter with mocked client."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from time_travel.search.base import SearchResult, WebSearch
from time_travel.search.tavily import TavilySearch


def test_search_result_dataclass():
    r = SearchResult(title="Test", url="https://example.com", snippet="A test result")
    assert r.title == "Test"
    assert r.score == 0.0


def test_web_search_is_abstract():
    with pytest.raises(TypeError):
        WebSearch()


def _make_searcher(mock_client: AsyncMock) -> TavilySearch:
    searcher = object.__new__(TavilySearch)
    searcher._client = mock_client
    return searcher


@pytest.fixture
def mock_tavily_response():
    return {
        "results": [
            {
                "title": "SaaS failure post-mortem",
                "url": "https://example.com/saas-failure",
                "content": "A startup failed after 90 days due to billing issues.",
                "score": 0.95,
            },
            {
                "title": "Stripe integration guide",
                "url": "https://example.com/stripe-guide",
                "content": "Common pitfalls when integrating Stripe payments.",
                "score": 0.87,
            },
        ]
    }


@pytest.mark.asyncio
async def test_tavily_search_returns_search_results(mock_tavily_response):
    mock_client = AsyncMock()
    mock_client.search = AsyncMock(return_value=mock_tavily_response)
    searcher = _make_searcher(mock_client)

    results = await searcher.search("SaaS MVP failure")

    assert len(results) == 2
    assert all(isinstance(r, SearchResult) for r in results)
    assert results[0].title == "SaaS failure post-mortem"
    assert results[0].score == 0.95
    assert results[1].url == "https://example.com/stripe-guide"


@pytest.mark.asyncio
async def test_tavily_search_correct_query_construction(mock_tavily_response):
    mock_client = AsyncMock()
    mock_client.search = AsyncMock(return_value=mock_tavily_response)
    searcher = _make_searcher(mock_client)

    await searcher.search("test query", max_results=3)
    mock_client.search.assert_called_once_with(query="test query", max_results=3)


@pytest.mark.asyncio
async def test_tavily_search_handles_quota_exceeded():
    mock_client = AsyncMock()
    mock_client.search = AsyncMock(side_effect=Exception("API quota exceeded"))
    searcher = _make_searcher(mock_client)

    results = await searcher.search("test query")
    assert results == []


@pytest.mark.asyncio
async def test_tavily_search_propagates_non_quota_errors():
    mock_client = AsyncMock()
    mock_client.search = AsyncMock(side_effect=ConnectionError("Network down"))
    searcher = _make_searcher(mock_client)

    with pytest.raises(ConnectionError):
        await searcher.search("test query")


@pytest.mark.asyncio
async def test_tavily_search_empty_results():
    mock_client = AsyncMock()
    mock_client.search = AsyncMock(return_value={"results": []})
    searcher = _make_searcher(mock_client)

    results = await searcher.search("obscure query")
    assert results == []
