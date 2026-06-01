"""Advisory Brief — six-section structured output + Finding (vaos-mvp/07, Q5/Q8).

Selects a Thinking Model (registry + per-intent default fallback), names it in the
brief by construction, and emits a typed Finding. Returns an AdvisoryBrief — no
tuples, no Store, only the LLM port.
"""

from vaos.domain.context import Context
from vaos.domain.grounding import Grounding
from vaos.domain.intent import Intent
from vaos.domain.output import AdvisoryBrief
from vaos.ports.llm import LLMClient


async def brief(
    query: str, context: Context, intent: Intent, grounding: Grounding, llm: LLMClient
) -> AdvisoryBrief:
    raise NotImplementedError("vaos-mvp/07 — return AdvisoryBrief(sections, thinking_model, finding)")
