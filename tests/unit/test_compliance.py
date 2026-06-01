"""Compliance reasoning — grounded-or-refuse (vaos-mvp/06).

Asserts on the RETURNED TYPE, not on a Store side-effect (Q3): grounding present
-> ComplianceAnswer with citations; empty grounding -> Refusal(EMPTY_GROUNDING);
dicabut regulation -> Refusal(REVOKED_REGULATION, superseding_reference set).
LLM behind a StubLLM; no Store needed.
"""

import pytest


@pytest.mark.skip(reason="implement in vaos-mvp/06")
def test_empty_grounding_returns_refusal() -> None:
    ...
