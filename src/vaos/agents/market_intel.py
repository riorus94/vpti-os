"""Market-Intel agent (ADR-0009). Scheduled trend sweep for opportunity briefs.

Pure over an injected WebSearch port (Tavily in prod, fake in tests). Never used
for compliance — strategy/opportunity only (ADR / web guardrail).
"""

from pydantic import BaseModel

from vaos.ports.search import WebSearch


class Insight(BaseModel):
    topic: str
    summary: str


_NO_RESULTS = "Tidak ada hasil pencarian untuk topik ini."


async def scan(topics: list[str], search: WebSearch) -> list[Insight]:
    """Sweep each topic via the injected WebSearch and return one Insight per topic,
    its summary distilled from the result snippets (placeholder when none)."""
    insights: list[Insight] = []
    for topic in topics:
        results = await search.search(topic)
        summary = " ".join(results) if results else _NO_RESULTS
        insights.append(Insight(topic=topic, summary=summary))
    return insights
