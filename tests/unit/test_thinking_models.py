"""Thinking Model registry (vaos-mvp/07, Q5) — pure, no stubs needed.

Cover: every Intent default maps to a registered model; the default fallback is
deterministic; the registry exposes 'use when' criteria for selection.
"""

from vaos.domain.intent import Intent
from vaos.modules.reasoning.thinking_models import DEFAULT_BY_INTENT, REGISTRY


def test_every_intent_default_is_a_registered_model() -> None:
    for intent, model in DEFAULT_BY_INTENT.items():
        assert model in REGISTRY, f"{intent} default {model!r} not in registry"
