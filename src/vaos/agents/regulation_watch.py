"""Regulation-Watch agent (ADR-0009). Catches revoked/amended regulations.

Core is pure given an injected status-checker: list cited references -> the ones
now dicabut/diubah (with superseding ref). No scheduler, no network in the logic.
"""

from collections.abc import Awaitable, Callable

from pydantic import BaseModel

from vaos.domain.grounding import RegulationStatus

StatusChecker = Callable[[str], Awaitable[tuple[RegulationStatus, str | None]]]


class StaleRegulation(BaseModel):
    reference: str
    status: RegulationStatus
    superseded_by: str | None = None


async def find_stale(cited_refs: list[str], status_of: StatusChecker) -> list[StaleRegulation]:
    """Return cited regulations whose status is now diubah/dicabut."""
    raise NotImplementedError("vaos-agents/regulation-watch")
