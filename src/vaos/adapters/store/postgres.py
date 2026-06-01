"""PostgreSQL store — durable log + Knowledge-Gap backlog + dedup lookup (vaos-mvp/09)."""

from vaos.domain.action import Action
from vaos.domain.feedback import KnowledgeGap
from vaos.ports.store import Store


class PostgresStore(Store):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    async def log_event(self, kind: str, payload: dict) -> None:
        raise NotImplementedError("vaos-mvp/09")

    async def record_knowledge_gap(self, query: str, context_id: str) -> None:
        raise NotImplementedError("vaos-mvp/09")

    async def knowledge_gaps(self) -> list[KnowledgeGap]:
        raise NotImplementedError("vaos-mvp/09")

    async def events(self) -> list[tuple[str, dict]]:
        raise NotImplementedError("vaos-mvp/09")

    async def find_open_action_by_dedup_key(self, dedup_key: str) -> Action | None:
        raise NotImplementedError("vaos-phase2-execution/03")
