"""Context Builder — infer + confirm (vaos-mvp/02, Q1).

Inference is behind the LLMClient port (stubbable); validation is pure
(domain/context.py). The pipeline never proceeds without a confirmed Context.
"""

from vaos.domain.context import Context, InferredContext
from vaos.ports.llm import LLMClient


async def infer(query: str, llm: LLMClient) -> InferredContext:
    """Propose a five-field Context from the raw query, to show the user."""
    raise NotImplementedError("vaos-mvp/02")


def confirm(inferred: InferredContext, asker_id: int) -> Context:
    """Promote an (accepted/corrected) InferredContext to a validated Context."""
    raise NotImplementedError("vaos-mvp/02")
