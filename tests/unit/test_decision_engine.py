"""Decision Engine — pure Finding -> [Action] (vaos-phase2-execution/01).

Highest-value tests: table-driven over (Finding -> expected Actions). No mocks,
no I/O. Asserts on Action types/counts/state — behavior, not implementation.
"""

from vaos.domain.action import ActionState, ActionType
from vaos.domain.decision_engine import decide
from vaos.domain.finding import ComplianceStatus, Finding, Opportunity, Risk


def test_compliant_finding_produces_no_actions() -> None:
    assert decide(Finding(compliance_status=ComplianceStatus.COMPLIANT)) == []


def test_not_applicable_and_unknown_produce_no_actions() -> None:
    # A routine lookup yields not_applicable/unknown — never a task (Q8).
    assert decide(Finding(compliance_status=ComplianceStatus.NOT_APPLICABLE)) == []
    assert decide(Finding(compliance_status=ComplianceStatus.UNKNOWN)) == []


def test_non_compliant_produces_one_remediation() -> None:
    actions = decide(Finding(compliance_status=ComplianceStatus.NON_COMPLIANT))
    assert [a.type for a in actions] == [ActionType.REMEDIATION]


def test_each_risk_becomes_a_flag() -> None:
    finding = Finding(
        risks=[Risk(description="late LS", severity="high"), Risk(description="HS mismatch", severity="med")]
    )
    actions = decide(finding)
    assert [a.type for a in actions] == [ActionType.RISK_FLAG, ActionType.RISK_FLAG]


def test_each_opportunity_becomes_a_strategy_assignment() -> None:
    finding = Finding(opportunities=[Opportunity(description="expand refrigerant gases")])
    actions = decide(finding)
    assert [a.type for a in actions] == [ActionType.STRATEGY_ASSIGNMENT]


def test_combined_finding_produces_all_applicable_actions() -> None:
    finding = Finding(
        compliance_status=ComplianceStatus.NON_COMPLIANT,
        risks=[Risk(description="late LS", severity="high")],
        opportunities=[Opportunity(description="new commodity")],
    )
    actions = decide(finding)
    assert {a.type for a in actions} == {
        ActionType.REMEDIATION,
        ActionType.RISK_FLAG,
        ActionType.STRATEGY_ASSIGNMENT,
    }
    assert len(actions) == 3


def test_combined_finding_preserves_declaration_order() -> None:
    # The docstring guarantees a fixed order: remediation, then risk flags (in
    # finding order), then opportunity assignments (in finding order). Reviewers
    # rely on this ordering, so assert the sequence, not just the set.
    finding = Finding(
        compliance_status=ComplianceStatus.NON_COMPLIANT,
        risks=[Risk(description="late LS", severity="high"),
               Risk(description="HS mismatch", severity="med")],
        opportunities=[Opportunity(description="new commodity"),
                       Opportunity(description="new lane")],
    )
    assert [a.type for a in decide(finding)] == [
        ActionType.REMEDIATION,
        ActionType.RISK_FLAG,
        ActionType.RISK_FLAG,
        ActionType.STRATEGY_ASSIGNMENT,
        ActionType.STRATEGY_ASSIGNMENT,
    ]


def test_actions_start_proposed_and_unkeyed() -> None:
    # Decision Engine is pure on the Finding; the dedup key is set later by the
    # execution layer (it needs the Context). ADR-0008.
    (action,) = decide(Finding(compliance_status=ComplianceStatus.NON_COMPLIANT))
    assert action.state is ActionState.PROPOSED
    assert action.dedup_key == ""
    assert action.summary  # non-empty, derived from the finding
