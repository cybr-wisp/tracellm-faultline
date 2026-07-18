"""Tests for the deterministic fake provider."""

import pytest
from faultline.providers.fake import FakeProvider
from faultline.schemas import Message


@pytest.mark.asyncio
async def test_fake_provider_returns_configured_responses() -> None:
    responses = [
        Message(role="assistant", content="First response"),
        Message(role="assistant", content="Second response"),
    ]
    provider = FakeProvider(responses=responses)
    assert provider.provider_name == "fake"

    r1 = await provider.complete(messages=[Message(role="user", content="hello")])
    assert r1.message.content == "First response"

    r2 = await provider.complete(messages=[Message(role="user", content="again")])
    assert r2.message.content == "Second response"


@pytest.mark.asyncio
async def test_fake_provider_exhausted() -> None:
    provider = FakeProvider(responses=[])
    r = await provider.complete(messages=[Message(role="user", content="hello")])
    assert "No more responses" in (r.message.content or "")
