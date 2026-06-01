"""LLMClient port — provider-agnostic (ADR-0007).

Adapters: adapters/llm/azure_openai.py (default), .../stub.py (tests),
optionally an OpenAI or self-hosted adapter. The production default governs
data residency regardless of modularity.
"""

from typing import Protocol


class LLMClient(Protocol):
    async def complete(self, system: str, prompt: str) -> str: ...
