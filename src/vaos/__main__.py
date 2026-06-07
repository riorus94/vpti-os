"""`python -m vaos` — assemble the runtime graph from config and long-poll Telegram.

Fails fast with a clear message when required config is missing, then hands off to
TelegramBot.run() (the getUpdates loop). This is the production entrypoint; verify
locally with a real bot token + allowlist + LLM key.
"""

import asyncio
import sys

from vaos.app import build_bot
from vaos.config import Settings


def _missing_config(settings: Settings) -> list[str]:
    """Required env vars that are absent, so startup can refuse with a clear list."""
    missing: list[str] = []
    if not settings.telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not settings.allowlist_ids():
        missing.append("TELEGRAM_ALLOWLIST")
    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        missing.append("ANTHROPIC_API_KEY")
    if settings.llm_provider == "azure_openai" and not settings.azure_openai_api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    return missing


async def serve(settings: Settings) -> None:
    bot = build_bot(settings)
    print(
        f"VAOS up — long-polling Telegram (llm={settings.llm_provider}, "
        f"internal_source={settings.internal_source}). Ctrl-C to stop."
    )
    await bot.run()


def main() -> int:
    settings = Settings()
    missing = _missing_config(settings)
    if missing:
        print("Cannot start — missing config: " + ", ".join(missing), file=sys.stderr)
        print("Set them in .env (see .env.example).", file=sys.stderr)
        return 1
    try:
        asyncio.run(serve(settings))
    except KeyboardInterrupt:
        print("\nVAOS stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
