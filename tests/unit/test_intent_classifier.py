"""Intent Classifier (#3). Maps LLM label -> Intent. LLM behind StubLLM.
Unknown/garbage label -> COMPLIANCE (safest: grounded-or-refuse, no web)."""

import asyncio

from vaos.adapters.llm.stub import StubLLM
from vaos.domain.context import Context
from vaos.domain.intent import Intent
from vaos.modules.intent_classifier import classify


def _ctx() -> Context:
    return Context(
        client="KSO", objective="o", audience="a",
        decision_required="d", constraints="c", asker_id=1,
    )


def test_compliance_label_classifies_compliance() -> None:
    intent = asyncio.run(classify("apakah ban truk wajib VPTI?", _ctx(), StubLLM("compliance")))
    assert intent is Intent.COMPLIANCE


def test_strategy_label_classifies_strategy() -> None:
    intent = asyncio.run(classify("haruskah ekspansi komoditas?", _ctx(), StubLLM("strategy")))
    assert intent is Intent.STRATEGY


def test_risk_label_classifies_risk() -> None:
    intent = asyncio.run(classify("apa risikonya?", _ctx(), StubLLM("risk")))
    assert intent is Intent.RISK


def test_opportunity_label_classifies_opportunity() -> None:
    intent = asyncio.run(classify("ada peluang ekspansi?", _ctx(), StubLLM("opportunity")))
    assert intent is Intent.OPPORTUNITY


def test_label_is_normalized_before_mapping() -> None:
    # The classifier strips + lowercases the LLM label, so casing/whitespace from
    # the model must not leak through as an unknown -> COMPLIANCE misclassification.
    intent = asyncio.run(classify("haruskah ekspansi?", _ctx(), StubLLM("  STRATEGY\n")))
    assert intent is Intent.STRATEGY


def test_unknown_label_defaults_to_compliance() -> None:
    intent = asyncio.run(classify("???", _ctx(), StubLLM("banana nonsense")))
    assert intent is Intent.COMPLIANCE
