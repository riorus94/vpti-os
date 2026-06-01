"""Telegram bot — long-polling (vaos-mvp/01, ADR-0003).

Enforces the allowlist (rejects unknown user IDs), stamps asker identity onto the
request, drives the infer+confirm handshake, and (Phase 2) the Approver flow.
No conversational memory — only short-lived pending-confirmation state.
"""

from vaos.config import Settings


class TelegramBot:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._allowlist = settings.allowlist_ids()

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self._allowlist

    def run(self) -> None:
        raise NotImplementedError("vaos-mvp/01 — getUpdates long-poll loop")
