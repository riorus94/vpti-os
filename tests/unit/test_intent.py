"""Intent domain type (Q2). The is_advisory property selects the output shape:
COMPLIANCE -> Compliance Answer (grounded lookup); everything else -> Advisory Brief.
"""

from vaos.domain.intent import Intent


def test_compliance_is_not_advisory() -> None:
    assert Intent.COMPLIANCE.is_advisory is False


def test_risk_opportunity_strategy_are_advisory() -> None:
    assert Intent.RISK.is_advisory is True
    assert Intent.OPPORTUNITY.is_advisory is True
    assert Intent.STRATEGY.is_advisory is True
