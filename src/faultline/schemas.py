"""Core Pydantic schemas for tasks, tool calls, messages, runs, steps, and results.

This module defines the typed data structures that flow through the entire system.
Every trace event, tool interaction, and experiment result is validated here.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CorruptionMode(str, Enum):
    """The four experimental corruption conditions."""

    CLEAN = "clean"
    EXPLICIT_ERROR = "explicit_error"
    MALFORMED = "malformed"
    PLAUSIBLE_WRONG = "plausible_wrong"


class AgentStrategy(str, Enum):
    """The four agent recovery strategies under evaluation."""

    BASELINE = "baseline"
    RETRY = "retry"
    CRITIC = "critic"
    VERIFIER = "verifier"


class TaskDomain(str, Enum):
    """The three synthetic task domains."""

    ORDER_SUPPORT = "order_support"
    SCHEDULING = "scheduling"
    DATA_ANALYSIS = "data_analysis"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------


class ToolDefinition(BaseModel):
    """A synthetic tool available to the agent."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """A tool invocation requested by the model."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    call_id: str = ""


class ToolResult(BaseModel):
    """The output returned to the model after a tool call."""

    call_id: str = ""
    output: Any = None
    error: str | None = None
    corrupted: bool = False
    corruption_mode: CorruptionMode = CorruptionMode.CLEAN


# ---------------------------------------------------------------------------
# Message schemas
# ---------------------------------------------------------------------------


class Message(BaseModel):
    """A single message in the agent conversation."""

    role: str  # "system", "user", "assistant", "tool"
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_result: ToolResult | None = None


# ---------------------------------------------------------------------------
# Task schemas
# ---------------------------------------------------------------------------


class TaskDefinition(BaseModel):
    """A synthetic evaluation task."""

    task_id: str
    domain: TaskDomain
    description: str
    instructions: str
    tools: list[ToolDefinition] = Field(default_factory=list)
    gold_state: dict[str, Any] = Field(default_factory=dict)
    gold_answer: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Run and step schemas
# ---------------------------------------------------------------------------


class StepRecord(BaseModel):
    """A single step within an agent run."""

    step_index: int
    message: Message
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: float = 0.0
    token_usage: dict[str, int] = Field(default_factory=dict)


class RunRecord(BaseModel):
    """A complete agent run for one task under one configuration."""

    run_id: str
    experiment_id: str
    task_id: str
    strategy: AgentStrategy
    corruption_mode: CorruptionMode
    provider: str
    model: str
    trial: int = 1
    status: RunStatus = RunStatus.PENDING
    steps: list[StepRecord] = Field(default_factory=list)
    final_answer: str | None = None
    success: bool | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Experiment schemas
# ---------------------------------------------------------------------------


class ExperimentConfig(BaseModel):
    """Top-level experiment configuration."""

    experiment_id: str
    description: str = ""
    tasks: list[str] = Field(default_factory=list)
    strategies: list[AgentStrategy] = Field(default_factory=list)
    corruption_modes: list[CorruptionMode] = Field(default_factory=list)
    providers: list[str] = Field(default_factory=list)
    trials: int = 5
    concurrency: int = 4
    timeout_seconds: float = 120.0
    metadata: dict[str, Any] = Field(default_factory=dict)
