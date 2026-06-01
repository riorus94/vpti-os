"""Intent Classifier — Query -> Intent (vaos-mvp/03, Q2).

Selects the output shape (Compliance Answer vs Advisory Brief) and retrieval/web mode.
"""

from vaos.domain.context import Context
from vaos.domain.intent import Intent
from vaos.ports.llm import LLMClient


async def classify(query: str, context: Context, llm: LLMClient) -> Intent:
    label = (await llm.complete(_SYSTEM, query)).strip().lower()
    try:
        return Intent(label)
    except ValueError:
        return Intent.COMPLIANCE  # safest fallback: grounded-or-refuse, no web


_SYSTEM = (
    "Classify the request into exactly one intent. Reply with ONLY one word: "
    "compliance | risk | opportunity | strategy."
)
