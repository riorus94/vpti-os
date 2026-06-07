"""Grounding — the retrieved evidence a Compliance Answer is built from (ADR-0001/0002).

Tagged by source so citations render correctly (verbatim pasal vs internal note).
"""

from enum import StrEnum

from pydantic import BaseModel


class GroundingSource(StrEnum):
    PASAL_ID = "pasal_id"      # official regulation text (ADR-0002)
    VAULT = "vault"            # internal FAISS-indexed note
    WEB = "web"                # web search — strategy/opportunity only (web guardrail)


class RegulationStatus(StrEnum):
    BERLAKU = "berlaku"        # in force
    DIUBAH = "diubah"          # amended
    DICABUT = "dicabut"        # revoked


class GroundingChunk(BaseModel):
    source: GroundingSource
    reference: str             # pasal cite, or internal note id
    text: str                  # verbatim (never machine-translated — ADR-0004)
    score: float
    status: RegulationStatus | None = None  # set only for PASAL_ID
    superseded_by: str | None = None         # superseding cite when diubah/dicabut (ADR-0002)


class Grounding(BaseModel):
    """Ordered evidence. Empty => compliance must refuse (ADR-0001)."""

    chunks: list[GroundingChunk] = []
    regulation_unavailable: bool = False
    """The regulation source could not be reached (ADR-0002). Distinct from
    empty: compliance must refuse with a source-unavailable signal, and the
    internal leg must never be substituted for the missing regulation text."""

    @property
    def is_empty(self) -> bool:
        return len(self.chunks) == 0
