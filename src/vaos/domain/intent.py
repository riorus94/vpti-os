"""Intent — classification of a Query (Q2). Selects output shape + retrieval mode."""

from enum import StrEnum


class Intent(StrEnum):
    COMPLIANCE = "compliance"      # -> Compliance Answer (grounded lookup)
    RISK = "risk"                  # -> Advisory Brief
    OPPORTUNITY = "opportunity"    # -> Advisory Brief
    STRATEGY = "strategy"          # -> Advisory Brief

    @property
    def is_advisory(self) -> bool:
        return self is not Intent.COMPLIANCE
