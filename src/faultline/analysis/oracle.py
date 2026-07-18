"""Oracle-optimal strategy computation.

The oracle has perfect information about which tool outputs are corrupted
and what type of corruption occurred. It selects the cheapest verification
action that still produces a correct outcome.

This is computed post-hoc from labeled experiment data, not during the run.
It serves as the theoretical lower bound against which all real strategies
are measured. The gap (regret) is the core metric of the research.

Oracle decision rules:
  - Clean output         → ACCEPT (cost: 0, no verification needed)
  - Explicit error       → RETRY  (cheapest: one retry fixes it)
  - Malformed output     → RETRY  (re-request usually yields valid format)
  - Plausible but wrong  → INVOKE_CRITIC or INVOKE_VERIFIER (cheapest that catches it)

TODO (Day 25–27): Implement oracle computation from labeled runs.
"""

from __future__ import annotations

from faultline.schemas import (
    CostModel,
    CorruptionMode,
    OracleAction,
    RegretRecord,
    RunRecord,
    VerificationAction,
    VerificationDecision,
)


# Default oracle action mapping — can be overridden per task domain
ORACLE_ACTION_MAP: dict[CorruptionMode, VerificationAction] = {
    CorruptionMode.CLEAN: VerificationAction.ACCEPT,
    CorruptionMode.EXPLICIT_ERROR: VerificationAction.RETRY,
    CorruptionMode.MALFORMED: VerificationAction.RETRY,
    CorruptionMode.PLAUSIBLE_WRONG: VerificationAction.INVOKE_CRITIC,
}


def compute_oracle_actions(
    run: RunRecord,
    cost_model: CostModel,
) -> list[OracleAction]:
    """Compute what the oracle would have done at each verification decision point.

    Uses the ground-truth corruption labels (which the oracle can see)
    to select the cheapest action that leads to a correct outcome.
    """
    oracle_actions: list[OracleAction] = []

    for step in run.steps:
        if step.verification is None:
            continue

        # Oracle knows the true corruption mode
        optimal_action = ORACLE_ACTION_MAP.get(
            run.corruption_mode, VerificationAction.ACCEPT
        )

        # Estimate the oracle's cost for this action
        optimal_cost = _estimate_action_cost(optimal_action, cost_model)

        oracle_actions.append(
            OracleAction(
                step_index=step.step_index,
                optimal_action=optimal_action,
                optimal_cost=optimal_cost,
                reasoning=f"Corruption mode is {run.corruption_mode.value}; "
                f"cheapest effective action is {optimal_action.value}.",
            )
        )

    return oracle_actions


def compute_regret(
    run: RunRecord,
    cost_model: CostModel,
) -> RegretRecord:
    """Compute the regret for a completed run.

    regret = actual_total_cost - oracle_total_cost

    The price of uncertainty is regret / oracle_total_cost,
    representing the fractional overhead of not having perfect information.
    """
    oracle_actions = compute_oracle_actions(run, cost_model)
    oracle_total = sum(a.optimal_cost for a in oracle_actions)

    # Add oracle's error cost (zero, since oracle always gets it right)
    # vs actual error cost from the run
    actual_total = run.total_cost

    regret = actual_total - oracle_total
    price = (regret / oracle_total) if oracle_total > 0 else 0.0

    actual_decisions = [
        step.verification
        for step in run.steps
        if step.verification is not None
    ]

    return RegretRecord(
        run_id=run.run_id,
        actual_total_cost=actual_total,
        oracle_total_cost=oracle_total,
        regret=max(0.0, regret),  # Clamp to non-negative
        actual_decisions=actual_decisions,
        oracle_decisions=oracle_actions,
        price_of_uncertainty=max(0.0, price),
    )


def _estimate_action_cost(action: VerificationAction, cost_model: CostModel) -> float:
    """Estimate the token cost of a verification action.

    These are rough estimates used for oracle computation.
    Actual costs come from the traced token usage.

    TODO: Calibrate from pilot data (Day 30).
    """
    ESTIMATED_TOKENS: dict[VerificationAction, tuple[int, int]] = {
        VerificationAction.ACCEPT: (0, 0),
        VerificationAction.RETRY: (500, 200),
        VerificationAction.INVOKE_CRITIC: (800, 300),
        VerificationAction.INVOKE_VERIFIER: (1000, 400),
        VerificationAction.SKIP: (0, 0),
    }
    input_t, output_t = ESTIMATED_TOKENS.get(action, (0, 0))
    return cost_model.token_cost(input_t, output_t)
