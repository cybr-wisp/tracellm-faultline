"""Tests for core Pydantic schemas."""

import pytest

from faultline.schemas import (
    AgentStrategy,
    CostModel,
    ExperimentConfig,
    Message,
    OracleAction,
    OutputCondition,
    RecoveryRecord,
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
# Enum tests
# ---------------------------------------------------------------------------


def test_output_condition_values() -> None:
    assert OutputCondition.CLEAN == "clean"
    assert OutputCondition.PLAUSIBLE_WRONG == "plausible_wrong"


def test_adaptive_strategy_exists() -> None:
    assert AgentStrategy.ADAPTIVE == "adaptive"


# ---------------------------------------------------------------------------
# Tool schema tests
# ---------------------------------------------------------------------------


def test_tool_call_creation() -> None:
    tc = ToolCall(tool_name="lookup_order", arguments={"order_id": "ORD-123"}, call_id="call_1")
    assert tc.tool_name == "lookup_order"
    assert tc.arguments["order_id"] == "ORD-123"


def test_tool_result_defaults_to_clean() -> None:
    tr = ToolResult(output={"status": "shipped"})
    assert tr.corrupted is False
    assert tr.output_condition == OutputCondition.CLEAN


def test_message_with_tool_calls() -> None:
    msg = Message(
        role="assistant",
        tool_calls=[ToolCall(tool_name="get_schedule", arguments={"date": "2026-01-15"})],
    )
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0].tool_name == "get_schedule"


# ---------------------------------------------------------------------------
# Task definition tests
# ---------------------------------------------------------------------------


def test_task_definition() -> None:
    task = TaskDefinition(
        task_id="order-001",
        domain=TaskDomain.ORDER_SUPPORT,
        description="Look up order status and report to user.",
        instructions="Use the lookup_order tool to find the order, then summarize.",
        gold_answer="Order ORD-123 was shipped on Jan 10.",
        gold_tool_output={"order_id": "ORD-123", "status": "shipped"},
    )
    assert task.domain == TaskDomain.ORDER_SUPPORT
    assert task.gold_tool_output["status"] == "shipped"


def test_task_definition_with_corruption_variants() -> None:
    task = TaskDefinition(
        task_id="order-002",
        domain=TaskDomain.ORDER_SUPPORT,
        description="Check return eligibility.",
        instructions="Use check_return tool.",
        gold_tool_output={"eligible": True, "deadline": "2026-08-09"},
        corruption_variants={
            "explicit_error": {"error": "Service unavailable", "code": 503},
            "malformed": {"eligible": True},
            "plausible_wrong": {"eligible": False, "deadline": "2026-08-02"},
        },
        success_criteria={
            "fields": ["eligible", "deadline"],
            "match_type": "exact",
        },
    )
    assert "explicit_error" in task.corruption_variants
    assert task.success_criteria["match_type"] == "exact"


# ---------------------------------------------------------------------------
# Cost model tests
# ---------------------------------------------------------------------------


def test_cost_model_token_cost() -> None:
    cm = CostModel(input_token_cost_per_1k=0.01, output_token_cost_per_1k=0.03)
    cost = cm.token_cost(input_tokens=1000, output_tokens=500)
    assert cost == 0.01 + (500 / 1000) * 0.03


def test_cost_model_error_sweep_defaults() -> None:
    cm = CostModel()
    assert cm.error_cost_sweep == [100.0, 500.0, 1000.0, 2500.0, 5000.0]
    assert len(cm.error_cost_sweep) == 5


def test_cost_model_custom_sweep() -> None:
    cm = CostModel(error_cost_sweep=[50.0, 200.0, 800.0])
    assert len(cm.error_cost_sweep) == 3
    assert cm.error_cost_sweep[0] == 50.0


# ---------------------------------------------------------------------------
# Verification decision tests
# ---------------------------------------------------------------------------


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
    with pytest.raises(Exception):
        VerificationDecision(step_index=0, action=VerificationAction.PASS, confidence=1.5)


# ---------------------------------------------------------------------------
# Recovery record tests
# ---------------------------------------------------------------------------


def test_recovery_full_recovery() -> None:
    rr = RecoveryRecord(
        detection=True,
        corrective_action=True,
        task_success=True,
        informed_correctness=True,
    )
    assert rr.full_recovery is True


def test_recovery_lucky_guess_is_not_recovery() -> None:
    rr = RecoveryRecord(
        detection=False,
        corrective_action=False,
        task_success=True,
        informed_correctness=False,
    )
    assert rr.full_recovery is False


def test_recovery_detection_without_success() -> None:
    rr = RecoveryRecord(
        detection=True,
        corrective_action=True,
        task_success=False,
        informed_correctness=False,
    )
    assert rr.full_recovery is False


# ---------------------------------------------------------------------------
# Oracle and regret tests
# ---------------------------------------------------------------------------


def test_oracle_action() -> None:
    oa = OracleAction(
        step_index=0,
        optimal_action=VerificationAction.RETRY,
        optimal_token_cost=0.02,
        reasoning="Tool output was corrupted; cheapest fix is a single retry.",
    )
    assert oa.optimal_action == VerificationAction.RETRY
    assert oa.optimal_token_cost == 0.02


def test_regret_record() -> None:
    rr = RegretRecord(
        run_id="run-001",
        cost_by_error_level={
            "1000.0": {
                "actual_cost": 1.50,
                "oracle_cost": 0.30,
                "regret": 1.20,
                "pou": 4.0,
            }
        },
    )
    level = rr.cost_by_error_level["1000.0"]
    assert level["regret"] == level["actual_cost"] - level["oracle_cost"]
    assert level["pou"] == 4.0


# ---------------------------------------------------------------------------
# Run record tests
# ---------------------------------------------------------------------------


def test_run_record_defaults() -> None:
    run = RunRecord(
        run_id="run-001",
        experiment_id="exp-001",
        task_id="order-001",
        strategy=AgentStrategy.BASELINE,
        output_condition=OutputCondition.CLEAN,
        provider="fake",
        model="fake-model",
    )
    assert run.status == RunStatus.PENDING
    assert run.steps == []
    assert run.total_tokens == 0
    assert run.answer_flipped is False
    assert run.recovery is None
    assert run.regret is None


def test_run_record_with_answer_flip() -> None:
    run = RunRecord(
        run_id="run-flip-001",
        experiment_id="exp-001",
        task_id="order-001",
        strategy=AgentStrategy.VERIFIER,
        output_condition=OutputCondition.CLEAN,
        provider="openai",
        model="gpt-4o",
        answer_flipped=True,
        success=False,
    )
    assert run.answer_flipped is True
    assert run.success is False


def test_run_record_with_recovery() -> None:
    run = RunRecord(
        run_id="run-rec-001",
        experiment_id="exp-001",
        task_id="order-001",
        strategy=AgentStrategy.ADAPTIVE,
        output_condition=OutputCondition.PLAUSIBLE_WRONG,
        provider="openai",
        model="gpt-4o",
        total_input_tokens=3000,
        total_output_tokens=800,
        total_token_cost=0.027,
        recovery=RecoveryRecord(
            detection=True,
            corrective_action=True,
            task_success=True,
            informed_correctness=True,
        ),
    )
    assert run.strategy == AgentStrategy.ADAPTIVE
    assert run.recovery is not None
    assert run.recovery.full_recovery is True


# ---------------------------------------------------------------------------
# Experiment config tests
# ---------------------------------------------------------------------------


def test_experiment_config() -> None:
    cfg = ExperimentConfig(
        experiment_id="smoke-001",
        tasks=["order-001", "sched-001"],
        strategies=[AgentStrategy.BASELINE, AgentStrategy.RETRY],
        output_conditions=[OutputCondition.CLEAN, OutputCondition.EXPLICIT_ERROR],
        providers=["fake"],
        trials=3,
    )
    assert len(cfg.strategies) == 2
    assert cfg.trials == 3
    assert "break-even" in cfg.research_question
    assert "oracle-optimal" in cfg.research_question