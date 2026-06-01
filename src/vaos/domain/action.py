"""Action — a unit of work produced from a Finding (Q8, ADR-0008).

Proposed, not auto-executed. Lifecycle:
    proposed -> pending_approval -> approved | rejected -> filed
An Action becomes a Linear task only after an Approver approves it (Phase 2).
"""

from enum import StrEnum

from pydantic import BaseModel


class ActionType(StrEnum):
    REMEDIATION = "remediation"            # from non_compliant
    RISK_FLAG = "risk_flag"                # from a risk
    STRATEGY_ASSIGNMENT = "strategy_assignment"  # from an opportunity


class ActionState(StrEnum):
    PROPOSED = "proposed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    FILED = "filed"


class Action(BaseModel):
    type: ActionType
    summary: str
    state: ActionState = ActionState.PROPOSED
    # Empty until the execution layer keys it (ADR-0008): the Decision Engine is
    # pure on the Finding and does not know the Context needed to derive the key.
    dedup_key: str = ""            # confirmed Context + type + regulation ref
    occurrences: int = 1           # bumped on dedup attach, never silently dropped
    linear_task_id: str | None = None
