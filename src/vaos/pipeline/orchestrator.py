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

from vaos.ports.llm import LLMClient
from vaos.ports.store import Store


class Orchestrator:
    def __init__(self, llm: LLMClient, store: Store) -> None:
        self._llm = llm
        self._store = store

    async def handle(self, query: str, asker_id: int) -> str:
        raise NotImplementedError("wired incrementally across vaos-mvp/01..09")
