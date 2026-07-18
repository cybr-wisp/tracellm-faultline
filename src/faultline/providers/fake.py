"""Deterministic fake provider for testing and development."""

from __future__ import annotations

from faultline.providers.base import ModelResponse
from faultline.schemas import Message, ToolDefinition


class FakeProvider:
    """Returns predetermined responses. Used for unit tests and offline development."""

    def __init__(self, responses: list[Message] | None = None) -> None:
        self._responses = list(responses or [])
        self._call_index = 0

    @property
    def provider_name(self) -> str:
        return "fake"

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        model: str | None = None,
    ) -> ModelResponse:
        if self._call_index < len(self._responses):
            message = self._responses[self._call_index]
        else:
            message = Message(role="assistant", content="[fake] No more responses configured.")
        self._call_index += 1
        return ModelResponse(
            message=message,
            model="fake-model",
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=0.0,
        )
