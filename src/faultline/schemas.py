"""Core Pydantic schemas for tasks, tool calls, messages, runs, steps, and results.

This module defines the typed data structures that flow through the entire system.
Every trace event, tool interaction, and experiment result is validated here.

The schemas support the core research question:

    Can a corruption-aware agent learn an adaptive verification policy that
    minimizes expected total cost (token spend + error cost) across heterogeneous
    failure modes, and how close does this policy come to the oracle-optimal strategy?

Key concepts encoded here:
  - CostModel: assigns real dollar costs to token usage and error severity
  - ErrorSeverity: graduated error impact (not just binary success/failure)
  - VerificationDecision: per-step record of what the agent chose to do and why
  - OracleAction: what a perfect-information agent would have done
  - RegretRecord: the gap between actual and oracle-optimal cost
  - AgentStrategy.ADAPTIVE: a policy that decides per-step whether to verify
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
    """The five agent recovery strategies under evaluation.

    The first four are static (always apply the same policy).
    ADAPTIVE decides per-step based on corruption signals.
    """

    BASELINE = "baseline"
    RETRY = "retry"
    CRITIC = "critic"
    VERIFIER = "verifier"
    ADAPTIVE = "adaptive"


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


class ErrorSeverity(str, Enum):
    """Graduated error impact — drives the cost model.

    NONE:     Correct answer, no error.
    MINOR:    Small inaccuracy, unlikely to cause downstream harm.
    MODERATE: Wrong answer that would require human correction.
    SEVERE:   Wrong answer that could cause material downstream damage.
    CRITICAL: Confidently wrong answer propagated without any detection.
    """

    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class VerificationAction(str, Enum):
    """What the agent decided to do at a verification decision point."""

    ACCEPT = "accept"          # Trust the tool output, move on
    RETRY = "retry"            # Call the tool again
    INVOKE_CRITIC = "critic"   # Ask a critic LLM to evaluate
    INVOKE_VERIFIER = "verify" # Ask a verifier LLM to check the final answer
    SKIP = "skip"              # No verification decision was made (baseline)


# ---------------------------------------------------------------------------
# Cost model
# ---------------------------------------------------------------------------


class CostModel(BaseModel):
    """Assigns real costs to tokens and errors.

    This is what transforms the evaluation from descriptive measurement
    into a decision-optimization problem. The oracle strategy is computed
    by minimizing total_cost = token_cost + error_cost.
    """

    # Token pricing (per 1K tokens)
    input_token_cost_per_1k: float = 0.005
    output_token_cost_per_1k: float = 0.015

    # Error severity costs (domain-configurable)
    error_costs: dict[str, float] = Field(default_factory=lambda: {
        "none": 0.0,
        "minor": 0.10,
        "moderate": 1.00,
        "severe": 5.00,
        "critical": 25.00,
    })

    # Verification action costs (beyond base token cost)
    verification_overhead: dict[str, float] = Field(default_factory=lambda: {
        "accept": 0.0,
        "retry": 0.0,       # Token cost captured separately
        "critic": 0.0,      # Token cost captured separately
        "verify": 0.0,      # Token cost captured separately
        "skip": 0.0,
    })

    def token_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Compute dollar cost of token usage."""
        return (
            (input_tokens / 1000) * self.input_token_cost_per_1k
            + (output_tokens / 1000) * self.output_token_cost_per_1k
        )

    def error_cost(self, severity: ErrorSeverity) -> float:
        """Compute dollar cost of an error at the given severity."""
        return self.error_costs.get(severity.value, 0.0)

    def total_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        severity: ErrorSeverity,
    ) -> float:
        """Total cost = token spend + error damage."""
        return self.token_cost(input_tokens, output_tokens) + self.error_cost(severity)


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
    error_severity_map: dict[str, ErrorSeverity] = Field(
        default_factory=dict,
        description="Maps failure mode descriptions to severity levels for cost computation.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Verification decision record
# ---------------------------------------------------------------------------


class VerificationDecision(BaseModel):
    """Records what the agent chose to do at each decision point and why.

    For static strategies, action is predetermined.
    For ADAPTIVE, the agent selects based on corruption signals.
    """

    step_index: int
    action: VerificationAction
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Agent's self-reported confidence in the tool output (0=suspicious, 1=trusted).",
    )
    signals: dict[str, Any] = Field(
        default_factory=dict,
        description="Features the adaptive policy used to decide (output entropy, format checks, etc).",
    )
    action_token_cost: int = 0
    action_latency_ms: float = 0.0


# ---------------------------------------------------------------------------
# Oracle and regret
# ---------------------------------------------------------------------------


class OracleAction(BaseModel):
    """What a perfect-information agent would have done at this step.

    Computed post-hoc from labeled data. If the tool output was corrupted,
    the oracle always verifies. If clean, the oracle always accepts.
    The oracle uses the cheapest effective verification method.
    """

    step_index: int
    optimal_action: VerificationAction
    optimal_cost: float = 0.0
    reasoning: str = ""


class RegretRecord(BaseModel):
    """The gap between what the agent actually spent and what the oracle would have spent.

    regret = actual_total_cost - oracle_total_cost

    Positive regret means the agent wasted resources or missed an error.
    Zero regret means the agent matched the oracle exactly.
    Negative regret is impossible by definition (oracle is optimal).
    """

    run_id: str
    actual_total_cost: float = 0.0
    oracle_total_cost: float = 0.0
    regret: float = 0.0
    actual_decisions: list[VerificationDecision] = Field(default_factory=list)
    oracle_decisions: list[OracleAction] = Field(default_factory=list)
    price_of_uncertainty: float = Field(
        default=0.0,
        description="regret / oracle_total_cost — the fractional cost of not knowing.",
    )


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
    verification: VerificationDecision | None = None


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
    # --- Outcome assessment ---
    success: bool | None = None
    error_severity: ErrorSeverity = ErrorSeverity.NONE
    # --- Cost accounting ---
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_tokens: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: float = 0.0
    total_token_cost: float = 0.0
    total_error_cost: float = 0.0
    total_cost: float = 0.0
    # --- Oracle comparison ---
    regret: RegretRecord | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Experiment schemas
# ---------------------------------------------------------------------------


class ExperimentConfig(BaseModel):
    """Top-level experiment configuration."""

    experiment_id: str
    description: str = ""
    research_question: str = (
        "Can a corruption-aware agent learn an adaptive verification policy "
        "that minimizes expected total cost (token spend + error cost) across "
        "heterogeneous failure modes, and how close does this policy come to "
        "the oracle-optimal strategy?"
    )
    tasks: list[str] = Field(default_factory=list)
    strategies: list[AgentStrategy] = Field(default_factory=list)
    corruption_modes: list[CorruptionMode] = Field(default_factory=list)
    providers: list[str] = Field(default_factory=list)
    cost_model: CostModel = Field(default_factory=CostModel)
    trials: int = 5
    concurrency: int = 4
    timeout_seconds: float = 120.0
    metadata: dict[str, Any] = Field(default_factory=dict)
