"""Azure OpenAI adapter — the default production LLM (ADR-0007).

The production default governs data residency; swap to the self-hosted adapter
if a 'nothing leaves Indonesia' policy lands.
"""

from vaos.ports.llm import LLMClient


class AzureOpenAILLM(LLMClient):
    def __init__(self, endpoint: str, api_key: str, deployment: str) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._deployment = deployment

    async def complete(self, system: str, prompt: str) -> str:
        raise NotImplementedError("wire azure-openai client")
