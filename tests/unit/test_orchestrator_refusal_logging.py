"""Orchestrator — Refusal logging (vaos-mvp/06, AC #4).

Reasoning returns a Refusal; the orchestrator owns the I/O (Q3) and logs it as a
structured Knowledge-Gap / stale-regulation signal. Without this, a refusal is
silent — the very failure mode ADR-0001 exists to prevent.
"""

import asyncio

from vaos.adapters.llm.stub import StubLLM
from vaos.adapters.store.memory import InMemoryStore
from vaos.domain.grounding import Grounding
from vaos.domain.output import GapReason, Refusal
from vaos.modules.retrieval.router import RetrievalRouter
from vaos.pipeline.orchestrator import Orchestrator


class _EmptySource:
    async def query(self, text: str) -> Grounding:
        return Grounding(chunks=[])


def _router() -> RetrievalRouter:
    # log_refusal never touches the router; a trivial one keeps the constructor honest.
    return RetrievalRouter(regs=_EmptySource(), vault=_EmptySource())


def test_empty_grounding_refusal_logs_knowledge_gap_signal() -> None:
    store = InMemoryStore()
    orch = Orchestrator(llm=StubLLM(""), store=store, router=_router())
    refusal = Refusal(reason=GapReason.EMPTY_GROUNDING, message="…")

    asyncio.run(orch.log_refusal(refusal, query="HS 3824.99 wajib LS?", context_id="ctx-1"))

    gaps = asyncio.run(store.knowledge_gaps())
    assert len(gaps) == 1
    assert gaps[0].query == "HS 3824.99 wajib LS?"
    events = asyncio.run(store.events())
    assert len(events) == 1
    kind, payload = events[0]
    assert kind == "knowledge_gap"
    assert payload["reason"] == GapReason.EMPTY_GROUNDING.value
    assert payload["context_id"] == "ctx-1"


def test_source_unavailable_refusal_is_not_recorded_as_knowledge_gap() -> None:
    # ADR-0002: 'regulation source down' is an ops failure, not missing content.
    # It must NOT pollute the Knowledge-Gap backlog (the vault owner can't fix it),
    # but it IS logged as a distinct event for ops/alerting.
    store = InMemoryStore()
    orch = Orchestrator(llm=StubLLM(""), store=store, router=_router())
    refusal = Refusal(reason=GapReason.SOURCE_UNAVAILABLE, message="…")

    asyncio.run(orch.log_refusal(refusal, query="wajib LS?", context_id="ctx-3"))

    assert asyncio.run(store.knowledge_gaps()) == []
    events = asyncio.run(store.events())
    assert len(events) == 1
    kind, _ = events[0]
    assert kind == "source_unavailable"


def test_revoked_regulation_refusal_logs_stale_regulation_with_superseding_reference() -> None:
    store = InMemoryStore()
    orch = Orchestrator(llm=StubLLM(""), store=store, router=_router())
    refusal = Refusal(
        reason=GapReason.REVOKED_REGULATION,
        message="…",
        superseding_reference="Permendag Y Pasal 5",
    )

    asyncio.run(orch.log_refusal(refusal, query="wajib LS?", context_id="ctx-2"))

    # Knowledge-Gap backlog is recorded for every refusal (so reviewers see the gap).
    assert len(asyncio.run(store.knowledge_gaps())) == 1
    events = asyncio.run(store.events())
    assert len(events) == 1
    kind, payload = events[0]
    # Stale-regulation is a distinct signal kind from a pure knowledge gap so that
    # downstream consumers can route it differently (e.g. trigger re-grounding).
    assert kind == "stale_regulation"
    assert payload["reason"] == GapReason.REVOKED_REGULATION.value
    assert payload["superseding_reference"] == "Permendag Y Pasal 5"
