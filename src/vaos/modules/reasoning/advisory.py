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
    "Produce an advisory brief as a single raw JSON object — no markdown fences, no "
    "prose — with exactly these keys:\n"
    "- thinking_model: string\n"
    "- sections: object with string values for keys ringkasan_eksekutif, konteks, "
    "analisis, risiko, peluang, rekomendasi\n"
    "- finding: object with keys compliance_status (one of: compliant, non_compliant, "
    "not_applicable, unknown), risks (array of objects {description: string, severity: "
    "string}), opportunities (array of objects {description: string})"
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
