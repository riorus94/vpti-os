"""PostgreSQL store — durable log + Knowledge-Gap backlog + dedup lookup (vaos-mvp/09).

Dialect-agnostic SQLAlchemy Core over an async engine, so the production
postgresql+psycopg URL and a SQLite test URL run the same code. find_open_action_
by_dedup_key is the Action dedup lookup and lands with vaos-phase2-execution/03.
"""

from sqlalchemy import JSON, Column, Integer, MetaData, String, Table, insert, select
from sqlalchemy.ext.asyncio import create_async_engine

from vaos.domain.action import Action
from vaos.domain.feedback import KnowledgeGap
from vaos.ports.store import Store

_metadata = MetaData()

_events = Table(
    "events",
    _metadata,
    Column("id", Integer, primary_key=True),
    Column("kind", String, nullable=False),
    Column("payload", JSON, nullable=False),
)

_gaps = Table(
    "knowledge_gaps",
    _metadata,
    Column("id", Integer, primary_key=True),
    Column("query", String, nullable=False),
    Column("context_id", String, nullable=False),
)


class PostgresStore(Store):
    def __init__(self, database_url: str) -> None:
        self._engine = create_async_engine(database_url)

    async def create_schema(self, reset: bool = False) -> None:
        async with self._engine.begin() as conn:
            if reset:
                await conn.run_sync(_metadata.drop_all)
            await conn.run_sync(_metadata.create_all)

    async def log_event(self, kind: str, payload: dict[str, object]) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(insert(_events).values(kind=kind, payload=payload))

    async def record_knowledge_gap(self, query: str, context_id: str) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(insert(_gaps).values(query=query, context_id=context_id))

    async def knowledge_gaps(self) -> list[KnowledgeGap]:
        async with self._engine.connect() as conn:
            rows = await conn.execute(
                select(_gaps.c.query, _gaps.c.context_id).order_by(_gaps.c.id)
            )
            return [KnowledgeGap(query=r.query, context_id=r.context_id) for r in rows]

    async def events(self) -> list[tuple[str, dict[str, object]]]:
        async with self._engine.connect() as conn:
            rows = await conn.execute(
                select(_events.c.kind, _events.c.payload).order_by(_events.c.id)
            )
            return [(r.kind, r.payload) for r in rows]

    async def find_open_action_by_dedup_key(self, dedup_key: str) -> Action | None:
        raise NotImplementedError  # vaos-phase2-execution/03

    async def dispose(self) -> None:
        await self._engine.dispose()
