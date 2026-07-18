"""Controlled corruption injection for tool outputs.

Supports four modes:
  - explicit_error: Tool returns an error message
  - malformed: Tool returns truncated, missing-field, or invalid JSON output
  - plausible_wrong: Tool returns well-formed but factually incorrect output
  - clean: No corruption (control condition)

TODO (Day 18): Implement each corruption mode with configurable parameters.
"""

from __future__ import annotations

from faultline.schemas import CorruptionMode, ToolResult


class CorruptionInjector:
    """Injects controlled faults into tool outputs based on the corruption mode."""

    def inject(self, result: ToolResult, mode: CorruptionMode) -> ToolResult:
        if mode == CorruptionMode.CLEAN:
            return result

        if mode == CorruptionMode.EXPLICIT_ERROR:
            return self._inject_error(result)
        elif mode == CorruptionMode.MALFORMED:
            return self._inject_malformed(result)
        elif mode == CorruptionMode.PLAUSIBLE_WRONG:
            return self._inject_plausible_wrong(result)
        else:
            raise ValueError(f"Unknown corruption mode: {mode}")

    def _inject_error(self, result: ToolResult) -> ToolResult:
        raise NotImplementedError

    def _inject_malformed(self, result: ToolResult) -> ToolResult:
        raise NotImplementedError

    def _inject_plausible_wrong(self, result: ToolResult) -> ToolResult:
        raise NotImplementedError
