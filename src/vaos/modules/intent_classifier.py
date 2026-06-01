"""Intent Classifier — Query -> Intent (vaos-mvp/03, Q2).

Selects the output shape (Compliance Answer vs Advisory Brief) and retrieval/web mode.
"""

from vaos.domain.context import Context
from vaos.domain.intent import Intent
from vaos.ports.llm import LLMClient


async def classify(query: str, context: Context, llm: LLMClient) -> Intent:
    raise NotImplementedError("vaos-mvp/03")
