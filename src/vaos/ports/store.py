"""Persistence port — the durable record + self-improvement signals (vaos-mvp/09).

Persists queries, confirmed Contexts, Findings, outputs, and Knowledge-Gap /
stale-regulation events. Collects feedback signals but does not act on them yet.
Also backs Action dedup lookups (ADR-0008).
"""

from typing import Protocol

from vaos.domain.action import Action


class Store(Protocol):
    async def log_event(self, kind: str, payload: dict) -> None: ...
    async def record_knowledge_gap(self, query: str, context_id: str) -> None: ...
    async def find_open_action_by_dedup_key(self, dedup_key: str) -> Action | None: ...
