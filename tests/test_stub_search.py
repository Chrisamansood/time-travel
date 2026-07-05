"""Unit tests for StubSearch — no network, deterministic canned results."""
from __future__ import annotations

import pytest

from time_travel.search.base import SearchResult, WebSearch
from time_travel.search.stub_search import StubSearch


def test_stub_search_is_a_websearch():
    assert isinstance(StubSearch(), WebSearch)


@pytest.mark.asyncio
async def test_stub_search_returns_a_search_result():
    results = await StubSearch().search("anything")
    assert len(results) == 1
    assert isinstance(results[0], SearchResult)


@pytest.mark.asyncio
async def test_stub_search_is_deterministic_regardless_of_query():
    search = StubSearch()
    assert await search.search("query one") == await search.search("query two")
