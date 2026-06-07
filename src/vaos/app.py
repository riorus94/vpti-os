"""FastAPI entry point + composition root.

This is where adapters are chosen (by config) and injected into the orchestrator
and Telegram bot. Nothing below this file imports a concrete adapter.
"""

from fastapi import FastAPI

from vaos.adapters.llm.anthropic_claude import AnthropicLLM
from vaos.adapters.llm.azure_openai import AzureOpenAILLM
from vaos.adapters.llm.stub import StubLLM
from vaos.adapters.retrieval.stub import EmptyInternalSource, EmptyRegulationSource
from vaos.adapters.store.memory import InMemoryStore
from vaos.adapters.telegram.bot import TelegramBot
from vaos.config import Settings, settings
from vaos.modules.retrieval.router import RetrievalRouter
from vaos.pipeline.orchestrator import Orchestrator
from vaos.ports.llm import LLMClient
from vaos.ports.retrieval import InternalSource
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
    if settings.llm_provider == "anthropic":
        return AnthropicLLM(api_key=settings.anthropic_api_key, model=settings.anthropic_model)
    if settings.llm_provider == "stub":
        return StubLLM()
    raise ValueError(f"unknown llm_provider: {settings.llm_provider!r}")


def _build_internal_source(settings: Settings) -> InternalSource:
    """Choose the internal (Vault) retrieval leg. FAISS + e5 are imported lazily so
    the base app stays runnable without the optional [rag] dependencies installed."""
    if settings.internal_source == "empty":
        return EmptyInternalSource()
    if settings.internal_source == "faiss":
        from vaos.adapters.embeddings.multilingual_e5 import MultilingualE5Embedder
        from vaos.modules.retrieval.faiss_vault import FaissVault

        embedder = MultilingualE5Embedder(settings.embedding_model)
        return FaissVault(embedder, settings.faiss_index_path)
    raise ValueError(f"unknown internal_source: {settings.internal_source!r}")


def build_bot(
    settings: Settings,
    *,
    llm: LLMClient | None = None,
    store: Store | None = None,
) -> TelegramBot:
    """Composition root: assemble Settings -> LLM -> RetrievalRouter -> Store ->
    Orchestrator -> TelegramBot. Wiring only — no business logic lives here.

    The internal (Vault) leg is config-selected (empty | faiss); the regulation leg
    stays the interim empty source until vaos-mvp/05 (PasalIdClient). The store is
    in-memory until vaos-mvp/09 wires Postgres. llm/store are overridable for tests.
    """
    llm = llm or _build_llm(settings)
    store = store or InMemoryStore()
    router = RetrievalRouter(regs=EmptyRegulationSource(), vault=_build_internal_source(settings))
    orchestrator = Orchestrator(llm=llm, store=store, router=router)
    return TelegramBot(settings, llm=llm, orchestrator=orchestrator)
