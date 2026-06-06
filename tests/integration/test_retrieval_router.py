"""Retrieval router (vaos-mvp/05) — real RetrievalRouter wired against stubbed
external edges (in-memory regulation + internal legs; no FAISS, no pasal-id HTTP).

Covers the load-bearing ADR-0002 invariant through the router's interface:
pasal-id unavailable -> regulation grounding reported unavailable, never
FAISS-substituted.
"""

import asyncio

from vaos.domain.context import Context
from vaos.domain.grounding import Grounding, GroundingChunk, GroundingSource
from vaos.modules.retrieval.router import RetrievalRouter
from vaos.ports.retrieval import RegulationSourceUnavailable


def _ctx() -> Context:
    return Context(client="KSO", objective="cek wajib VPTI", audience="importer",
                   decision_required="lanjut?", constraints="-", asker_id=1)


class DeadPasalId:
    async def query(self, text: str) -> Grounding:
        raise RegulationSourceUnavailable("pasal-id unreachable")


class FixtureVault:
    async def query(self, text: str) -> Grounding:
        return Grounding(chunks=[GroundingChunk(
            source=GroundingSource.VAULT, reference="note-LS",
            text="catatan proses internal LS", score=0.82)])


def test_pasal_id_unavailable_is_not_substituted_by_faiss() -> None:
    router = RetrievalRouter(regs=DeadPasalId(), vault=FixtureVault())
    g = asyncio.run(router.retrieve("apakah HS 4011 wajib LS?", _ctx()))

    assert g.regulation_unavailable is True
    # The internal note is present, but it is NOT promoted to regulation grounding.
    assert all(c.source is GroundingSource.VAULT for c in g.chunks)
    assert not any(c.source is GroundingSource.PASAL_ID for c in g.chunks)
