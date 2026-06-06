"""FastAPI entry point + composition root.

This is where adapters are chosen (by config) and injected into the orchestrator
and Telegram bot. Nothing below this file imports a concrete adapter.
"""

from fastapi import FastAPI

from vaos.adapters.llm.azure_openai import AzureOpenAILLM
from vaos.adapters.llm.stub import StubLLM
from vaos.adapters.retrieval.stub import EmptyInternalSource, EmptyRegulationSource
from vaos.adapters.store.memory import InMemoryStore
from vaos.adapters.telegram.bot import TelegramBot
from vaos.config import Settings, settings
from vaos.modules.retrieval.router import RetrievalRouter
from vaos.pipeline.orchestrator import Orchestrator
from vaos.ports.llm import LLMClient
from vaos.ports.store import Store

app = FastAPI(title="VAOS", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "llm_provider": settings.llm_provider}


def _build_llm(settings: Settings) -> LLMClient:
    """Choose the LLM adapter by config — the only place a provider is named."""
    if settings.llm_provider == "azure_openai":
        return AzureOpenAILLM(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            deployment=settings.azure_openai_deployment,
        )
    if settings.llm_provider == "stub":
        return StubLLM()
    raise ValueError(f"unknown llm_provider: {settings.llm_provider!r}")


def build_bot(
    settings: Settings,
    *,
    llm: LLMClient | None = None,
    store: Store | None = None,
) -> TelegramBot:
    """Composition root: assemble Settings -> LLM -> RetrievalRouter -> Store ->
    Orchestrator -> TelegramBot. Wiring only — no business logic lives here.

    The retrieval legs are the interim empty sources; vaos-mvp/05 (PasalIdClient)
    and vaos-mvp/04 (FaissVault) swap in the real adapters. The store is in-memory
    until vaos-mvp/09 wires Postgres. llm/store are overridable for tests.
    """
    llm = llm or _build_llm(settings)
    store = store or InMemoryStore()
    router = RetrievalRouter(regs=EmptyRegulationSource(), vault=EmptyInternalSource())
    orchestrator = Orchestrator(llm=llm, store=store, router=router)
    return TelegramBot(settings, llm=llm, orchestrator=orchestrator)
