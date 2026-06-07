"""Telegram infer->confirm handshake (#1, ADR-0003). The conversation logic is
tested here; the getUpdates long-poll loop is thin I/O and is not unit-tested.

Short-lived pending-confirmation state only — no conversational memory: once a
request completes the pending slot is cleared and nothing carries to the next."""

import asyncio
import json

from vaos.adapters.llm.stub import StubLLM
from vaos.adapters.telegram.bot import TelegramBot
from vaos.config import Settings

_INFER = json.dumps({
    "client": "KSO", "objective": "cek wajib VPTI", "audience": "importer",
    "decision_required": "lanjut impor?", "constraints": "-",
})


class FakeOrchestrator:
    def __init__(self, reply: str = "JAWABAN") -> None:
        self.reply = reply
        self.calls: list[tuple[str, int]] = []

    async def handle(self, query: str, context: object, context_id: str) -> str:
        self.calls.append((query, context.asker_id))  # type: ignore[attr-defined]
        return self.reply


def _bot(orch: FakeOrchestrator | None = None) -> TelegramBot:
    return TelegramBot(
        Settings(telegram_allowlist="7,8,9"),
        llm=StubLLM(_INFER),
        orchestrator=orch or FakeOrchestrator(),
    )


class _BoomLLM:
    async def complete(self, system: str, prompt: str) -> str:
        raise AssertionError("the LLM must not be called for a slash command")


def test_slash_commands_return_help_without_calling_the_llm() -> None:
    bot = TelegramBot(
        Settings(telegram_allowlist="8"), llm=_BoomLLM(), orchestrator=FakeOrchestrator()
    )
    start = asyncio.run(bot.on_message(user_id=8, text="/start"))
    assert "VPTI" in start and "ya/tidak" in start.lower()   # onboarding, not a context prompt
    assert asyncio.run(bot.on_message(user_id=8, text="/help")) == start


def test_unauthorized_sender_is_rejected_without_processing() -> None:
    orch = FakeOrchestrator()
    bot = _bot(orch)
    reply = asyncio.run(bot.on_message(user_id=42, text="apakah ban truk wajib VPTI?"))
    assert "akses" in reply.lower()
    assert orch.calls == []


def test_new_query_infers_and_asks_to_confirm_without_processing() -> None:
    orch = FakeOrchestrator()
    bot = _bot(orch)
    reply = asyncio.run(bot.on_message(user_id=8, text="apakah ban truk wajib VPTI?"))
    assert "cek wajib VPTI" in reply           # inferred objective surfaced for confirmation
    assert "ya/tidak" in reply.lower()
    assert orch.calls == []                     # not processed until the user confirms


def test_confirmation_dispatches_original_query_then_clears_pending() -> None:
    orch = FakeOrchestrator(reply="Ya, wajib LS.")
    bot = _bot(orch)
    asyncio.run(bot.on_message(user_id=8, text="apakah ban truk wajib VPTI?"))  # sets pending
    reply = asyncio.run(bot.on_message(user_id=8, text="ya"))                    # confirms

    assert reply == "Ya, wajib LS."
    # the ORIGINAL query is dispatched (not "ya"), with the asker id stamped on the Context
    assert orch.calls == [("apakah ban truk wajib VPTI?", 8)]
    # pending cleared: another "ya" is now a fresh query (re-infer), not a second dispatch
    asyncio.run(bot.on_message(user_id=8, text="ya"))
    assert len(orch.calls) == 1
