"""Orchestrator — Refusal logging (vaos-mvp/06, AC #4).

Reasoning returns a Refusal; the orchestrator owns the I/O (Q3) and logs it as a
structured Knowledge-Gap / stale-regulation signal. Without this, a refusal is
silent — the very failure mode ADR-0001 exists to prevent.
"""

import asyncio

from vaos.adapters.llm.stub import StubLLM
from vaos.adapters.store.memory import InMemoryStore
from vaos.domain.output import GapReason, Refusal
from vaos.pipeline.orchestrator import Orchestrator


def test_empty_grounding_refusal_logs_knowledge_gap_signal() -> None:
    store = InMemoryStore()
    orch = Orchestrator(llm=StubLLM(""), store=store)
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


def test_revoked_regulation_refusal_logs_stale_regulation_with_superseding_reference() -> None:
    store = InMemoryStore()
    orch = Orchestrator(llm=StubLLM(""), store=store)
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
