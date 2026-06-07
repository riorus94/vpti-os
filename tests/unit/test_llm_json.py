"""complete_json seam — parse + validate an LLM string into a Pydantic model,
or raise one LLMFormatError. Strict (no retry, no fence-strip). LLM behind StubLLM."""

import asyncio
import json

import pytest

from vaos.adapters.llm.stub import StubLLM
from vaos.domain.context import InferredContext
from vaos.modules.llm_json import LLMFormatError, complete_json

_VALID = json.dumps({
    "client": "KSO", "objective": "cek wajib VPTI", "audience": "importer",
    "decision_required": "lanjut impor?", "constraints": "tidak ada",
})


class _CapturingLLM:
    def __init__(self, canned: str) -> None:
        self._canned, self.system = canned, ""

    async def complete(self, system: str, prompt: str) -> str:
        self.system = system
        return self._canned


def test_injects_target_schema_into_the_prompt() -> None:
    llm = _CapturingLLM(_VALID)
    asyncio.run(complete_json(llm, "Infer the Context.", "q", InferredContext))
    assert "Infer the Context." in llm.system          # caller framing preserved
    assert "decision_required" in llm.system           # schema field types surfaced to the model


def test_parses_valid_json_into_schema() -> None:
    out = asyncio.run(complete_json(StubLLM(_VALID), "sys", "q", InferredContext))
    assert isinstance(out, InferredContext)
    assert out.client == "KSO"


def test_parses_json_wrapped_in_markdown_fences() -> None:
    fenced = f"```json\n{_VALID}\n```"
    out = asyncio.run(complete_json(StubLLM(fenced), "sys", "q", InferredContext))
    assert out.objective == "cek wajib VPTI"


def test_parses_json_with_surrounding_prose() -> None:
    wrapped = f"Tentu, ini hasilnya:\n{_VALID}\nSemoga membantu."
    out = asyncio.run(complete_json(StubLLM(wrapped), "sys", "q", InferredContext))
    assert out.client == "KSO"


def test_non_json_raises_format_error_wrapping_json_decode() -> None:
    with pytest.raises(LLMFormatError) as exc:
        asyncio.run(complete_json(StubLLM("not json at all"), "sys", "q", InferredContext))
    assert isinstance(exc.value.__cause__, json.JSONDecodeError)


def test_wrong_shape_raises_format_error_wrapping_validation() -> None:
    from pydantic import ValidationError
    missing = json.dumps({"client": "KSO"})  # missing the other four fields
    with pytest.raises(LLMFormatError) as exc:
        asyncio.run(complete_json(StubLLM(missing), "sys", "q", InferredContext))
    assert isinstance(exc.value.__cause__, ValidationError)


def test_format_error_carries_raw_and_schema() -> None:
    with pytest.raises(LLMFormatError) as exc:
        asyncio.run(complete_json(StubLLM("garbage"), "sys", "q", InferredContext))
    assert exc.value.raw == "garbage"
    assert exc.value.schema is InferredContext
