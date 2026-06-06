"""Context Builder (#2). Pure validation/promotion tested directly; infer tested
behind a StubLLM. The 'never output without Context' invariant lives here."""

import asyncio
import json

import pytest

from vaos.adapters.llm.stub import StubLLM
from vaos.domain.context import Context, InferredContext
from vaos.modules.context_builder import confirm, infer


def _inferred(**over: str) -> InferredContext:
    base = dict(
        client="KSO", objective="cek wajib VPTI", audience="importer",
        decision_required="lanjut impor?", constraints="tidak ada",
    )
    base.update(over)
    return InferredContext(**base)


def test_confirm_promotes_and_stamps_asker() -> None:
    ctx = confirm(_inferred(), asker_id=42)
    assert isinstance(ctx, Context)
    assert ctx.asker_id == 42
    assert ctx.objective == "cek wajib VPTI"


def test_confirm_rejects_blank_field() -> None:
    # never output without a complete Context — blank/whitespace = missing.
    with pytest.raises(ValueError):
        confirm(_inferred(constraints="   "), asker_id=1)


def test_infer_parses_json_into_inferred_context() -> None:
    payload = json.dumps({
        "client": "KSO", "objective": "cek wajib VPTI", "audience": "importer",
        "decision_required": "lanjut impor?", "constraints": "tidak ada",
    })
    inferred = asyncio.run(infer("apakah ban truk wajib VPTI?", StubLLM(payload)))
    assert isinstance(inferred, InferredContext)
    assert inferred.client == "KSO"
    assert inferred.decision_required == "lanjut impor?"


def test_infer_malformed_output_raises_format_error() -> None:
    from vaos.modules.llm_json import LLMFormatError
    with pytest.raises(LLMFormatError):
        asyncio.run(infer("apakah ban truk wajib VPTI?", StubLLM("}{ not json")))
