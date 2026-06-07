"""Telegram transport seam (#1/#20). The long-poll loop in bot.py depends only on
the TelegramClient protocol, so it is testable with a fake. HttpTelegramClient is
the thin HTTP adapter over the Bot API; its JSON->Update parsing is unit-tested
with a mocked transport, but the live long-poll is smoke-tested with a real token.
"""

from typing import Any, Protocol

import httpx
from pydantic import BaseModel


class Update(BaseModel):
    """The only fields the dispatch loop needs from a Telegram update."""

    update_id: int
    user_id: int
    chat_id: int
    text: str


class TelegramClient(Protocol):
    async def get_updates(self, offset: int) -> list[Update]: ...
    async def send_message(self, chat_id: int, text: str) -> None: ...


class HttpTelegramClient:
    def __init__(self, token: str, http: httpx.AsyncClient | None = None) -> None:
        self._base = f"https://api.telegram.org/bot{token}"
        self._http = http or httpx.AsyncClient(timeout=35.0)

    async def get_updates(self, offset: int) -> list[Update]:
        response = await self._http.get(
            f"{self._base}/getUpdates", params={"offset": offset, "timeout": 30}
        )
        response.raise_for_status()
        return [u for u in map(_parse, response.json().get("result", [])) if u is not None]

    async def send_message(self, chat_id: int, text: str) -> None:
        response = await self._http.post(
            f"{self._base}/sendMessage", json={"chat_id": chat_id, "text": text}
        )
        response.raise_for_status()


def _parse(item: dict[str, Any]) -> Update | None:
    """Map a raw Telegram update to an Update, skipping non-text / non-message ones."""
    message = item.get("message") or {}
    sender, chat, text = message.get("from") or {}, message.get("chat") or {}, message.get("text")
    if text is None or "id" not in sender or "id" not in chat:
        return None
    return Update(update_id=item["update_id"], user_id=sender["id"], chat_id=chat["id"], text=text)
