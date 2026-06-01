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


def _chunk(status: RegulationStatus, superseded_by: str | None = None) -> GroundingChunk:
    return GroundingChunk(
        source=GroundingSource.PASAL_ID, reference="Permendag X Pasal 3",
        text="LS wajib untuk komoditas ini.", score=0.95, status=status,
        superseded_by=superseded_by,
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


def test_amended_regulation_names_superseding_reference() -> None:
    # AC #3: a dicabut/diubah regulation must NAME the superseding reference and
    # never be asserted as current. The refusal carries it; the message names it.
    g = Grounding(chunks=[_chunk(RegulationStatus.DIUBAH, superseded_by="Permendag Y Pasal 5")])
    res = asyncio.run(answer("wajib LS?", _ctx(), g, StubLLM("x")))
    assert isinstance(res, Refusal)
    assert res.reason is GapReason.REVOKED_REGULATION
    assert res.superseding_reference == "Permendag Y Pasal 5"
    assert "Permendag Y Pasal 5" in res.message


def test_in_force_grounding_returns_compliance_answer() -> None:
    g = Grounding(chunks=[_chunk(RegulationStatus.BERLAKU)])
    res = asyncio.run(answer("wajib LS?", _ctx(), g, StubLLM("Ya, wajib LS per Permendag X Pasal 3.")))
    assert isinstance(res, ComplianceAnswer)
    assert res.text == "Ya, wajib LS per Permendag X Pasal 3."
    assert res.citations == g.chunks
