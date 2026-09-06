"""Tavily web-search adapter (vaos-mvp/08). Never invoked for compliance — the
Web Search Strategy routing (modules/web_search.mode_for) is the authoritative gate.

Thin HTTP over the Tavily search endpoint; returns the result snippets. The httpx
client is created lazily so constructing the adapter opens no socket.

When include_domains is configured the sweep is scoped to those domains only
(config.web_source_domains) — the same watched sources the proactive agents use.
"""

import httpx

from vaos.ports.search import WebSearch

_ENDPOINT = "https://api.tavily.com/search"
_MAX_RESULTS = 5


class TavilySearch(WebSearch):
    def __init__(
        self,
        api_key: str,
        http: httpx.AsyncClient | None = None,
        include_domains: list[str] | None = None,
    ) -> None:
        self._api_key = api_key
        self._http = http
        self._include_domains = list(include_domains or [])

    def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=20.0)
        return self._http

    async def search(self, query: str) -> list[str]:
        payload: dict[str, object] = {
            "api_key": self._api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": _MAX_RESULTS,
        }
        if self._include_domains:
            payload["include_domains"] = self._include_domains
        response = await self._client().post(_ENDPOINT, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        return [str(r["content"]) for r in results if r.get("content")]
