"""In-memory Store — for tests and local dev (vaos-mvp/09). No persistence.
The durable Postgres adapter lives in postgres.py."""

from vaos.domain.action import Action
from vaos.domain.feedback import KnowledgeGap
from vaos.ports.store import Store


class InMemoryStore(Store):
    def __init__(self) -> None:
        self._events: list[tuple[str, dict]] = []
        self._gaps: list[KnowledgeGap] = []

    async def log_event(self, kind: str, payload: dict) -> None:
        self._events.append((kind, payload))

    async def record_knowledge_gap(self, query: str, context_id: str) -> None:
        self._gaps.append(KnowledgeGap(query=query, context_id=context_id))

    async def knowledge_gaps(self) -> list[KnowledgeGap]:
        return list(self._gaps)

    async def events(self) -> list[tuple[str, dict]]:
        return list(self._events)

    async def find_open_action_by_dedup_key(self, dedup_key: str) -> Action | None:
        raise NotImplementedError  # vaos-phase2-execution/03
