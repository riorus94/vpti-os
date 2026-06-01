"""FastAPI entry point + composition root.

This is where adapters are chosen (by config) and injected into the orchestrator
and Telegram bot. Nothing below this file imports a concrete adapter.
"""

from fastapi import FastAPI

from vaos.config import settings

app = FastAPI(title="VAOS", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "llm_provider": settings.llm_provider}


# Composition root (wire adapters -> orchestrator -> TelegramBot) is assembled
# in vaos-mvp/01 once the walking skeleton lands.
