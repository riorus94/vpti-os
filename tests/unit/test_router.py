"""RetrievalRouter — fans out to the regulation leg and the internal leg, merges,
and tags chunks by source. The regulation leg is load-bearing: if it is
unavailable the router never substitutes internal grounding for it (ADR-0002).
Both legs are stubbed with in-memory fakes — no FAISS, no pasal-id HTTP."""

import asyncio

from vaos.domain.context import Context
from vaos.domain.grounding import Grounding, GroundingChunk, GroundingSource
from vaos.modules.retrieval.router import RetrievalRouter
from vaos.ports.retrieval import RegulationSourceUnavailable


def _ctx() -> Context:
    return Context(client="KSO", objective="o", audience="a",
                   decision_required="d", constraints="c", asker_id=1)


def _pasal() -> GroundingChunk:
    return GroundingChunk(source=GroundingSource.PASAL_ID,
                          reference="Permendag 20/2021 Pasal 3", text="…", score=0.9)


def _note() -> GroundingChunk:
    return GroundingChunk(source=GroundingSource.VAULT, reference="note-1", text="…", score=0.8)


class FakeSource:
    def __init__(self, chunks: list[GroundingChunk]) -> None:
        self._chunks = chunks

    async def query(self, text: str) -> Grounding:
        return Grounding(chunks=self._chunks)


class DeadRegulationSource:
    async def query(self, text: str) -> Grounding:
        raise RegulationSourceUnavailable("pasal-id unreachable")


def test_router_merges_both_legs_tagged_by_source() -> None:
    router = RetrievalRouter(regs=FakeSource([_pasal()]), vault=FakeSource([_note()]))
    g = asyncio.run(router.retrieve("apakah wajib LS?", _ctx()))
    assert {c.source for c in g.chunks} == {GroundingSource.PASAL_ID, GroundingSource.VAULT}
    assert g.regulation_unavailable is False


def test_dead_regulation_leg_is_reported_not_substituted() -> None:
    # pasal-id down, but the internal Vault still has a note. ADR-0002: the router
    # must flag the regulation leg unavailable and must NOT pass off the internal
    # note as regulation grounding.
    router = RetrievalRouter(regs=DeadRegulationSource(), vault=FakeSource([_note()]))
    g = asyncio.run(router.retrieve("apakah wajib LS?", _ctx()))
    assert g.regulation_unavailable is True
    assert all(c.source is GroundingSource.VAULT for c in g.chunks)
    assert not any(c.source is GroundingSource.PASAL_ID for c in g.chunks)
