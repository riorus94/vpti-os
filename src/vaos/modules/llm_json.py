"""Structured LLM output — the seam over the LLMClient port that turns a raw
completion into a validated Pydantic model, or raises one typed failure.

Strict by design: one provider call, json.loads, model_validate. No retry, no
fence-stripping (decide a repair decorator later if a provider needs it). The
LLMClient port stays a single string-returning method (ADR-0007); this module
is provider-independent, so adapters never re-implement parsing.

Callers own the fallback on LLMFormatError (e.g. intent -> COMPLIANCE,
advisory -> per-intent default model) — this module never decides domain policy.
"""

import json

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


async def complete_json[T: BaseModel](
    llm: LLMClient, system: str, prompt: str, schema: type[T]
) -> T:
    raw = await llm.complete(system, prompt)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise LLMFormatError(raw, schema, e) from e
    try:
        return schema.model_validate(data)
    except ValidationError as e:
        raise LLMFormatError(raw, schema, e) from e
