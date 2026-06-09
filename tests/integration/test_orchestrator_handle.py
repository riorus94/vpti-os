"""Orchestrator.handle — the fixed pipeline wired end-to-end against stubbed edges
(scripted LLM keyed by system prompt, real RetrievalRouter over in-memory fakes,
in-memory Store). Proves: classify -> retrieve -> reason -> (decide) -> reply,
with a CONFIRMED Context passed in (the Telegram layer owns infer->confirm)."""

import asyncio
import json

from vaos.adapters.store.memory import InMemoryStore
from vaos.domain.context import Context
from vaos.domain.grounding import Grounding, GroundingChunk, GroundingSource, RegulationStatus
from vaos.modules.retrieval.router import RetrievalRouter
from vaos.pipeline.orchestrator import Orchestrator
from vaos.ports.retrieval import RegulationSourceUnavailable

_SECTIONS = {k: "x" for k in
             ("ringkasan_eksekutif", "konteks", "analisis", "risiko", "peluang", "rekomendasi")}


class ScriptedLLM:
    """Routes by system prompt so one provider can serve every step of the pipeline."""

    def __init__(self, intent: str, compliance: str = "x", advisory: str = "{}") -> None:
        self._intent, self._compliance, self._advisory = intent, compliance, advisory

    async def complete(self, system: str, prompt: str) -> str:
        if "Classify" in system:
            return self._intent
        if "advisory brief" in system:
            return self._advisory
        return self._compliance  # the compliance answer system prompt


class FakeSource:
    def __init__(self, chunks: list[GroundingChunk]) -> None:
        self._chunks = chunks

    async def query(self, text: str) -> Grounding:
        return Grounding(chunks=self._chunks)


class DeadRegs:
    async def query(self, text: str) -> Grounding:
        raise RegulationSourceUnavailable("down")


def _ctx() -> Context:
    return Context(client="KSO", objective="cek wajib VPTI", audience="importer",
                   decision_required="lanjut?", constraints="-", asker_id=1)


def _pasal(status: RegulationStatus = RegulationStatus.BERLAKU) -> GroundingChunk:
    return GroundingChunk(source=GroundingSource.PASAL_ID, reference="Permendag X Pasal 3",
                          text="LS wajib.", score=0.95, status=status)


class RecordingWeb:
    def __init__(self, snippets: list[str] | None = None) -> None:
        self._snippets = snippets or []
        self.queries: list[str] = []

    async def search(self, query: str) -> list[str]:
        self.queries.append(query)
        return self._snippets


_ADVISORY = json.dumps({
    "thinking_model": "pre_mortem", "sections": _SECTIONS,
    "finding": {"compliance_status": "not_applicable", "risks": [], "opportunities": []},
})


def test_strategy_intent_incorporates_web_search() -> None:
    web = RecordingWeb(["tren pasar baja 2026"])
    orch = Orchestrator(
        llm=ScriptedLLM(intent="strategy", advisory=_ADVISORY), store=InMemoryStore(),
        router=RetrievalRouter(regs=FakeSource([]), vault=FakeSource([])), web=web,
    )
    asyncio.run(orch.handle("strategi ekspansi?", _ctx(), context_id="ctx-w"))
    assert web.queries == ["strategi ekspansi?"]   # HYBRID intent fetched the web


def test_compliance_never_calls_web() -> None:
    web = RecordingWeb(["should never be fetched"])
    orch = Orchestrator(
        llm=ScriptedLLM(intent="compliance", compliance="Ya, wajib."), store=InMemoryStore(),
        router=RetrievalRouter(regs=FakeSource([_pasal()]), vault=FakeSource([])), web=web,
    )
    asyncio.run(orch.handle("wajib LS?", _ctx(), context_id="ctx-c"))
    assert web.queries == []   # guardrail: compliance never reaches the web


def test_risk_advisory_does_not_call_web() -> None:
    web = RecordingWeb(["x"])
    orch = Orchestrator(
        llm=ScriptedLLM(intent="risk", advisory=_ADVISORY), store=InMemoryStore(),
        router=RetrievalRouter(regs=FakeSource([]), vault=FakeSource([])), web=web,
    )
    asyncio.run(orch.handle("risiko?", _ctx(), context_id="ctx-r"))
    assert web.queries == []   # risk is INTERNAL (web only for strategy/opportunity)


def test_compliance_query_returns_grounded_answer_text() -> None:
    llm = ScriptedLLM(intent="compliance", compliance="Ya, wajib LS per Permendag X Pasal 3.")
    router = RetrievalRouter(regs=FakeSource([_pasal()]), vault=FakeSource([]))
    orch = Orchestrator(llm=llm, store=InMemoryStore(), router=router)

    reply = asyncio.run(orch.handle("wajib LS?", _ctx(), context_id="ctx-1"))
    assert reply.startswith("Ya, wajib LS per Permendag X Pasal 3.")
    assert "Sumber: 1 pasal_id, 0 vault, 0 web" in reply   # transparency footer


def test_grounding_source_counts() -> None:
    g = Grounding(chunks=[
        _pasal(),
        GroundingChunk(source=GroundingSource.VAULT, reference="n1", text="t", score=0.5),
        GroundingChunk(source=GroundingSource.VAULT, reference="n2", text="t", score=0.4),
    ])
    assert g.source_counts == {GroundingSource.PASAL_ID: 1, GroundingSource.VAULT: 2}


def test_compliance_empty_grounding_refusal_is_transparent_and_logs_gap() -> None:
    llm = ScriptedLLM(intent="compliance", compliance="should-not-be-used")
    router = RetrievalRouter(regs=FakeSource([]), vault=FakeSource([]))  # empty grounding
    store = InMemoryStore()
    orch = Orchestrator(llm=llm, store=store, router=router)

    reply = asyncio.run(orch.handle("wajib LS?", _ctx(), context_id="ctx-e"))
    assert "knowledge gap" in reply.lower()              # transparent: says it was recorded
    assert "Sumber: 0 pasal_id, 0 vault, 0 web" in reply  # what was checked
    assert len(asyncio.run(store.knowledge_gaps())) == 1


def test_compliance_with_dead_regulation_source_refuses_and_logs() -> None:
    # pasal-id down: handle must return the source-unavailable refusal (NOT the
    # unused compliance answer), and log it as an ops event — never a knowledge gap.
    llm = ScriptedLLM(intent="compliance", compliance="should-not-be-used")
    router = RetrievalRouter(regs=DeadRegs(), vault=FakeSource([]))
    store = InMemoryStore()
    orch = Orchestrator(llm=llm, store=store, router=router)

    reply = asyncio.run(orch.handle("wajib LS?", _ctx(), context_id="ctx-9"))
    assert "tidak dapat diakses" in reply.lower()
    assert asyncio.run(store.knowledge_gaps()) == []
    assert [k for k, _ in asyncio.run(store.events())] == ["source_unavailable"]


def test_advisory_query_returns_brief_and_proposes_actions() -> None:
    payload = json.dumps({
        "thinking_model": "pre_mortem",
        "sections": _SECTIONS,
        "finding": {
            "compliance_status": "non_compliant",
            "risks": [{"description": "late LS", "severity": "high"}],
            "opportunities": [],
        },
    })
    llm = ScriptedLLM(intent="risk", advisory=payload)
    router = RetrievalRouter(regs=FakeSource([]), vault=FakeSource([]))
    orch = Orchestrator(llm=llm, store=InMemoryStore(), router=router)

    reply = asyncio.run(orch.handle("haruskah ekspansi?", _ctx(), context_id="ctx-7"))
    assert "pre_mortem" in reply
    # non_compliant -> remediation, plus one risk_flag = 2 proposed Actions.
    assert "2 tindakan diusulkan" in reply
    assert "Sumber:" in reply   # transparency footer on advisory briefs too
