"""Trace event schema — append-only event log for full run reconstruction.

TODO (Day 13–14): Implement span hierarchy, parent-child relationships, and instrumentation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TraceEventType(str, Enum):
    MODEL_REQUEST = "model_request"
    MODEL_RESPONSE = "model_response"
    TOOL_REQUEST = "tool_request"
    TOOL_RESULT = "tool_result"
    CORRUPTION_INJECTED = "corruption_injected"
    ERROR = "error"
    RETRY = "retry"
    FINAL_ANSWER = "final_answer"


class TraceEvent(BaseModel):
    """A single event in the execution trace."""

    event_id: str
    run_id: str
    event_type: TraceEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parent_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
