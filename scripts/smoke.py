"""Smoke-test the real LLM + pipeline without Telegram.

Reads .env, calls Claude for real (billed), and drives one query through the
in-process pipeline via on_message. Run:  .venv/bin/python -m scripts.smoke

Needs ANTHROPIC_API_KEY in .env (LLM_PROVIDER=anthropic). No Telegram token or
running entrypoint required — this is the cheapest way to confirm Claude works.
"""

import asyncio

from vaos.app import _build_llm, build_bot
from vaos.config import Settings


async def main() -> None:
    settings = Settings(telegram_allowlist="1")  # allow our fake test user (id 1)

    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        print("⚠  Set ANTHROPIC_API_KEY in .env first (LLM_PROVIDER=anthropic).")
        return

    llm = _build_llm(settings)

    # 1) Adapter talks to Claude at all.
    print("[1] raw LLM →", await llm.complete("Jawab sangat singkat.", "Balas dengan: OK"))

    # 2) Full pipeline via on_message (infer → confirm → handle), real Claude inference.
    bot = build_bot(settings, llm=llm)
    query = "apakah ban truk wajib VPTI?"
    print("[2a] infer  →", await bot.on_message(user_id=1, text=query))
    print("[2b] reply  →", await bot.on_message(user_id=1, text="ya"))
    # Note: with INTERNAL_SOURCE=empty and no pasal-id wired, [2b] correctly REFUSES
    # for lack of grounding — that proves classify→retrieve→reason→reply all ran.


if __name__ == "__main__":
    asyncio.run(main())
