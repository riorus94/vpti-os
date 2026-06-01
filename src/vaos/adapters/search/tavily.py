"""Tavily web-search adapter (vaos-mvp/08). Never invoked for compliance."""

from vaos.ports.search import WebSearch


class TavilySearch(WebSearch):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def search(self, query: str) -> list[str]:
        raise NotImplementedError("vaos-mvp/08")
