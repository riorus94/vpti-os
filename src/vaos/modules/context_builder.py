"""Context Builder — infer + confirm (vaos-mvp/02, Q1).

Inference is behind the LLMClient port (stubbable); validation is pure
(domain/context.py). The pipeline never proceeds without a confirmed Context.
"""

import json

from vaos.domain.context import Context, InferredContext
from vaos.ports.llm import LLMClient

_SYSTEM = (
    "Infer a VPTI request Context. Reply with ONLY a JSON object with keys: "
    "client, objective, audience, decision_required, constraints."
)


async def infer(query: str, llm: LLMClient) -> InferredContext:
    """Propose a five-field Context from the raw query, to show the user."""
    raw = await llm.complete(_SYSTEM, query)
    return InferredContext(**json.loads(raw))


def confirm(inferred: InferredContext, asker_id: int) -> Context:
    """Promote an (accepted/corrected) InferredContext to a validated Context."""
    return Context(**inferred.model_dump(), asker_id=asker_id)
