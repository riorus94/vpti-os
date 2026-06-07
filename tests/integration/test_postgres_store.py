"""PostgresStore durable roundtrip (#9). The adapter is dialect-agnostic SQLAlchemy
Core: verified here against SQLite (always runs, no Docker), and against real
Postgres when TEST_DATABASE_URL is set. PG-specific bits (JSONB, psycopg async) are
only exercised on the real-PG path:

    docker compose up -d db
    TEST_DATABASE_URL=postgresql+psycopg://vaos:vaos@localhost:5432/vaos \\
        pytest tests/integration/test_postgres_store.py
"""

import os
from pathlib import Path

from vaos.adapters.store.postgres import PostgresStore


def _url(tmp_path: Path) -> str:
    return os.environ.get("TEST_DATABASE_URL") or f"sqlite+aiosqlite:///{tmp_path}/store.db"


async def test_events_roundtrip_in_order(tmp_path: Path) -> None:
    store = PostgresStore(_url(tmp_path))
    await store.create_schema(reset=True)
    try:
        await store.log_event("source_unavailable", {"context_id": "ctx-1"})
        await store.log_event("knowledge_gap", {"context_id": "ctx-2", "reason": "empty_grounding"})

        assert await store.events() == [
            ("source_unavailable", {"context_id": "ctx-1"}),
            ("knowledge_gap", {"context_id": "ctx-2", "reason": "empty_grounding"}),
        ]
    finally:
        await store.dispose()


async def test_knowledge_gap_roundtrip(tmp_path: Path) -> None:
    store = PostgresStore(_url(tmp_path))
    await store.create_schema(reset=True)
    try:
        await store.record_knowledge_gap("HS 3824.99 wajib LS?", "ctx-1")

        gaps = await store.knowledge_gaps()
        assert len(gaps) == 1
        assert gaps[0].query == "HS 3824.99 wajib LS?"
        assert gaps[0].context_id == "ctx-1"
    finally:
        await store.dispose()
