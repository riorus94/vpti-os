"""LLMClient port — provider-agnostic (ADR-0007).

Adapters: adapters/llm/azure_openai.py (default), .../stub.py (tests),
optionally an OpenAI or self-hosted adapter. The production default governs
data residency regardless of modularity.
"""

from typing import Protocol


class LLMError(RuntimeError):
    """The LLM provider was unreachable or returned an unusable response. Adapters
    raise this instead of leaking transport-specific exceptions, so callers can
    degrade on a single typed failure (mirrors the retrieval port's contract)."""


class LLMClient(Protocol):
    async def complete(self, system: str, prompt: str) -> str: ...
