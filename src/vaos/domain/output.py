"""Output shapes as first-class domain types (Q2/Q4) — so the code speaks the
glossary (CONTEXT.md) instead of returning bare strings/tuples.

Reasoning modules return these and perform no I/O; the orchestrator inspects the
result and logs a Knowledge Gap on a Refusal (Q3).
"""

from enum import StrEnum

from pydantic import BaseModel

from vaos.domain.finding import Finding
from vaos.domain.grounding import GroundingChunk


class GapReason(StrEnum):
    EMPTY_GROUNDING = "empty_grounding"        # nothing retrieved (ADR-0001)
    REVOKED_REGULATION = "revoked_regulation"  # dicabut/diubah (ADR-0002)


class ComplianceAnswer(BaseModel):
    """Compact, grounded, source-cited answer. Citations are verbatim pasal text."""

    text: str
    citations: list[GroundingChunk]


class Refusal(BaseModel):
    """Compliance refusal — never an ungrounded answer (ADR-0001). Triggers a
    Knowledge-Gap log in the orchestrator."""

    reason: GapReason
    message: str
    superseding_reference: str | None = None  # set when REVOKED_REGULATION


class SixSections(BaseModel):
    """Localized Indonesian headers (ADR-0004). Fixed by the PRD — encoding them
    as a type makes section drift a type error."""

    ringkasan_eksekutif: str
    konteks: str
    analisis: str
    risiko: str
    peluang: str
    rekomendasi: str


class AdvisoryPayload(BaseModel):
    """The raw shape an LLM returns for an Advisory Brief, before the model name
    is checked against the registry. `thinking_model` is a free str on purpose:
    an unregistered name is a domain fallback (-> per-intent default), NOT a parse
    failure. Promoted to AdvisoryBrief by advisory.brief — mirrors
    InferredContext -> Context."""

    sections: SixSections
    thinking_model: str
    finding: Finding


class AdvisoryBrief(BaseModel):
    sections: SixSections
    thinking_model: str   # named in the output by construction (Q5)
    finding: Finding


# A compliance request resolves to exactly one of these.
ComplianceResult = ComplianceAnswer | Refusal
