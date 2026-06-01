"""Execution flow — approval gate + dedup (vaos-phase2-execution/02 & 03, ADR-0008).

Proposed Actions enter pending_approval; only an Approver (allowlist subset) may
approve in Telegram; on approval, dedup by Action Dedup Key (attach to an open
match, never silently drop) then file via the ExecutionHook port.
"""

from vaos.domain.action import Action
from vaos.ports.execution import ExecutionHook
from vaos.ports.store import Store


def dedup_key(context_summary: str, action_type: str, regulation_ref: str) -> str:
    """ADR-0008: derive from confirmed Context (+ type + reg ref), not raw query."""
    raise NotImplementedError("vaos-phase2-execution/03")


async def approve_and_file(action: Action, approver_id: int, hook: ExecutionHook, store: Store) -> Action:
    raise NotImplementedError("vaos-phase2-execution/02 & 03")
