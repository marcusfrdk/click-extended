"""Shared test fixtures and utilities for click-extended tests."""

from typing import Any

import pytest
from click.testing import CliRunner

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CliRunner for testing CLI commands."""
    return CliRunner()


class SimpleChild(ChildNode):
    """Reusable child node that uppercases strings."""

    def handle_str(self, value: str, context: Context) -> str:
        """Uppercase the input value."""
        return value.upper()


class MultiplyChild(ChildNode):
    """Reusable child node that multiplies numbers."""

    def handle_int(self, value: int, context: Context) -> int:
        """Multiply value by 2."""
        return value * 2


class ValidatingChild(ChildNode):
    """Reusable child node that validates positive numbers."""

    def handle_int(self, value: int, context: Context) -> int:
        """Validate value is positive."""
        if value <= 0:
            raise ValueError(f"{value} must be positive")
        return value


def make_child(
    name: str = "test_child",
    handler_fn: Any = None,
) -> type[ChildNode]:
    """
    Create a custom ChildNode class for testing.

    Args:
        name: Name for the child node
        handler_fn: Custom handler function. If None, returns value unchanged.

    Returns:
        A ChildNode subclass
    """

    class CustomChild(ChildNode):
        def handle_all(self, value: Any, context: Context) -> Any:
            if handler_fn:
                return handler_fn(value, context)
            return value

    CustomChild.__name__ = name
    return CustomChild


def make_parent(
    name: str = "test_param",
    **kwargs: Any,
) -> ParentNode:
    """
    Create a ParentNode for testing.

    Args:
        name: Parameter name
        **kwargs: Additional ParentNode arguments

    Returns:
        A ParentNode instance
    """

    class TestParent(ParentNode):
        def __init__(self, **init_kwargs: Any):
            super().__init__(name=name, **{**kwargs, **init_kwargs})

        def load(self, context: Context, *args: Any, **kwargs: Any) -> Any:
            """Load method implementation for testing."""
            return kwargs.get("default")

    return TestParent()


def invoke_cli(
    runner: CliRunner, cmd: Any, args: list[str] | None = None
) -> Any:
    """
    Invoke a CLI command and return the result.

    Args:
        runner: CliRunner instance
        cmd: Command to invoke
        args: Command line arguments

    Returns:
        Click result object
    """
    return runner.invoke(cmd, args or [])


def assert_success(result: Any, expected_output: str | None = None) -> None:
    """
    Assert that a CLI invocation succeeded.

    Args:
        result: Click result object
        expected_output: Optional expected output string
    """
    assert result.exit_code == 0, f"Command failed: {result.output}"
    if expected_output:
        assert expected_output in result.output


def assert_error(
    result: Any, expected_code: int = 1, expected_msg: str | None = None
) -> None:
    """
    Assert that a CLI invocation failed with expected error.

    Args:
        result: Click result object
        expected_code: Expected exit code (default 1)
        expected_msg: Optional expected error message
    """
    assert (
        result.exit_code == expected_code
    ), f"Expected exit code {expected_code}, got {result.exit_code}"
    if expected_msg:
        assert (
            expected_msg in result.output
        ), f"Expected '{expected_msg}' in output: {result.output}"
