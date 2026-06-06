"""Retrieval router — fans out to the regulation leg and the internal leg, merges,
and tags each chunk by GroundingSource (vaos-mvp/05, ADR-0002).

Deep module: callers cross one interface (retrieve) and the router hides the
fan-out, the merge, the source tagging, and the load-bearing degradation rule —
if the regulation leg is unavailable it is reported as such and the internal leg
is NEVER substituted for it. Both legs are ports, so the router is unit-testable
with in-memory fakes (no FAISS, no pasal-id HTTP).
"""

from vaos.domain.context import Context
from vaos.domain.grounding import Grounding
from vaos.ports.retrieval import (
    InternalSource,
    RegulationSource,
    RegulationSourceUnavailable,
)


class RetrievalRouter:
    def __init__(self, regs: RegulationSource, vault: InternalSource) -> None:
        self._regs = regs
        self._vault = vault

    async def retrieve(self, query: str, context: Context) -> Grounding:
        internal = await self._vault.query(query)
        try:
            regulation = await self._regs.query(query)
        except RegulationSourceUnavailable:
            # ADR-0002: report unavailable; never substitute the internal leg.
            return Grounding(chunks=internal.chunks, regulation_unavailable=True)
        return Grounding(chunks=regulation.chunks + internal.chunks)
