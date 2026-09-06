"""Market-Intel agent (ADR-0009). Scheduled trend sweep for opportunity briefs.

Pure over an injected WebSearch port (Tavily in prod, fake in tests). Never used
for compliance — strategy/opportunity only (ADR / web guardrail).

The sweep is scoped by the injected port (Tavily carries the configured watched
domains); `sources` records that same list on each Insight so a brief states which
domains it was drawn from instead of leaving the provenance implicit.
"""

from pydantic import BaseModel

from vaos.ports.search import WebSearch


class Insight(BaseModel):
    topic: str
    summary: str
    sources: list[str] = []   # watched domains the sweep was scoped to ([] = open web)


_NO_RESULTS = "Tidak ada hasil pencarian untuk topik ini."


async def scan(
    topics: list[str], search: WebSearch, sources: list[str] | None = None
) -> list[Insight]:
    """Sweep each topic via the injected WebSearch and return one Insight per topic,
    its summary distilled from the result snippets (placeholder when none). `sources`
    is the watched-domain list the sweep was scoped to, carried onto every Insight."""
    watched = list(sources or [])
    insights: list[Insight] = []
    for topic in topics:
        results = await search.search(topic)
        summary = " ".join(results) if results else _NO_RESULTS
        insights.append(Insight(topic=topic, summary=summary, sources=watched))
    return insights
