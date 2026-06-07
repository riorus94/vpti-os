"""Anthropic Claude adapter for the LLMClient port (ADR-0007).

Uses the official anthropic SDK (AsyncAnthropic). Defaults to claude-opus-4-8 —
the most capable model; switch to a cheaper model via the `model` arg / config if
desired. API/transport failures and empty responses surface as LLMError so callers
degrade on one typed failure rather than a raw SDK exception.

The port is a plain text-completion seam, so this adapter does not enable adaptive
thinking; per-call reasoning depth is a future refinement above the port.
"""

import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import TextBlock

from vaos.ports.llm import LLMClient, LLMError

_MAX_TOKENS = 16000


class AnthropicLLM(LLMClient):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-8",
        client: AsyncAnthropic | None = None,
    ) -> None:
        self._model = model
        self._client = client or AsyncAnthropic(api_key=api_key)

    async def complete(self, system: str, prompt: str) -> str:
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=_MAX_TOKENS,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            raise LLMError(f"Anthropic request failed: {exc}") from exc

        text = "".join(b.text for b in message.content if isinstance(b, TextBlock))
        if not text:
            raise LLMError(f"no text block in Anthropic response: {message.content!r}")
        return text
