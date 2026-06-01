"""Decision Engine — pure mapping Finding -> [Action] (Q8). Highest-value module.

No I/O. Reads flags only. A compliant / not_applicable / unknown Finding with no
risks or opportunities produces zero Actions. Lives in domain/ so it is unit-tested
directly, with no mocks. The Action dedup key is set later by the execution layer
(it needs the Context); see ADR-0008.
"""

from vaos.domain.action import Action, ActionType
from vaos.domain.finding import ComplianceStatus, Finding


def decide(finding: Finding) -> list[Action]:
    """Map a Finding's typed flags to proposed Actions (in declaration order:
    remediation, then risk flags, then opportunity assignments)."""
    actions: list[Action] = []

    if finding.compliance_status is ComplianceStatus.NON_COMPLIANT:
        actions.append(
            Action(type=ActionType.REMEDIATION, summary="Remediate non-compliant case")
        )

    for risk in finding.risks:
        actions.append(
            Action(type=ActionType.RISK_FLAG, summary=f"Risk: {risk.description}")
        )

    for opportunity in finding.opportunities:
        actions.append(
            Action(
                type=ActionType.STRATEGY_ASSIGNMENT,
                summary=f"Opportunity: {opportunity.description}",
            )
        )

    return actions
