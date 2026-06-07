"""Interim empty retrieval sources for the composition root.

They satisfy the RegulationSource / InternalSource ports and return no grounding,
so the assembled pipeline runs end-to-end today and (correctly) refuses compliance
answers for lack of grounding. The real adapters replace them: regulation =
PasalIdClient (vaos-mvp/05), internal = FaissVault (vaos-mvp/04).
"""

from vaos.domain.grounding import Grounding


class EmptyRegulationSource:
    async def query(self, text: str) -> Grounding:
        return Grounding(chunks=[])


class EmptyInternalSource:
    async def query(self, text: str) -> Grounding:
        return Grounding(chunks=[])
