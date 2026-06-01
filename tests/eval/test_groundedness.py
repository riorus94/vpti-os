"""AI evaluation with Ragas (groundedness / relevance / correctness).

Runs against a golden set of (query, expected grounding, expected answer). Most
important metric here is groundedness — a Compliance Answer must not assert beyond
its Grounding (ADR-0001). Kept separate from unit/integration; may be slow / costed.
"""

import pytest


@pytest.mark.skip(reason="set up Ragas golden set after vaos-mvp/06")
def test_compliance_answers_are_grounded() -> None:
    ...
