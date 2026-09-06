"""TavilySearch adapter (#8, ADR / web guardrail). Mocked transport — no network.
Pins the request shape (api_key + query) and result extraction. Never invoked for
compliance: the Web Search Strategy routing (mode_for) is the authoritative gate."""

import httpx

from vaos.adapters.search.tavily import TavilySearch


def _search(handler: object) -> TavilySearch:
    transport = httpx.MockTransport(handler)  # type: ignore[arg-type]
    return TavilySearch(api_key="tvly-key", http=httpx.AsyncClient(transport=transport))


async def test_search_posts_query_and_returns_result_snippets() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        import json
        body = json.loads(request.content)
        assert body["api_key"] == "tvly-key"
        assert body["query"] == "tren impor baja 2026"
        return httpx.Response(200, json={"results": [
            {"title": "A", "url": "https://a", "content": "Baja naik 5%."},
            {"title": "B", "url": "https://b", "content": "Permintaan stabil."},
            {"title": "C", "url": "https://c"},  # no content -> skipped
        ]})

    out = await _search(handler).search("tren impor baja 2026")
    assert out == ["Baja naik 5%.", "Permintaan stabil."]


async def test_empty_results_yield_empty_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    assert await _search(handler).search("apa pun") == []


async def test_include_domains_scopes_the_sweep() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        import json
        body = json.loads(request.content)
        assert body["include_domains"] == ["anindya.biz", "*.anindya.biz"]
        return httpx.Response(200, json={"results": [{"content": "X"}]})

    transport = httpx.MockTransport(handler)  # type: ignore[arg-type]
    adapter = TavilySearch(
        api_key="tvly-key",
        http=httpx.AsyncClient(transport=transport),
        include_domains=["anindya.biz", "*.anindya.biz"],
    )
    assert await adapter.search("apa pun") == ["X"]


async def test_no_domains_leaves_the_sweep_unscoped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        import json
        assert "include_domains" not in json.loads(request.content)
        return httpx.Response(200, json={"results": []})

    assert await _search(handler).search("apa pun") == []
