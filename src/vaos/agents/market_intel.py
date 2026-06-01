"""Market-Intel agent (ADR-0009). Scheduled trend sweep for opportunity briefs.

Pure over an injected WebSearch port (Tavily in prod, fake in tests). Never used
for compliance — strategy/opportunity only (ADR / web guardrail).
"""

from pydantic import BaseModel

from vaos.ports.search import WebSearch


class Insight(BaseModel):
    topic: str
    summary: str


async def scan(topics: list[str], search: WebSearch) -> list[Insight]:
    """Sweep each topic via WebSearch and return distilled insights."""
    raise NotImplementedError("vaos-agents/market-intel")
