"""Thinking Model registry (vaos-mvp/07, Q5).

Each entry carries 'use when' criteria; the LLM picks + justifies a model, the
choice is named in the brief, and a deterministic per-intent default is used on
fallback. Registry lookup + default are pure (testable); the LLM choice is behind
the port.
"""

from vaos.domain.intent import Intent

REGISTRY: dict[str, str] = {
    "first_principles": "Reduce to fundamentals when assumptions are shaky.",
    "systems_thinking": "Trace interactions and feedback across the whole system.",
    "pre_mortem": "Assume failure, work backward to causes — for risk framing.",
    "five_whys": "Drill to root cause of a specific problem.",
    "second_order": "Reason about downstream / knock-on effects.",
}

DEFAULT_BY_INTENT: dict[Intent, str] = {
    Intent.RISK: "pre_mortem",
    Intent.OPPORTUNITY: "second_order",
    Intent.STRATEGY: "systems_thinking",
}
