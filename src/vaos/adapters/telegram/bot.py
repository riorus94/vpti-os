"""Telegram bot — long-polling (vaos-mvp/01, ADR-0003).

Enforces the allowlist (rejects unknown user IDs), stamps asker identity onto the
request, drives the infer+confirm handshake, and (Phase 2) the Approver flow.
No conversational memory — only short-lived pending-confirmation state: at most
one InferredContext per user awaiting yes/no, cleared the moment a request
completes. Nothing carries between completed requests (ADR-0003).

The conversation logic lives in on_message (unit-tested); run() is the thin
getUpdates I/O loop that feeds it and is covered by integration, not unit tests.
"""

from uuid import uuid4

from vaos.config import Settings
from vaos.domain.context import InferredContext
from vaos.modules.context_builder import confirm, infer
from vaos.pipeline.orchestrator import Orchestrator
from vaos.ports.llm import LLMClient

_AFFIRMATIVE = {"ya", "yes", "y", "benar", "betul", "ok", "oke", "lanjut"}
_REJECTION = "Maaf, Anda tidak memiliki akses ke layanan ini."


class TelegramBot:
    def __init__(
        self,
        settings: Settings,
        llm: LLMClient | None = None,
        orchestrator: Orchestrator | None = None,
    ) -> None:
        self._settings = settings
        self._allowlist = settings.allowlist_ids()
        self._llm = llm
        self._orchestrator = orchestrator
        # user_id -> (original query, inferred context awaiting confirmation)
        self._pending: dict[int, tuple[str, InferredContext]] = {}

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self._allowlist

    async def on_message(self, user_id: int, text: str) -> str:
        if not self.is_authorized(user_id):
            return _REJECTION
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

    def run(self) -> None:
        raise NotImplementedError("vaos-mvp/01 — getUpdates long-poll loop")
