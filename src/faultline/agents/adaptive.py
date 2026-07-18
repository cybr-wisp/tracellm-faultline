"""Adaptive verification policy.

Unlike static strategies (always retry, always critique), the adaptive policy
inspects signals from each tool output to decide whether verification is worth
the cost. This is the core experimental intervention.

Signals the policy can use:
  - Output format validity (is it valid JSON? expected schema?)
  - Output entropy (how surprising is the content?)
  - Consistency with prior tool outputs in the same run
  - Domain-specific heuristics (e.g., numeric range checks)
  - Historical corruption rate for this tool

The policy maps signals → VerificationAction using a threshold rule
(initially simple, can be extended to a learned policy).

TODO (Day 28-29): Implement signal extraction and threshold-based decision logic.
"""

from __future__ import annotations

from faultline.schemas import (
    ToolResult,
    VerificationAction,
    VerificationDecision,
)


class AdaptivePolicy:
    """Decides per-step whether to verify a tool output.

    The simplest version is a threshold on a suspicion score.
    If suspicion > threshold, verify. Otherwise, accept.
    """

    def __init__(
        self,
        suspicion_threshold: float = 0.5,
        default_action: VerificationAction = VerificationAction.INVOKE_CRITIC,
    ) -> None:
        self.suspicion_threshold = suspicion_threshold
        self.default_action = default_action

    def decide(
        self,
        step_index: int,
        tool_result: ToolResult,
    ) -> VerificationDecision:
        """Evaluate the tool result and decide whether to verify."""
        signals = self._extract_signals(tool_result)
        suspicion = self._compute_suspicion(signals)

        if suspicion > self.suspicion_threshold:
            action = self.default_action
        else:
            action = VerificationAction.ACCEPT

        return VerificationDecision(
            step_index=step_index,
            action=action,
            confidence=1.0 - suspicion,
            signals=signals,
        )

    def _extract_signals(self, tool_result: ToolResult) -> dict[str, float | bool]:
        """Extract decision-relevant features from the tool output.

        TODO: Implement real signal extraction.
        """
        signals: dict[str, float | bool] = {}

        # Signal: did the tool return an error?
        signals["has_error"] = tool_result.error is not None

        # Signal: is the output None or empty?
        signals["output_empty"] = tool_result.output is None or tool_result.output == {}

        # Signal: is the output a string that's suspiciously short?
        if isinstance(tool_result.output, str):
            signals["output_length"] = float(len(tool_result.output))
        elif isinstance(tool_result.output, dict):
            signals["output_length"] = float(len(str(tool_result.output)))
        else:
            signals["output_length"] = 0.0

        return signals

    def _compute_suspicion(self, signals: dict[str, float | bool]) -> float:
        """Combine signals into a single suspicion score in [0, 1].

        TODO: Replace with a learned scoring function after pilot data.
        """
        score = 0.0

        if signals.get("has_error"):
            score += 0.8
        if signals.get("output_empty"):
            score += 0.6
        if signals.get("output_length", 100.0) < 10.0:
            score += 0.3

        return min(1.0, score)
