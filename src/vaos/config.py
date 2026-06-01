"""Typed settings loaded from environment / .env (see .env.example).

Centralizes all config so adapters never read os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Telegram (ADR-0003)
    telegram_bot_token: str = ""
    telegram_allowlist: str = ""      # comma-separated user IDs
    telegram_approvers: str = ""      # comma-separated subset (ADR-0008)

    # LLM (modular port; Azure default — ADR-0007)
    llm_provider: str = "azure_openai"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""

    # Embeddings (local, on-prem — ADR-0007)
    embedding_model: str = "intfloat/multilingual-e5-large"

    # Retrieval (ADR-0002)
    pasal_id_base_url: str = ""
    vault_path: str = "./vault"
    faiss_index_path: str = "./data/index/vault.faiss"

    # Web search (never compliance)
    tavily_api_key: str = ""

    # Persistence (vaos-mvp/09)
    database_url: str = "postgresql+psycopg://localhost/vaos"

    # Execution (Phase 2 — ADR-0008)
    linear_api_key: str = ""

    def allowlist_ids(self) -> set[int]:
        return {int(x) for x in self.telegram_allowlist.split(",") if x.strip()}

    def approver_ids(self) -> set[int]:
        return {int(x) for x in self.telegram_approvers.split(",") if x.strip()}


settings = Settings()
