"""Context Builder — infer + confirm (vaos-mvp/02, Q1).

Inference is behind the LLMClient port (stubbable); validation is pure
(domain/context.py). The pipeline never proceeds without a confirmed Context.
"""

from vaos.domain.context import Context, InferredContext
from vaos.modules.llm_json import complete_json
from vaos.ports.llm import LLMClient

_SYSTEM = (
    "Infer a VPTI request Context. Reply with ONLY a JSON object with keys: "
    "client, objective, audience, decision_required, constraints."
)


async def infer(query: str, llm: LLMClient) -> InferredContext:
    """Propose a five-field Context from the raw query, to show the user.
    A malformed completion surfaces as LLMFormatError (the caller decides what
    to tell the user) — never a silent or half-built Context."""
    return await complete_json(llm, _SYSTEM, query, InferredContext)


def confirm(inferred: InferredContext, asker_id: int) -> Context:
    """Promote an (accepted/corrected) InferredContext to a validated Context."""
    return Context(**inferred.model_dump(), asker_id=asker_id)
