"""Linear ExecutionHook — real task creation + assignment (vaos-phase2-execution/03).

Assignment via a configurable Action-type -> team/project table (values owed by
the org). HITL slice: requires Linear creds + the mapping before it runs.
"""

from vaos.domain.action import Action
from vaos.ports.execution import ExecutionHook


class LinearExecutionHook(ExecutionHook):
    def __init__(self, api_key: str, team_map: dict[str, str]) -> None:
        self._api_key = api_key
        self._team_map = team_map  # ActionType -> Linear team/project id

    async def file(self, action: Action) -> str:
        raise NotImplementedError("vaos-phase2-execution/03")
