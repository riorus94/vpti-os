"""Stub ExecutionHook — logs 'would file' (vaos-phase2-execution/02)."""

from vaos.domain.action import Action
from vaos.ports.execution import ExecutionHook


class StubExecutionHook(ExecutionHook):
    async def file(self, action: Action) -> str:
        return f"stub:{action.type}"  # no external write
