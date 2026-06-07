"""Agent-layer unit tests (ADR-0009). Each agent's core is testable with injected
fakes — no scheduler, no network. Stubs until implemented per agent issue."""

import pytest

from vaos.adapters.store.memory import InMemoryStore
from vaos.agents.knowledge_gap_resolver import digest


@pytest.mark.skip(reason="implement in vaos-agents/regulation-watch")
def test_find_stale_returns_only_revoked_or_amended() -> None:
    # given cited refs + a fake status checker, returns the diubah/dicabut ones.
    ...


async def test_digest_ranks_gaps_by_frequency() -> None:
    store = InMemoryStore()
    for _ in range(3):
        await store.record_knowledge_gap("wajib LS untuk ban truk?", "ctx")
    await store.record_knowledge_gap("HS 3824.99 wajib LS?", "ctx")
    for _ in range(2):
        await store.record_knowledge_gap("izin impor besi baja?", "ctx")

    items = await digest(store)

    assert [(i.query, i.count) for i in items] == [
        ("wajib LS untuk ban truk?", 3),
        ("izin impor besi baja?", 2),
        ("HS 3824.99 wajib LS?", 1),
    ]


async def test_digest_of_empty_backlog_is_empty() -> None:
    assert await digest(InMemoryStore()) == []


@pytest.mark.skip(reason="implement in vaos-agents/market-intel")
def test_scan_distills_one_insight_per_topic() -> None:
    # fake WebSearch -> one Insight per topic.
    ...
