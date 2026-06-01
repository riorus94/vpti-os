"""Retrieval router — dispatches sub-queries to the right source and merges,
tagging each chunk by GroundingSource (vaos-mvp/05, ADR-0002)."""

from vaos.domain.context import Context
from vaos.domain.grounding import Grounding


async def retrieve(query: str, context: Context) -> Grounding:
    raise NotImplementedError("vaos-mvp/05")
