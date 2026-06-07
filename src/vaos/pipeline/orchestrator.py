"""Orchestrator — the fixed request pipeline.

    receive -> build/confirm Context -> classify Intent -> retrieve grounding
            -> compliance answer (grounded-or-refuse)  [Intent.COMPLIANCE]
            -> advisory brief + Finding -> Decision Engine -> propose Actions  [advisory]
            -> log everything

Enforces the boundary invariants: no output without a confirmed Context; no
Advisory Brief without a named Thinking Model; compliance is grounded-or-refuse.
Depends only on ports — never on a concrete adapter.

Owns the I/O that reasoning deliberately does NOT (Q3): when compliance.answer
returns a Refusal, the orchestrator calls store.record_knowledge_gap(...). A
Refusal the orchestrator fails to handle is a visible bug, not a silent one.
"""

from vaos.domain.context import Context
from vaos.domain.decision_engine import decide
from vaos.domain.output import Refusal
from vaos.modules.intent_classifier import classify
from vaos.modules.reasoning import advisory, compliance
from vaos.modules.retrieval.router import RetrievalRouter
from vaos.ports.llm import LLMClient
from vaos.ports.store import Store


class Orchestrator:
    def __init__(self, llm: LLMClient, store: Store, router: RetrievalRouter) -> None:
        self._llm = llm
        self._store = store
        self._router = router

    async def handle(self, query: str, context: Context, context_id: str) -> str:
        # Context is already CONFIRMED (the Telegram layer owns infer->confirm);
        # the orchestrator holds no conversational memory (ADR-0003).
        intent = await classify(query, context, self._llm)
        grounding = await self._router.retrieve(query, context)

        if not intent.is_advisory:
            result = await compliance.answer(query, context, grounding, self._llm)
            if isinstance(result, Refusal):
                await self.log_refusal(result, query, context_id)
                return result.message
            return result.text

        brief = await advisory.brief(query, context, intent, grounding, self._llm)
        actions = decide(brief.finding)
        # Persisting the full output + actions is vaos-mvp/09; here we render the reply.
        named = f"[{brief.thinking_model}] {brief.sections.ringkasan_eksekutif}"
        return f"{named}\n{len(actions)} tindakan diusulkan."

    async def log_refusal(self, refusal: Refusal, query: str, context_id: str) -> None:
        # A Refusal the orchestrator fails to log would be a silent gap — the exact
        # failure mode ADR-0001 exists to prevent. Two writes by design: the
        # Knowledge-Gap backlog feeds reviewers; the event log feeds analytics.
        # The Refusal classifies itself (domain/output.py): a source-unavailable
        # refusal is an ops failure, not missing content, so it skips the backlog.
        if refusal.is_knowledge_gap:
            await self._store.record_knowledge_gap(query, context_id)
        await self._store.log_event(
            refusal.event_kind,
            {
                "reason": refusal.reason.value,
                "query": query,
                "context_id": context_id,
                "superseding_reference": refusal.superseding_reference,
            },
        )
