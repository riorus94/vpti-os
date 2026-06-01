"""Compliance reasoning — grounded-or-refuse (vaos-mvp/06).

Asserts on the RETURNED TYPE, not a Store side-effect (Q3): empty grounding ->
Refusal(EMPTY_GROUNDING). LLM behind a StubLLM; no Store needed.
"""

import asyncio

from vaos.adapters.llm.stub import StubLLM
from vaos.domain.context import Context
from vaos.domain.grounding import Grounding, GroundingChunk, GroundingSource, RegulationStatus
from vaos.domain.output import ComplianceAnswer, GapReason, Refusal
from vaos.modules.reasoning.compliance import answer


def _chunk(status: RegulationStatus) -> GroundingChunk:
    return GroundingChunk(
        source=GroundingSource.PASAL_ID, reference="Permendag X Pasal 3",
        text="LS wajib untuk komoditas ini.", score=0.95, status=status,
    )


def _ctx() -> Context:
    return Context(
        client="KSO", objective="cek wajib VPTI", audience="importer",
        decision_required="lanjut?", constraints="-", asker_id=1,
    )


def test_empty_grounding_returns_refusal() -> None:
    res = asyncio.run(answer("HS 3824.99 wajib LS?", _ctx(), Grounding(chunks=[]), StubLLM("x")))
    assert isinstance(res, Refusal)
    assert res.reason is GapReason.EMPTY_GROUNDING


def test_revoked_regulation_returns_refusal() -> None:
    g = Grounding(chunks=[_chunk(RegulationStatus.DICABUT)])
    res = asyncio.run(answer("wajib LS?", _ctx(), g, StubLLM("x")))
    assert isinstance(res, Refusal)
    assert res.reason is GapReason.REVOKED_REGULATION


def test_in_force_grounding_returns_compliance_answer() -> None:
    g = Grounding(chunks=[_chunk(RegulationStatus.BERLAKU)])
    res = asyncio.run(answer("wajib LS?", _ctx(), g, StubLLM("Ya, wajib LS per Permendag X Pasal 3.")))
    assert isinstance(res, ComplianceAnswer)
    assert res.text == "Ya, wajib LS per Permendag X Pasal 3."
    assert res.citations == g.chunks
