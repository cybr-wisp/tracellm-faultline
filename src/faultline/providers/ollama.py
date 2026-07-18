"""Ollama local model provider adapter.

TODO (Day 9): Implement local model calls, structured output, and tool-call normalization.
"""

from __future__ import annotations

from faultline.providers.base import ModelResponse
from faultline.schemas import Message, ToolDefinition


class OllamaProvider:
    """Adapter for locally hosted models via Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.1") -> None:
        self._base_url = base_url
        self._default_model = default_model

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        model: str | None = None,
    ) -> ModelResponse:
        raise NotImplementedError("Ollama provider not yet implemented — see Day 9")
