"""Stub search — returns a canned result for CI tests and offline dry runs."""
from __future__ import annotations

from time_travel.search.base import SearchResult, WebSearch

_CANNED_RESULT = SearchResult(
    title="Stub search result",
    url="https://example.com/stub",
    snippet="This is a stub search result for testing purposes.",
    score=0.5,
)


class StubSearch(WebSearch):
    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        return [_CANNED_RESULT]
