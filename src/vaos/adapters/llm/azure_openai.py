"""Azure OpenAI adapter — the default production LLM (ADR-0007).

The production default governs data residency; swap to the self-hosted adapter
if a 'nothing leaves Indonesia' policy lands. Transport/HTTP failures surface as
LLMError so callers degrade on one typed failure rather than a raw httpx error.
"""

import httpx

from vaos.ports.llm import LLMClient, LLMError

# Pinned GA chat-completions API version (override only when intentionally upgrading).
_API_VERSION = "2024-10-21"


class AzureOpenAILLM(LLMClient):
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._deployment = deployment
        self._client = client or httpx.AsyncClient(timeout=30.0)

    async def complete(self, system: str, prompt: str) -> str:
        url = f"{self._endpoint}/openai/deployments/{self._deployment}/chat/completions"
        try:
            response = await self._client.post(
                url,
                params={"api-version": _API_VERSION},
                headers={"api-key": self._api_key},
                json={
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ]
                },
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise LLMError(f"Azure OpenAI request failed: {exc}") from exc

        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"unexpected Azure OpenAI response shape: {data!r}") from exc
