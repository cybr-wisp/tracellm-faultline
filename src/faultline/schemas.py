
"""Core Pydantic schemas for tasks, tool calls, messages, runs, steps, and results.

This module defines the typed data structures that flow through the entire system.
Every trace event, tool interaction, and experiment result is validated here.

The schemas support the core research question:

    What are the break-even conditions under which tool-output verification
    becomes cost-negative for LLM agents, how do these conditions vary across
    output conditions, and how closely can a signal-based adaptive policy
    track the oracle-optimal verification frontier?

Key concepts encoded here:
  - CostModel: three-part cost decomposition C_total = C_tokens + E[Damage_missed] + E[Damage_flipped]
  - RecoveryRecord: four-part recovery (detection, corrective action, success, informed correctness)
  - VerificationDecision: per-step record of what the agent chose to do and why
  - OracleAction: what a perfect-information agent would have done
  - RegretRecord: the gap between actual and oracle-optimal cost at each C_e level
  - AgentStrategy.ADAPTIVE: a policy π(x) that decides per-step whether to verify
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OutputCondition(str, Enum):
    """The four experimental output conditions.
    
    Called 'output conditions' not 'corruption types' because
    Clean is one of the four conditions but is not corruption.
    """

    CLEAN = "clean"
    EXPLICIT_ERROR = "explicit_error"
    MALFORMED = "malformed"
    PLAUSIBLE_WRONG = "plausible_wrong"


class AgentStrategy(str, Enum):
    """The five agent verification strategies under evaluation.

    The first four are static (always apply the same policy).
    ADAPTIVE decides per-step based on observable corruption signals.
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


class VerificationAction(str, Enum):
    """What the agent decided to do at a verification decision point."""

    PASS = "pass"              # Trust the tool output, no verification
    RETRY = "retry"            # Call the tool again
    INVOKE_CRITIC = "critic"   # Ask a critic LLM to evaluate
    INVOKE_VERIFIER = "verify" # Ask a verifier LLM to check constraints
    SKIP = "skip"              # No verification decision was made (baseline)


# ---------------------------------------------------------------------------
# Cost model
# ---------------------------------------------------------------------------


class CostModel(BaseModel):
    """Three-part cost decomposition for the Faultline framework.

    C_total(S) = C_tokens(S) + E[Damage_missed] + E[Damage_flipped]

    Error cost C_e is NOT fixed — it is swept across multiple values
    during post-hoc analysis to produce break-even crossover charts.
    Total cost is computed during analysis, not at runtime.
    """

    # Token pricing (per 1K tokens)
    input_token_cost_per_1k: float = 0.005
    output_token_cost_per_1k: float = 0.015

    # Error cost sweep values (token equivalents) for break-even analysis
    error_cost_sweep: list[float] = Field(
        default_factory=lambda: [100.0, 500.0, 1000.0, 2500.0, 5000.0],
        description="Downstream error cost C_e values for parameterized sweep.",
    )

    def token_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Compute dollar cost of token usage (C_tokens component)."""
        return (
            (input_tokens / 1000) * self.input_token_cost_per_1k
            + (output_tokens / 1000) * self.output_token_cost_per_1k
        )


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
    output_condition: OutputCondition = OutputCondition.CLEAN


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
    """A synthetic evaluation task with gold outputs and corruption variants."""

    task_id: str
    domain: TaskDomain
    description: str
    instructions: str
    tools: list[ToolDefinition] = Field(default_factory=list)
    gold_tool_output: dict[str, Any] = Field(
        default_factory=dict,
        description="The correct tool response. Used for oracle computation.",
    )
    gold_answer: str | None = None
    gold_state: dict[str, Any] = Field(default_factory=dict)
    corruption_variants: dict[str, Any] = Field(
        default_factory=dict,
        description="Pre-defined corrupted outputs keyed by OutputCondition value.",
    )
    success_criteria: dict[str, Any] = Field(
        default_factory=dict,
        description="Key fields to check, match types (exact, tolerance, set_equality), thresholds.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Verification decision record
# ---------------------------------------------------------------------------


class VerificationDecision(BaseModel):
    """Records what the agent chose to do at each decision point and why.

    For static strategies, action is predetermined.
    For ADAPTIVE, the agent selects based on observable corruption signals.
    """

    step_index: int
    action: VerificationAction
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Agent's confidence in the tool output (0=suspicious, 1=trusted).",
    )
    signals: dict[str, Any] = Field(
        default_factory=dict,
        description="Observable features the adaptive policy π(x) used to decide.",
    )
    action_token_cost: int = 0
    action_latency_ms: float = 0.0


# ---------------------------------------------------------------------------
# Recovery record
# ---------------------------------------------------------------------------


class RecoveryRecord(BaseModel):
    """Four-part recovery assessment. All four must be true for full recovery.

    Prevents rewarding lucky guesses or parametric knowledge bypass.
    """

    detection: bool = False
    corrective_action: bool = False
    task_success: bool = False
    informed_correctness: bool = False

    @property
    def full_recovery(self) -> bool:
        """True only if all four conditions are met."""
        return (
            self.detection
            and self.corrective_action
            and self.task_success
            and self.informed_correctness
        )


# ---------------------------------------------------------------------------
# Oracle and regret
# ---------------------------------------------------------------------------


class OracleAction(BaseModel):
    """What a perfect-information agent would have done at this step.

    Computed post-hoc from labeled data.
    Clean output → Pass (no verification).
    Corrupted output → cheapest effective tier (Retry, Critic, or Verifier).
    """

    step_index: int
    optimal_action: VerificationAction
    optimal_token_cost: float = 0.0
    reasoning: str = ""


class RegretRecord(BaseModel):
    """The gap between actual cost and oracle-optimal cost.

    R(S) = C_total(S) - C_total(S*) >= 0

    Computed per error-cost level during post-hoc analysis.
    Each entry in cost_by_error_level maps a C_e value to its
    actual cost, oracle cost, regret, and price of uncertainty.
    """

    run_id: str
    actual_decisions: list[VerificationDecision] = Field(default_factory=list)
    oracle_decisions: list[OracleAction] = Field(default_factory=list)
    cost_by_error_level: dict[str, Any] = Field(
        default_factory=dict,
        description="Keyed by C_e value. Each contains actual_cost, oracle_cost, regret, pou.",
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
    output_condition: OutputCondition
    provider: str
    model: str
    trial: int = 1
    status: RunStatus = RunStatus.PENDING
    steps: list[StepRecord] = Field(default_factory=list)
    final_answer: str | None = None
    # --- Outcome assessment ---
    success: bool | None = None
    answer_flipped: bool = False
    recovery: RecoveryRecord | None = None
    # --- Cost accounting (runtime, not post-hoc) ---
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_tokens: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: float = 0.0
    total_token_cost: float = 0.0
    # --- Oracle comparison (computed post-hoc) ---
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
        "What are the break-even conditions under which tool-output "
        "verification becomes cost-negative for LLM agents, how do these "
        "conditions vary across output conditions, and how closely can a "
        "signal-based adaptive policy track the oracle-optimal verification frontier?"
    )
    tasks: list[str] = Field(default_factory=list)
    strategies: list[AgentStrategy] = Field(default_factory=list)
    output_conditions: list[OutputCondition] = Field(default_factory=list)
    providers: list[str] = Field(default_factory=list)
    cost_model: CostModel = Field(default_factory=CostModel)
    trials: int = 5
    concurrency: int = 4
    timeout_seconds: float = 120.0
    metadata: dict[str, Any] = Field(default_factory=dict)