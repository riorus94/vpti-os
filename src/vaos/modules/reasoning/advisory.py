"""Advisory Brief — six-section structured output + Finding (vaos-mvp/07, Q5/Q8).

Selects a Thinking Model (registry + per-intent default fallback), names it in the
brief by construction, and emits a typed Finding. Returns an AdvisoryBrief — no
tuples, no Store, only the LLM port.
"""

import json

from vaos.domain.context import Context
from vaos.domain.finding import Finding
from vaos.domain.grounding import Grounding
from vaos.domain.intent import Intent
from vaos.domain.output import AdvisoryBrief, SixSections
from vaos.ports.llm import LLMClient

_SYSTEM = (
    "Produce an advisory brief as JSON with keys: thinking_model, sections "
    "(ringkasan_eksekutif, konteks, analisis, risiko, peluang, rekomendasi), "
    "finding (compliance_status, risks, opportunities)."
)


async def brief(
    query: str, context: Context, intent: Intent, grounding: Grounding, llm: LLMClient
) -> AdvisoryBrief:
    data = json.loads(await llm.complete(_SYSTEM, query))
    return AdvisoryBrief(
        sections=SixSections(**data["sections"]),
        thinking_model=data["thinking_model"],
        finding=Finding(**data["finding"]),
    )
