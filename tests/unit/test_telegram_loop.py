"""Telegram getUpdates long-poll loop (#20). The dispatch + offset logic is tested
against a fake TelegramClient (no network); HttpTelegramClient's JSON->Update parse
is tested with a mocked transport. The live long-poll itself is a token smoke test."""

import json

import httpx
import pytest

from vaos.adapters.llm.stub import StubLLM
from vaos.adapters.telegram.bot import TelegramBot
from vaos.adapters.telegram.client import HttpTelegramClient, Update
from vaos.config import Settings

_INFER = json.dumps({
    "client": "KSO", "objective": "cek wajib VPTI", "audience": "importer",
    "decision_required": "lanjut?", "constraints": "-",
})


class FakeOrchestrator:
    async def handle(self, query: str, context: object, context_id: str) -> str:
        return "JAWABAN"


class FakeClient:
    def __init__(self, batches: list[list[Update]]) -> None:
        self._batches = list(batches)
        self.requested_offsets: list[int] = []
        self.sent: list[tuple[int, str]] = []

    async def get_updates(self, offset: int) -> list[Update]:
        self.requested_offsets.append(offset)
        return self._batches.pop(0) if self._batches else []

    async def send_message(self, chat_id: int, text: str) -> None:
        self.sent.append((chat_id, text))


def _bot(client: FakeClient) -> TelegramBot:
    return TelegramBot(
        Settings(telegram_allowlist="8"),
        llm=StubLLM(_INFER),
        orchestrator=FakeOrchestrator(),
        client=client,
    )


async def test_poll_once_routes_update_through_on_message_and_replies() -> None:
    client = FakeClient([[Update(update_id=10, user_id=8, chat_id=100, text="wajib LS?")]])

    new_offset = await _bot(client)._poll_once(0)

    assert new_offset == 11                               # update_id + 1
    assert len(client.sent) == 1
    chat_id, reply = client.sent[0]
    assert chat_id == 100
    assert "cek wajib VPTI" in reply                      # the inferred confirmation prompt


async def test_offset_advances_across_polls_without_reprocessing() -> None:
    client = FakeClient([
        [Update(update_id=5, user_id=8, chat_id=1, text="satu")],
        [Update(update_id=6, user_id=8, chat_id=1, text="dua")],
    ])
    bot = _bot(client)

    first = await bot._poll_once(0)
    second = await bot._poll_once(first)

    assert (first, second) == (6, 7)
    assert client.requested_offsets == [0, 6]             # second poll skips the consumed update


async def test_poll_once_replies_and_advances_even_when_handler_raises() -> None:
    # A single bad message must not kill the loop or leave the user with silence.
    from vaos.config import Settings
    bot = TelegramBot(
        Settings(telegram_allowlist="8"),
        llm=StubLLM("not json — infer will raise LLMFormatError"),
        orchestrator=FakeOrchestrator(),
        client=(client := FakeClient([[Update(update_id=10, user_id=8, chat_id=100, text="hi")]])),
    )

    new_offset = await bot._poll_once(0)

    assert new_offset == 11                  # advanced: the bad update is not reprocessed forever
    assert len(client.sent) == 1             # an error reply was sent, not silence
    assert client.sent[0][0] == 100


async def test_unauthorized_update_still_replies_and_advances() -> None:
    client = FakeClient([[Update(update_id=3, user_id=999, chat_id=7, text="x")]])

    new_offset = await _bot(client)._poll_once(0)

    assert new_offset == 4
    assert client.sent[0][0] == 7
    assert "akses" in client.sent[0][1].lower()           # rejection routed back


async def test_http_client_parses_text_updates_and_skips_others() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": [
            {"update_id": 1,
             "message": {"from": {"id": 8}, "chat": {"id": 100}, "text": "halo"}},
            # next has no text -> skipped by the parser
            {"update_id": 2, "message": {"from": {"id": 8}, "chat": {"id": 100}}},
        ]})

    transport = httpx.MockTransport(handler)
    client = HttpTelegramClient("tok", http=httpx.AsyncClient(transport=transport))
    updates = await client.get_updates(0)

    assert [u.update_id for u in updates] == [1]
    assert updates[0].user_id == 8 and updates[0].chat_id == 100 and updates[0].text == "halo"


def _processing_bot(client: object) -> TelegramBot:
    return TelegramBot(
        Settings(telegram_allowlist="8"),
        llm=StubLLM(_INFER),
        orchestrator=FakeOrchestrator(),
        client=client,  # type: ignore[arg-type]
    )


async def test_handler_failure_is_logged_with_traceback() -> None:
    from loguru import logger
    records: list[str] = []
    sink = logger.add(records.append, level="ERROR")
    try:
        client = FakeClient([[Update(update_id=1, user_id=8, chat_id=9, text="hi")]])
        bot = TelegramBot(
            Settings(telegram_allowlist="8"),
            llm=StubLLM("not json — infer raises"),
            orchestrator=FakeOrchestrator(),
            client=client,
        )
        await bot._poll_once(0)
    finally:
        logger.remove(sink)
    assert any("handling update" in str(r) for r in records)   # error logged for diagnosis
    assert client.sent                                          # user still got a reply


async def test_send_failure_is_logged_and_does_not_stop_the_batch() -> None:
    class SendBoom:
        def __init__(self) -> None:
            self.sends = 0

        async def get_updates(self, offset: int) -> list[Update]:
            return [
                Update(update_id=1, user_id=8, chat_id=9, text="ya"),
                Update(update_id=2, user_id=8, chat_id=9, text="ya"),
            ]

        async def send_message(self, chat_id: int, text: str) -> None:
            self.sends += 1
            raise RuntimeError("send down")

    client = SendBoom()
    new_offset = await _processing_bot(client)._poll_once(0)

    assert new_offset == 3        # both updates processed despite every send failing
    assert client.sends == 2      # tried to send for both, didn't bail after the first


async def test_run_survives_a_transient_getupdates_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import vaos.adapters.telegram.bot as botmod

    async def _no_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(botmod.asyncio, "sleep", _no_sleep)  # don't wait the backoff

    class _Stop(BaseException):
        pass

    class Flaky:
        def __init__(self) -> None:
            self.calls = 0
            self.sent: list[tuple[int, str]] = []

        async def get_updates(self, offset: int) -> list[Update]:
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("transient getUpdates failure")
            if self.calls == 2:
                return [Update(update_id=5, user_id=8, chat_id=9, text="ya")]
            raise _Stop()  # BaseException — escapes run()'s `except Exception` to end the test

        async def send_message(self, chat_id: int, text: str) -> None:
            self.sent.append((chat_id, text))

    client = Flaky()
    with pytest.raises(_Stop):
        await _processing_bot(client).run()
    assert len(client.sent) == 1   # recovered after the transient error and processed the update
