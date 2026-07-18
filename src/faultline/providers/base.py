"""Provider protocol: the contract every model adapter must satisfy."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from faultline.schemas import Message, ToolDefinition


class ModelResponse:
    """Normalized response from any model provider."""

    def __init__(
        self,
        message: Message,
        model: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_ms: float = 0.0,
    ) -> None:
        self.message = message
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.latency_ms = latency_ms

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@runtime_checkable
class ModelProvider(Protocol):
    """Interface that OpenAI, Ollama, and fake providers all implement."""

    @property
    def provider_name(self) -> str: ...

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        model: str | None = None,
    ) -> ModelResponse:
        """Send a conversation to the model and return a normalized response."""
        ...
