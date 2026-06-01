"""Execution port — turns an approved Action into an external task (ADR-0008).

Adapters: adapters/execution/linear.py (real), .../stub.py (skeleton + tests).
Only invoked after an Approver approves; the assignment team comes from a
configurable Action-type -> team table.
"""

from typing import Protocol

from vaos.domain.action import Action


class ExecutionHook(Protocol):
    async def file(self, action: Action) -> str:
        """Create the external task; return its id. Caller guarantees the Action
        is approved and de-duplicated."""
        ...
