"""Advisory Brief — six-section structured output + Finding (vaos-mvp/07, Q5/Q8).

Selects a Thinking Model (registry + per-intent default fallback), names it in the
brief by construction, and emits a typed Finding. Returns an AdvisoryBrief — no
tuples, no Store, only the LLM port.
"""

from vaos.domain.context import Context
from vaos.domain.grounding import Grounding
from vaos.domain.intent import Intent
from vaos.domain.output import AdvisoryBrief, AdvisoryPayload
from vaos.modules.llm_json import complete_json
from vaos.modules.reasoning.thinking_models import DEFAULT_BY_INTENT, REGISTRY
from vaos.ports.llm import LLMClient

_SYSTEM = (
    "Produce an advisory brief as JSON with keys: thinking_model, sections "
    "(ringkasan_eksekutif, konteks, analisis, risiko, peluang, rekomendasi), "
    "finding (compliance_status, risks, opportunities)."
)


async def brief(
    query: str, context: Context, intent: Intent, grounding: Grounding, llm: LLMClient
) -> AdvisoryBrief:
    payload = await complete_json(llm, _SYSTEM, query, AdvisoryPayload)
    # Registry validation is a domain decision, applied after the parse: an
    # unregistered model is a soft fallback, never a parse failure.
    model = payload.thinking_model
    if model not in REGISTRY:
        model = DEFAULT_BY_INTENT.get(intent, "systems_thinking")
    return AdvisoryBrief(
        sections=payload.sections, thinking_model=model, finding=payload.finding
    )
