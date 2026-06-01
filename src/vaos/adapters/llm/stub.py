"""Deterministic stub LLM for the walking skeleton (vaos-mvp/01) and tests."""

from vaos.ports.llm import LLMClient


class StubLLM(LLMClient):
    def __init__(self, canned: str = "[stub response]") -> None:
        self._canned = canned

    async def complete(self, system: str, prompt: str) -> str:
        return self._canned
