"""Web Search Strategy — pure routing + Tavily (vaos-mvp/08).

mode(query type) -> internal (default) | web (fallback) | hybrid (strategy).
Hard guardrail: compliance / regulation / internal-process ALWAYS resolve to
internal and never reach the web — authoritative over any other signal.
"""

from enum import StrEnum

from vaos.domain.intent import Intent


class SearchMode(StrEnum):
    INTERNAL = "internal"
    WEB = "web"
    HYBRID = "hybrid"


def mode_for(intent: Intent) -> SearchMode:
    """Pure routing. Compliance is always INTERNAL (guardrail)."""
    if intent in (Intent.STRATEGY, Intent.OPPORTUNITY):
        return SearchMode.HYBRID
    return SearchMode.INTERNAL
