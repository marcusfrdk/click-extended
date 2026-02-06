"""Tests for observe decorator."""

from typing import Any

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.core.other.context import Context
from click_extended.decorators.misc.observe import Observe, observe


class TestObserveInit:
    """Test Observe class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_observe_is_child_node(self) -> None:
        """Test that Observe extends ChildNode."""
        node = Observe(name="test")
        assert isinstance(node, ChildNode)

    def test_observe_has_handle_all_method(self) -> None:
        """Test that Observe implements handle_all handler."""
        node = Observe(name="test")
        assert hasattr(node, "handle_all")
        assert callable(node.handle_all)


class TestObserveValueOnly:
    """Test observe decorator with value-only handler."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_handler_receives_value(self, cli_runner: CliRunner) -> None:
        """Test that handler receives value and value passes through."""
        captured: list[Any] = []

        def handler(value: Any) -> None:
            captured.append(value)

        @command()
        @option("count", type=int, default=5)
        @observe(handler)
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["--count", "7"])
        assert result.exit_code == 0
        assert "Count: 7" in result.output
        assert captured == [7]

    def test_handler_return_is_ignored(self, cli_runner: CliRunner) -> None:
        """Test that handler return value does not change the chain."""

        def handler(value: Any) -> str:
            return "override"

        @command()
        @option("name", default="alice")
        @observe(handler)
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "bob"])
        assert result.exit_code == 0
        assert "Name: bob" in result.output


class TestObserveValueContext:
    """Test observe decorator with value+context handler."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_handler_receives_context(self, cli_runner: CliRunner) -> None:
        """Test that handler receives context when it accepts two params."""
        captured: dict[str, Any] = {}

        def handler(value: Any, ctx: Context) -> None:
            captured["value"] = value
            captured["parent_name"] = ctx.get_current_parent_as_parent().name

        @command()
        @option("path", default="/tmp")
        @observe(handler)
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "/var/log"])
        assert result.exit_code == 0
        assert "Path: /var/log" in result.output
        assert captured == {"value": "/var/log", "parent_name": "path"}


class TestObserveInvalidHandler:
    """Test observe decorator with invalid handler signatures."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_handler_with_no_params_errors(self, cli_runner: CliRunner) -> None:
        """Test that handler with no params raises error."""

        def handler() -> None:
            pass

        @command()
        @option("value", default="x")
        @observe(handler)  # type: ignore[arg-type]
        def cmd(value: str) -> None:
            click.echo(value)

        result = cli_runner.invoke(cmd, ["--value", "y"])
        assert result.exit_code != 0
        assert "observe() handler must accept" in result.output

    def test_handler_with_three_params_errors(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that handler with too many params raises error."""

        def handler(value: Any, ctx: Context, extra: Any) -> None:
            _ = (value, ctx, extra)

        @command()
        @option("value", default="x")
        @observe(handler)  # type: ignore[arg-type]
        def cmd(value: str) -> None:
            click.echo(value)

        result = cli_runner.invoke(cmd, ["--value", "y"])
        assert result.exit_code != 0
        assert "observe() handler must accept" in result.output
