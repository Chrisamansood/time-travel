"""Tavily web search adapter."""
from __future__ import annotations

from time_travel.search.base import SearchResult, WebSearch


class TavilySearch(WebSearch):
    def __init__(self, api_key: str) -> None:
        from tavily import AsyncTavilyClient
        self._client = AsyncTavilyClient(api_key=api_key)

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            response = await self._client.search(query=query, max_results=max_results)
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                return []
            raise
        results = []
        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    score=item.get("score", 0.0),
                )
            )
        return results
