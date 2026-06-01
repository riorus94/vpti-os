"""Decision Engine — pure Finding -> [Action] (vaos-phase2-execution/01).

Highest-value tests: table-driven over (Finding -> expected Actions). No mocks.
Cover: non_compliant -> remediation; each risk -> flag+task; each opportunity ->
strategy; compliant/not_applicable/unknown with no risks/opps -> []; combined.
"""

import pytest

# from vaos.domain.decision_engine import decide
# from vaos.domain.finding import ComplianceStatus, Finding, Risk, Opportunity


@pytest.mark.skip(reason="implement in vaos-phase2-execution/01")
def test_routine_lookup_produces_no_action() -> None:
    ...
