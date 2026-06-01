"""Context — the five-field frame that scopes every request (ADR / Q1).

Satisfied by infer-plus-confirm: the system proposes an InferredContext, the
user confirms/corrects, and the result is a validated Context. The pipeline
never proceeds without a confirmed Context.
"""

from pydantic import BaseModel, field_validator


class InferredContext(BaseModel):
    """Proposed by the system before the user confirms (vaos-mvp/02)."""

    client: str
    objective: str
    audience: str
    decision_required: str
    constraints: str


class Context(BaseModel):
    """A confirmed Context. All five fields present; asker identity stamped."""

    client: str
    objective: str
    audience: str
    decision_required: str
    constraints: str
    asker_id: int  # Telegram user id (audit trail, ADR-0003)

    @field_validator("client", "objective", "audience", "decision_required", "constraints")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        # Empty / whitespace counts as missing — enforces "never output without Context".
        if not v or not v.strip():
            raise ValueError("Context field must not be blank")
        return v
