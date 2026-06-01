"""Decision Engine — pure mapping Finding -> [Action] (Q8). Highest-value module.

No I/O. Reads flags only. A compliant / not_applicable / unknown Finding with no
risks or opportunities produces zero Actions. Lives in domain/ so it is unit-tested
directly, with no mocks. Dedup keys are computed by the caller (it knows the Context).
"""

from vaos.domain.action import Action, ActionType
from vaos.domain.finding import ComplianceStatus, Finding


def decide(finding: Finding, dedup_key_for: object = None) -> list[Action]:
    """Map a Finding to Actions. `dedup_key_for` is a placeholder for the
    key-derivation hook wired in by the pipeline (vaos-phase2-execution/01)."""
    raise NotImplementedError(
        "vaos-phase2-execution/01 — implement the pure Finding -> [Action] rules:\n"
        "  non_compliant -> REMEDIATION; each risk -> RISK_FLAG; "
        "each opportunity -> STRATEGY_ASSIGNMENT; else -> []"
    )


__all__ = ["decide", "Action", "ActionType", "ComplianceStatus", "Finding"]
