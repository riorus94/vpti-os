"""Web search port. Adapter: Tavily. Used only for strategy/opportunity —
never compliance (the Web Search Strategy guardrail is authoritative)."""

from typing import Protocol


class WebSearch(Protocol):
    async def search(self, query: str) -> list[str]: ...
