"""InMemoryStore (vaos-mvp/09). Behavior through the Store interface:
record a Knowledge Gap -> it's in the backlog; log an event -> retrievable."""

import asyncio

from vaos.adapters.store.memory import InMemoryStore


def test_fresh_store_has_empty_knowledge_gap_backlog() -> None:
    store = InMemoryStore()
    assert asyncio.run(store.knowledge_gaps()) == []


def test_recorded_gap_appears_in_backlog() -> None:
    store = InMemoryStore()

    async def scenario() -> None:
        await store.record_knowledge_gap("HS 3824.99 wajib LS?", context_id="ctx-1")
        gaps = await store.knowledge_gaps()
        assert len(gaps) == 1
        assert gaps[0].query == "HS 3824.99 wajib LS?"
        assert gaps[0].context_id == "ctx-1"

    asyncio.run(scenario())


def test_logged_event_is_retrievable() -> None:
    store = InMemoryStore()

    async def scenario() -> None:
        await store.log_event("query", {"text": "apakah wajib VPTI?", "asker": 42})
        events = await store.events()
        assert events == [("query", {"text": "apakah wajib VPTI?", "asker": 42})]

    asyncio.run(scenario())
