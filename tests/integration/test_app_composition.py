"""Composition root (#19): build_bot assembles the real object graph from Settings
and a message flows end-to-end through on_message. LLM is scripted (keyed by system
prompt) and the store is injected so the test can observe what the wired pipeline did;
retrieval legs are the interim empty sources, so a confirmed compliance query
correctly refuses for lack of grounding — proving bot -> orchestrator -> router ->
reasoning -> store are all connected."""

import json

import pytest

from vaos.adapters.llm.anthropic_claude import AnthropicLLM
from vaos.adapters.llm.azure_openai import AzureOpenAILLM
from vaos.adapters.llm.stub import StubLLM
from vaos.adapters.retrieval.stub import EmptyInternalSource
from vaos.adapters.store.memory import InMemoryStore
from vaos.app import _build_internal_source, _build_llm, build_bot
from vaos.config import Settings

_CTX = json.dumps({
    "client": "KSO", "objective": "cek wajib VPTI", "audience": "importer",
    "decision_required": "lanjut?", "constraints": "-",
})


class ScriptedLLM:
    async def complete(self, system: str, prompt: str) -> str:
        if "Infer" in system:
            return _CTX
        if "Classify" in system:
            return "compliance"
        return "Ya, wajib."  # compliance-answer system prompt (never reached on empty grounding)


def test_build_llm_selects_adapter_by_provider() -> None:
    assert isinstance(_build_llm(Settings(llm_provider="stub")), StubLLM)
    assert isinstance(
        _build_llm(Settings(llm_provider="azure_openai")), AzureOpenAILLM
    )
    assert isinstance(_build_llm(Settings(llm_provider="anthropic")), AnthropicLLM)
    with pytest.raises(ValueError):
        _build_llm(Settings(llm_provider="bogus"))


def test_build_internal_source_selects_leg_by_config() -> None:
    from vaos.modules.retrieval.faiss_vault import FaissVault

    empty = _build_internal_source(Settings(internal_source="empty"))
    assert isinstance(empty, EmptyInternalSource)
    assert isinstance(_build_internal_source(Settings(internal_source="faiss")), FaissVault)
    with pytest.raises(ValueError):
        _build_internal_source(Settings(internal_source="bogus"))


async def test_composition_root_assembles_runnable_bot() -> None:
    store = InMemoryStore()
    bot = build_bot(
        Settings(telegram_allowlist="8", llm_provider="stub"),
        llm=ScriptedLLM(),
        store=store,
    )

    # New query -> infer -> confirmation prompt surfacing the inferred objective.
    prompt = await bot.on_message(user_id=8, text="wajib LS?")
    assert "cek wajib VPTI" in prompt

    # Confirm -> full pipeline runs; empty grounding -> grounded-or-refuse -> logged.
    reply = await bot.on_message(user_id=8, text="ya")
    assert reply  # a refusal message, not an empty string
    assert len(await store.knowledge_gaps()) == 1
