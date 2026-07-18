"""Tests for core Pydantic schemas."""

from faultline.schemas import (
    AgentStrategy,
    CorruptionMode,
    ExperimentConfig,
    Message,
    RunRecord,
    RunStatus,
    TaskDefinition,
    TaskDomain,
    ToolCall,
    ToolResult,
)


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
