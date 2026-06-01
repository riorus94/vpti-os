"""Feedback-loop domain types (vaos-mvp/09).

A Knowledge Gap is logged when a compliance query has no Grounding (ADR-0001) —
it tells the Vault owner what to add. Collected now; acted on later (no
retrieval re-weighting yet, Q9).
"""

from pydantic import BaseModel


class KnowledgeGap(BaseModel):
    query: str
    context_id: str
