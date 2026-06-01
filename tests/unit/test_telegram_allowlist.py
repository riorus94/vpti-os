"""Telegram allowlist auth (#1, ADR-0003). Pure membership check — the only
infra-free part of the Telegram adapter (the long-poll loop is I/O)."""

from vaos.adapters.telegram.bot import TelegramBot
from vaos.config import Settings


def _bot(allowlist: str) -> TelegramBot:
    return TelegramBot(Settings(telegram_allowlist=allowlist))


def test_allowlisted_user_is_authorized() -> None:
    assert _bot("7,8,9").is_authorized(8) is True


def test_unknown_user_is_rejected() -> None:
    assert _bot("7,8,9").is_authorized(42) is False
