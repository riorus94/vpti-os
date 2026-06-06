"""Azure OpenAI LLMClient adapter (#18, ADR-0007). Mocked transport — no network.

Pins the request shape (deployment in the path, api-key header, system+user
messages) and the failure contract (HTTP/transport error -> typed LLMError)."""

import json

import httpx
import pytest

from vaos.adapters.llm.azure_openai import _API_VERSION, AzureOpenAILLM
from vaos.ports.llm import LLMError


def _llm(handler: object) -> AzureOpenAILLM:
    transport = httpx.MockTransport(handler)  # type: ignore[arg-type]
    return AzureOpenAILLM(
        endpoint="https://example.openai.azure.com/",
        api_key="secret",
        deployment="gpt-4o",
        client=httpx.AsyncClient(transport=transport),
    )


async def test_complete_posts_chat_request_and_returns_assistant_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert "/openai/deployments/gpt-4o/chat/completions" in str(request.url)
        assert request.url.params["api-version"] == _API_VERSION
        assert request.headers["api-key"] == "secret"
        body = json.loads(request.content)
        assert [m["role"] for m in body["messages"]] == ["system", "user"]
        assert body["messages"][1]["content"] == "wajib LS?"
        return httpx.Response(200, json={"choices": [{"message": {"content": "Ya, wajib."}}]})

    out = await _llm(handler).complete(system="Kamu asisten VPTI.", prompt="wajib LS?")
    assert out == "Ya, wajib."


async def test_http_error_is_wrapped_in_llm_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    with pytest.raises(LLMError):
        await _llm(handler).complete(system="s", prompt="p")
