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
from vaos.domain.output import ComplianceAnswer, ComplianceResult, GapReason, Refusal
from vaos.ports.llm import LLMClient

_REVOKED = {RegulationStatus.DICABUT, RegulationStatus.DIUBAH}
_SYSTEM = (
    "Answer the compliance question ONLY from the provided grounding. Cite pasal "
    "text verbatim in Bahasa Indonesia. Do not use outside knowledge."
)


async def answer(query: str, context: Context, grounding: Grounding, llm: LLMClient) -> ComplianceResult:
    if grounding.is_empty:
        # No grounding -> refuse, never answer from model memory (ADR-0001).
        return Refusal(
            reason=GapReason.EMPTY_GROUNDING,
            message="Tidak ditemukan di basis pengetahuan. Diteruskan ke peninjau.",
        )
    stale = next((c for c in grounding.chunks if c.status in _REVOKED), None)
    if stale is not None:
        # Regulation revoked/amended -> do not assert it as current; name the
        # superseding reference instead so the reviewer can re-ground (ADR-0002).
        superseding = stale.superseded_by
        message = "Regulasi terkait sudah dicabut/diubah. Diteruskan ke peninjau."
        if superseding:
            message = (
                f"Regulasi terkait ({stale.reference}) sudah dicabut/diubah, "
                f"digantikan oleh {superseding}. Diteruskan ke peninjau."
            )
        return Refusal(
            reason=GapReason.REVOKED_REGULATION,
            message=message,
            superseding_reference=superseding,
        )
    prompt = f"Pertanyaan: {query}\n\nGrounding:\n" + "\n".join(
        f"[{c.reference}] {c.text}" for c in grounding.chunks
    )
    text = await llm.complete(_SYSTEM, prompt)
    return ComplianceAnswer(text=text, citations=grounding.chunks)
