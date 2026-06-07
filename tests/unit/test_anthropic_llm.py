"""Anthropic Claude LLMClient adapter (ADR-0007). The SDK client is faked — no
network, no key — to pin the request shape (model, system, user message) and the
failure contract (anthropic.APIError -> typed LLMError)."""

from types import SimpleNamespace
from typing import Any

import anthropic
import httpx
import pytest
from anthropic.types import TextBlock

from vaos.adapters.llm.anthropic_claude import AnthropicLLM
from vaos.ports.llm import LLMError


class _Messages:
    def __init__(self, content: list[Any] | None, error: Exception | None) -> None:
        self._content, self._error = content, error
        self.captured: dict[str, Any] = {}

    async def create(self, **kwargs: Any) -> Any:
        self.captured.update(kwargs)
        if self._error is not None:
            raise self._error
        return SimpleNamespace(content=self._content)


class FakeClient:
    def __init__(self, content: list[Any] | None = None, error: Exception | None = None) -> None:
        self.messages = _Messages(content, error)


async def test_complete_sends_system_and_user_message_and_returns_text() -> None:
    client = FakeClient(content=[TextBlock(type="text", text="Ya, wajib LS.", citations=None)])
    llm = AnthropicLLM(api_key="k", model="claude-opus-4-8", client=client)

    out = await llm.complete(system="Kamu asisten VPTI.", prompt="wajib LS?")

    assert out == "Ya, wajib LS."
    assert client.messages.captured["model"] == "claude-opus-4-8"
    assert client.messages.captured["system"] == "Kamu asisten VPTI."
    assert client.messages.captured["messages"] == [{"role": "user", "content": "wajib LS?"}]


async def test_api_error_is_wrapped_in_llm_error() -> None:
    boom = anthropic.APIConnectionError(request=httpx.Request("POST", "https://api.anthropic.com"))
    llm = AnthropicLLM(api_key="k", client=FakeClient(error=boom))

    with pytest.raises(LLMError):
        await llm.complete(system="s", prompt="p")


async def test_response_without_text_block_raises_llm_error() -> None:
    llm = AnthropicLLM(api_key="k", client=FakeClient(content=[]))

    with pytest.raises(LLMError):
        await llm.complete(system="s", prompt="p")
