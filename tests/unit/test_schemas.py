"""Tests for core Pydantic schemas."""

from faultline.schemas import (
    AgentStrategy,
    CostModel,
    CorruptionMode,
    ErrorSeverity,
    ExperimentConfig,
    Message,
    OracleAction,
    RegretRecord,
    RunRecord,
    RunStatus,
    TaskDefinition,
    TaskDomain,
    ToolCall,
    ToolResult,
    VerificationAction,
    VerificationDecision,
)


# ---------------------------------------------------------------------------
# Original schema tests
# ---------------------------------------------------------------------------


def test_tool_call_creation() -> None:
    tc = ToolCall(tool_name="lookup_order", arguments={"order_id": "ORD-123"}, call_id="call_1")
    assert tc.tool_name == "lookup_order"
    assert tc.arguments["order_id"] == "ORD-123"


def test_tool_result_defaults_to_clean() -> None:
    tr = ToolResult(output={"status": "shipped"})
    assert tr.corrupted is False
    assert tr.corruption_mode == CorruptionMode.CLEAN


def test_message_with_tool_calls() -> None:
    msg = Message(
        role="assistant",
        tool_calls=[ToolCall(tool_name="get_schedule", arguments={"date": "2026-01-15"})],
    )
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0].tool_name == "get_schedule"


def test_task_definition() -> None:
    task = TaskDefinition(
        task_id="order-001",
        domain=TaskDomain.ORDER_SUPPORT,
        description="Look up order status and report to user.",
        instructions="Use the lookup_order tool to find the order, then summarize.",
        gold_answer="Order ORD-123 was shipped on Jan 10.",
    )
    assert task.domain == TaskDomain.ORDER_SUPPORT


def test_run_record_defaults() -> None:
    run = RunRecord(
        run_id="run-001",
        experiment_id="exp-001",
        task_id="order-001",
        strategy=AgentStrategy.BASELINE,
        corruption_mode=CorruptionMode.CLEAN,
        provider="fake",
        model="fake-model",
    )
    assert run.status == RunStatus.PENDING
    assert run.steps == []
    assert run.total_tokens == 0
    assert run.error_severity == ErrorSeverity.NONE
    assert run.total_cost == 0.0
    assert run.regret is None


def test_experiment_config() -> None:
    cfg = ExperimentConfig(
        experiment_id="smoke-001",
        tasks=["order-001", "sched-001"],
        strategies=[AgentStrategy.BASELINE, AgentStrategy.RETRY],
        corruption_modes=[CorruptionMode.CLEAN, CorruptionMode.EXPLICIT_ERROR],
        providers=["fake"],
        trials=3,
    )
    assert len(cfg.strategies) == 2
    assert cfg.trials == 3
    assert "oracle-optimal" in cfg.research_question


# ---------------------------------------------------------------------------
# Cost model tests
# ---------------------------------------------------------------------------


def test_cost_model_token_cost() -> None:
    cm = CostModel(input_token_cost_per_1k=0.01, output_token_cost_per_1k=0.03)
    cost = cm.token_cost(input_tokens=1000, output_tokens=500)
    assert cost == 0.01 + (500 / 1000) * 0.03  # 0.01 + 0.015 = 0.025


def test_cost_model_error_cost() -> None:
    cm = CostModel()
    assert cm.error_cost(ErrorSeverity.NONE) == 0.0
    assert cm.error_cost(ErrorSeverity.CRITICAL) == 25.0


def test_cost_model_total_cost() -> None:
    cm = CostModel(input_token_cost_per_1k=0.01, output_token_cost_per_1k=0.03)
    total = cm.total_cost(
        input_tokens=2000,
        output_tokens=1000,
        severity=ErrorSeverity.MODERATE,
    )
    token_part = (2000 / 1000) * 0.01 + (1000 / 1000) * 0.03  # 0.02 + 0.03 = 0.05
    error_part = 1.00  # moderate default
    assert total == token_part + error_part


# ---------------------------------------------------------------------------
# Adaptive strategy and verification decision tests
# ---------------------------------------------------------------------------


def test_adaptive_strategy_exists() -> None:
    assert AgentStrategy.ADAPTIVE == "adaptive"


def test_verification_decision() -> None:
    vd = VerificationDecision(
        step_index=0,
        action=VerificationAction.INVOKE_CRITIC,
        confidence=0.3,
        signals={"output_entropy": 2.7, "format_valid": True},
        action_token_cost=150,
    )
    assert vd.confidence == 0.3
    assert vd.signals["output_entropy"] == 2.7


def test_verification_decision_confidence_bounds() -> None:
    """Confidence must be between 0 and 1."""
    import pytest
    with pytest.raises(Exception):
        VerificationDecision(step_index=0, action=VerificationAction.ACCEPT, confidence=1.5)


# ---------------------------------------------------------------------------
# Oracle and regret tests
# ---------------------------------------------------------------------------


def test_oracle_action() -> None:
    oa = OracleAction(
        step_index=0,
        optimal_action=VerificationAction.RETRY,
        optimal_cost=0.02,
        reasoning="Tool output was corrupted; cheapest fix is a single retry.",
    )
    assert oa.optimal_action == VerificationAction.RETRY


def test_regret_record() -> None:
    rr = RegretRecord(
        run_id="run-001",
        actual_total_cost=1.50,
        oracle_total_cost=0.30,
        regret=1.20,
        price_of_uncertainty=4.0,  # 1.20 / 0.30
    )
    assert rr.regret == rr.actual_total_cost - rr.oracle_total_cost
    assert rr.price_of_uncertainty == 4.0


def test_regret_is_non_negative_by_convention() -> None:
    """Oracle is optimal, so regret should never be negative in practice."""
    rr = RegretRecord(run_id="run-002", actual_total_cost=0.50, oracle_total_cost=0.50, regret=0.0)
    assert rr.regret >= 0


# ---------------------------------------------------------------------------
# Run record with cost fields
# ---------------------------------------------------------------------------


def test_run_record_cost_fields() -> None:
    run = RunRecord(
        run_id="run-cost-001",
        experiment_id="exp-001",
        task_id="order-001",
        strategy=AgentStrategy.ADAPTIVE,
        corruption_mode=CorruptionMode.PLAUSIBLE_WRONG,
        provider="openai",
        model="gpt-4o",
        error_severity=ErrorSeverity.SEVERE,
        total_input_tokens=3000,
        total_output_tokens=800,
        total_token_cost=0.027,
        total_error_cost=5.0,
        total_cost=5.027,
    )
    assert run.strategy == AgentStrategy.ADAPTIVE
    assert run.error_severity == ErrorSeverity.SEVERE
    assert run.total_cost == run.total_token_cost + run.total_error_cost
