"""Telegram getUpdates long-poll loop (#20). The dispatch + offset logic is tested
against a fake TelegramClient (no network); HttpTelegramClient's JSON->Update parse
is tested with a mocked transport. The live long-poll itself is a token smoke test."""

import json

import httpx

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
            {"update_id": 2, "message": {"from": {"id": 8}, "chat": {"id": 100}}},  # no text -> skip
        ]})

    transport = httpx.MockTransport(handler)
    client = HttpTelegramClient("tok", http=httpx.AsyncClient(transport=transport))
    updates = await client.get_updates(0)

    assert [u.update_id for u in updates] == [1]
    assert updates[0].user_id == 8 and updates[0].chat_id == 100 and updates[0].text == "halo"
