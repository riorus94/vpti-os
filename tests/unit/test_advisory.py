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
