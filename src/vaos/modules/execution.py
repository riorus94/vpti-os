"""Execution flow — approval gate + dedup (vaos-phase2-execution/02 & 03, ADR-0008).

Proposed Actions enter pending_approval; only an Approver (allowlist subset) may
approve in Telegram; on approval, dedup by Action Dedup Key (attach to an open
match, never silently drop) then file via the ExecutionHook port.
"""

from vaos.domain.action import Action, ActionState, ActionType
from vaos.domain.context import Context
from vaos.ports.execution import ExecutionHook
from vaos.ports.store import Store


def dedup_key(context: Context, action_type: ActionType, regulation_ref: str) -> str:
    """ADR-0008: derive from confirmed Context (+ type + reg ref), not raw query."""
    parts = [context.client, context.objective, context.decision_required,
             action_type.value, regulation_ref]
    return "|".join(p.strip().lower() for p in parts)


async def approve(action: Action, approver_id: int, approvers: set[int], hook: ExecutionHook) -> Action:
    """Only an Approver may approve (ADR-0008). On approval, file via the hook and
    return the FILED action carrying the external task id."""
    if approver_id not in approvers:
        raise PermissionError("only an Approver may approve an Action (ADR-0008)")
    task_id = await hook.file(action)
    return action.model_copy(update={"state": ActionState.FILED, "linear_task_id": task_id})
