"""Compliance Answer — grounded-or-refuse (vaos-mvp/06, ADR-0001/0002/0004).

Returns a typed ComplianceResult and performs NO I/O beyond the LLM port (Q3):
- grounding present, regulation in force  -> ComplianceAnswer (verbatim Indonesian citations)
- grounding empty                         -> Refusal(EMPTY_GROUNDING)
- regulation dicabut/diubah               -> Refusal(REVOKED_REGULATION, superseding_reference=...)

The orchestrator inspects the result and logs the Knowledge Gap on a Refusal —
this module never touches the Store. No thinking model is used for compliance.
"""

from vaos.domain.context import Context
from vaos.domain.grounding import Grounding, RegulationStatus
from vaos.domain.output import ComplianceResult, GapReason, Refusal
from vaos.ports.llm import LLMClient

_REVOKED = {RegulationStatus.DICABUT, RegulationStatus.DIUBAH}


async def answer(query: str, context: Context, grounding: Grounding, llm: LLMClient) -> ComplianceResult:
    if grounding.is_empty:
        # No grounding -> refuse, never answer from model memory (ADR-0001).
        return Refusal(
            reason=GapReason.EMPTY_GROUNDING,
            message="Tidak ditemukan di basis pengetahuan. Diteruskan ke peninjau.",
        )
    if any(c.status in _REVOKED for c in grounding.chunks):
        # Regulation revoked/amended -> do not assert it as current (ADR-0002).
        return Refusal(
            reason=GapReason.REVOKED_REGULATION,
            message="Regulasi terkait sudah dicabut/diubah. Diteruskan ke peninjau.",
        )
    raise NotImplementedError("vaos-mvp/06 — grounded answer next")
