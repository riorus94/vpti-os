"""Structured LLM output — the seam over the LLMClient port that turns a raw
completion into a validated Pydantic model, or raises one typed failure.

Tries strict json.loads first (a clean JSON completion is unchanged), then a
bounded repair for the common ways chat models wrap JSON — markdown code fences
and surrounding prose — before giving up. The LLMClient port stays a single
string-returning method (ADR-0007); this module is provider-independent, so
adapters never re-implement parsing.

Callers own the domain fallback on LLMFormatError (e.g. intent -> COMPLIANCE,
advisory -> per-intent default model) — this module never decides domain policy.
"""

import json
from typing import Any

from pydantic import BaseModel, ValidationError

from vaos.ports.llm import LLMClient


class LLMFormatError(Exception):
    """The LLM returned output that is not valid JSON, or does not match the
    requested schema. Carries the raw text and schema for logging; the wrapped
    cause is a json.JSONDecodeError or a pydantic ValidationError."""

    def __init__(self, raw: str, schema: type[BaseModel], cause: Exception) -> None:
        super().__init__(f"LLM output did not match {schema.__name__}: {cause}")
        self.raw = raw
        self.schema = schema


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if not text.startswith("```"):
        return text
    body = text[text.find("\n") + 1 :] if "\n" in text else text[3:]
    if body.rstrip().endswith("```"):
        body = body.rstrip()[:-3]
    return body.strip()


def _outermost_json(text: str) -> str | None:
    """The span from the first opening bracket to the last closing one, or None."""
    opens = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not opens:
        return None
    start, end = min(opens), max(text.rfind("}"), text.rfind("]"))
    return text[start : end + 1] if end > start else None


def _loads_lenient(raw: str) -> Any:
    """json.loads, tolerating markdown fences and surrounding prose. Raises
    json.JSONDecodeError if no JSON can be recovered (so callers wrap one type)."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    candidate = _strip_code_fences(raw)
    snippet = _outermost_json(candidate)
    # Parse the recovered snippet if any, else re-attempt the candidate so the
    # resulting JSONDecodeError carries a meaningful message for logging.
    return json.loads(snippet if snippet is not None else candidate)


def _schema_instruction(schema: type[BaseModel]) -> str:
    """Tell the model the exact target shape (field types, enums, nested objects),
    so it doesn't return a string where an object/list is expected."""
    return (
        "Respond with ONLY a raw JSON object — no markdown fences, no prose — that "
        "matches this JSON Schema:\n" + json.dumps(schema.model_json_schema())
    )


async def complete_json[T: BaseModel](
    llm: LLMClient, system: str, prompt: str, schema: type[T]
) -> T:
    raw = await llm.complete(f"{system}\n\n{_schema_instruction(schema)}", prompt)
    try:
        data = _loads_lenient(raw)
    except json.JSONDecodeError as e:
        raise LLMFormatError(raw, schema, e) from e
    try:
        return schema.model_validate(data)
    except ValidationError as e:
        raise LLMFormatError(raw, schema, e) from e
