"""Telegram bot — long-polling (vaos-mvp/01, ADR-0003).

Enforces the allowlist (rejects unknown user IDs), stamps asker identity onto the
request, drives the infer+confirm handshake, and (Phase 2) the Approver flow.
No conversational memory — only short-lived pending-confirmation state: at most
one InferredContext per user awaiting yes/no, cleared the moment a request
completes. Nothing carries between completed requests (ADR-0003).

The conversation logic lives in on_message (unit-tested); run() is the getUpdates
I/O loop that feeds it. The loop is resilient: a failure handling one update, or a
transport failure in getUpdates/sendMessage, is logged (loguru) and never kills the
process — so silence is always explained in the logs, never a dead bot.
"""

import asyncio
from uuid import uuid4

from loguru import logger

from vaos.adapters.telegram.client import TelegramClient
from vaos.config import Settings
from vaos.domain.context import InferredContext
from vaos.modules.context_builder import confirm, infer
from vaos.pipeline.orchestrator import Orchestrator
from vaos.ports.llm import LLMClient

_AFFIRMATIVE = {"ya", "yes", "y", "benar", "betul", "ok", "oke", "lanjut"}
_COMMANDS = {"/start", "/help"}
_REJECTION = "Maaf, Anda tidak memiliki akses ke layanan ini."
_HELP = (
    "Halo! Saya VAOS — asisten kepatuhan VPTI.\n"
    'Kirim pertanyaan biasa (bukan perintah), contoh: "apakah ban truk wajib VPTI?".\n'
    'Saya akan meringkas konteksnya lalu bertanya "Benar? (ya/tidak)" sebelum memproses.'
)
_HANDLER_ERROR = "Maaf, terjadi kesalahan saat memproses pesan Anda. Coba lagi."
_RETRY_BACKOFF_SECONDS = 3.0


class TelegramBot:
    def __init__(
        self,
        settings: Settings,
        llm: LLMClient | None = None,
        orchestrator: Orchestrator | None = None,
        client: TelegramClient | None = None,
    ) -> None:
        self._settings = settings
        self._allowlist = settings.allowlist_ids()
        self._llm = llm
        self._orchestrator = orchestrator
        self._client = client
        # user_id -> (original query, inferred context awaiting confirmation)
        self._pending: dict[int, tuple[str, InferredContext]] = {}

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self._allowlist

    async def on_message(self, user_id: int, text: str) -> str:
        if not self.is_authorized(user_id):
            return _REJECTION
        if text.strip().lower() in _COMMANDS:
            return _HELP  # onboarding, not a query — no LLM call
        assert self._llm is not None and self._orchestrator is not None  # required for processing

        pending = self._pending.get(user_id)
        if pending is not None and text.strip().lower() in _AFFIRMATIVE:
            query, inferred = self._pending.pop(user_id)
            context = confirm(inferred, asker_id=user_id)
            return await self._orchestrator.handle(query, context, context_id=uuid4().hex)

        # A new query (or a correction): infer a Context and ask the user to confirm.
        inferred = await infer(text, self._llm)
        self._pending[user_id] = (text, inferred)
        return (
            f"Saya baca: Objektif: {inferred.objective}; Audiens: {inferred.audience}; "
            f"Keputusan: {inferred.decision_required}. Benar? (ya/tidak)"
        )

    async def run(self) -> None:
        """Long-poll getUpdates forever. A transport failure in a cycle is logged and
        retried after a bounded backoff — the loop never dies on a transient error."""
        logger.info(
            "VAOS bot polling: llm_provider={}, internal_source={}, allowlist={} user(s)",
            self._settings.llm_provider, self._settings.internal_source, len(self._allowlist),
        )
        offset = 0
        while True:
            try:
                offset = await self._poll_once(offset)
            except Exception:
                logger.exception("getUpdates cycle failed; retrying in {}s", _RETRY_BACKOFF_SECONDS)
                await asyncio.sleep(_RETRY_BACKOFF_SECONDS)

    async def _poll_once(self, offset: int) -> int:
        """Process one getUpdates batch; return the next offset (last id + 1) so the
        consumed updates are never re-fetched. Per-update handler and send failures
        are logged and never stop the batch."""
        assert self._client is not None
        for update in await self._client.get_updates(offset):
            logger.info(
                "update {} from {}: {!r}", update.update_id, update.user_id, update.text[:80]
            )
            try:
                reply = await self.on_message(update.user_id, update.text)
            except Exception:
                logger.exception(
                    "handling update {} from {} failed", update.update_id, update.user_id
                )
                reply = _HANDLER_ERROR
            try:
                await self._client.send_message(update.chat_id, reply)
                logger.info("replied to chat {} ({} chars)", update.chat_id, len(reply))
            except Exception:
                logger.exception("sendMessage to chat {} failed", update.chat_id)
            offset = update.update_id + 1
        return offset
