"""Orchestrator — the fixed request pipeline.

    receive -> build/confirm Context -> classify Intent -> retrieve grounding
            -> compliance answer (grounded-or-refuse)  [Intent.COMPLIANCE]
            -> advisory brief + Finding -> Decision Engine -> propose Actions  [advisory]
            -> log everything

Enforces the boundary invariants: no output without a confirmed Context; no
Advisory Brief without a named Thinking Model; compliance is grounded-or-refuse.
Depends only on ports — never on a concrete adapter.

Owns the I/O that reasoning deliberately does NOT (Q3): when compliance.answer
returns a Refusal, the orchestrator calls store.record_knowledge_gap(...). A
Refusal the orchestrator fails to handle is a visible bug, not a silent one.
"""

from vaos.domain.output import GapReason, Refusal
from vaos.ports.llm import LLMClient
from vaos.ports.store import Store


class Orchestrator:
    def __init__(self, llm: LLMClient, store: Store) -> None:
        self._llm = llm
        self._store = store

    async def handle(self, query: str, asker_id: int) -> str:
        raise NotImplementedError("wired incrementally across vaos-mvp/01..09")

    async def log_refusal(self, refusal: Refusal, query: str, context_id: str) -> None:
        # A Refusal the orchestrator fails to log would be a silent gap — the exact
        # failure mode ADR-0001 exists to prevent. Two writes by design: the
        # Knowledge-Gap backlog feeds reviewers; the event log feeds analytics.
        await self._store.record_knowledge_gap(query, context_id)
        kind = "stale_regulation" if refusal.reason is GapReason.REVOKED_REGULATION else "knowledge_gap"
        await self._store.log_event(
            kind,
            {
                "reason": refusal.reason.value,
                "query": query,
                "context_id": context_id,
                "superseding_reference": refusal.superseding_reference,
            },
        )
