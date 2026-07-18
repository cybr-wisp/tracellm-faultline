"""OpenAI API provider adapter.

TODO (Day 8): Implement API calls, structured output, and tool-call normalization.
"""

from __future__ import annotations

from faultline.providers.base import ModelResponse
from faultline.schemas import Message, ToolDefinition


class OpenAIProvider:
    """Adapter for the OpenAI chat completions API."""

    def __init__(self, api_key: str | None = None, default_model: str = "gpt-4o") -> None:
        self._api_key = api_key
        self._default_model = default_model

    @property
    def provider_name(self) -> str:
        return "openai"

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        model: str | None = None,
    ) -> ModelResponse:
        raise NotImplementedError("OpenAI provider not yet implemented — see Day 8")
