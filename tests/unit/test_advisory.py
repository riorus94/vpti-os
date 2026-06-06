"""Advisory Brief reasoning (vaos-mvp/07).

brief() returns an AdvisoryBrief naming a thinking_model and carrying a Finding.
LLM picks a model from the registry; unregistered/garbage -> per-intent default.
LLM behind StubLLM (canned JSON)."""

import asyncio
import json

from vaos.adapters.llm.stub import StubLLM
from vaos.domain.context import Context
from vaos.domain.intent import Intent
from vaos.domain.grounding import Grounding
from vaos.domain.output import AdvisoryBrief
from vaos.modules.reasoning.advisory import brief
from vaos.modules.reasoning.thinking_models import DEFAULT_BY_INTENT

_SECTIONS = {k: "x" for k in
             ("ringkasan_eksekutif", "konteks", "analisis", "risiko", "peluang", "rekomendasi")}


def _payload(model: str, **finding: object) -> str:
    f = {"compliance_status": "not_applicable", "risks": [], "opportunities": []}
    f.update(finding)
    return json.dumps({"thinking_model": model, "sections": _SECTIONS, "finding": f})


def _ctx() -> Context:
    return Context(client="KSO", objective="o", audience="a",
                   decision_required="d", constraints="c", asker_id=1)


def test_brief_uses_registered_model_from_llm() -> None:
    res = asyncio.run(brief("haruskah ekspansi?", _ctx(), Intent.RISK,
                            Grounding(chunks=[]), StubLLM(_payload("pre_mortem"))))
    assert isinstance(res, AdvisoryBrief)
    assert res.thinking_model == "pre_mortem"


def test_unregistered_model_falls_back_to_intent_default() -> None:
    res = asyncio.run(brief("q", _ctx(), Intent.RISK,
                            Grounding(chunks=[]), StubLLM(_payload("banana_nonsense"))))
    assert res.thinking_model == DEFAULT_BY_INTENT[Intent.RISK]


def test_malformed_llm_output_raises_format_error() -> None:
    import pytest

    from vaos.modules.llm_json import LLMFormatError
    with pytest.raises(LLMFormatError):
        asyncio.run(brief("q", _ctx(), Intent.RISK, Grounding(chunks=[]), StubLLM("not json")))


def test_brief_emits_finding_from_llm() -> None:
    payload = _payload(
        "systems_thinking",
        compliance_status="non_compliant",
        risks=[{"description": "late LS", "severity": "high"}],
    )
    res = asyncio.run(brief("q", _ctx(), Intent.STRATEGY, Grounding(chunks=[]), StubLLM(payload)))
    assert res.finding.compliance_status.value == "non_compliant"
    assert len(res.finding.risks) == 1
