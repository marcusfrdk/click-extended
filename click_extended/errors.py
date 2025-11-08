"""Errors and exceptions used in Click Extended."""

from click_extended.core._failure import Failure


class ClickExtendedError(Exception):
    """Base exception for all click_extended errors."""


class DecoratorImplementationError(ClickExtendedError):
    """Raised when a decorator is improperly implemented."""


class NoMainNodeError(ClickExtendedError):
    """Raised when parents or children are used without a main node."""


class NoParentNodeError(ClickExtendedError):
    """Raised when a child decorator is used without a parent decorator."""


class TaggedEnvironmentError(ClickExtendedError):
    """Raised when child used in tagged environment without implementation."""


class UsageError(ClickExtendedError):
    """Raised when a decorator is used incorrectly."""


class ExecutionError(ClickExtendedError):
    """Raised when one or more failures occur during execution."""

    def __init__(self, failures: list["Failure"]) -> None:
        """Initialize a new ExecutionError with collected failures."""
        self.failures = failures
        message = self._format_failures()
        super().__init__(message)

    def _format_failures(self) -> str:
        """Format all failures into a readable message."""
        if not self.failures:
            return "Execution failed"

        lines = [f"Execution failed with {len(self.failures)} error(s):"]
        for i, failure in enumerate(self.failures, 1):
            lines.append(f"  {i}. {failure}")
        return "\n".join(lines)
