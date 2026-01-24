"""Tests for ValidationNode class and decorators."""

from typing import Any

import click
from click.testing import CliRunner

from click_extended import command, option
from click_extended.core.nodes.validation_node import ValidationNode
from click_extended.core.other._tree import Tree
from click_extended.core.other.context import Context
from click_extended.decorators import exclusive


class TestValidationNodeBase:
    """Test base ValidationNode functionality."""

    def test_validation_node_initialization(self) -> None:
        """Test that ValidationNode can be initialized properly."""

        class CustomValidation(ValidationNode):
            def on_finalize(
                self, context: Context, *args: Any, **kwargs: Any
            ) -> None:
                pass

        node = CustomValidation(name="test_validation")
        assert node.name == "test_validation"
        assert node.process_args == ()
        assert node.process_kwargs == {}

    def test_validation_node_with_process_args(self) -> None:
        """Test ValidationNode with process arguments."""

        class CustomValidation(ValidationNode):
            def on_finalize(
                self, context: Context, *args: Any, **kwargs: Any
            ) -> None:
                pass

        node = CustomValidation(
            name="test_validation",
            process_args=("arg1", "arg2"),
            process_kwargs={"key": "value"},
        )
        assert node.process_args == ("arg1", "arg2")
        assert node.process_kwargs == {"key": "value"}


class TestValidationNodeWithSyncCommands:
    """Test ValidationNode decorators with synchronous commands."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_sync_command_with_exclusive_no_flags(self) -> None:
        """Test synchronous command with exclusive decorator and no flags."""

        @command()
        @option("flag1", is_flag=True)
        @option("flag2", is_flag=True)
        @exclusive("flag1", "flag2")
        def my_command(flag1: bool, flag2: bool) -> None:
            click.echo(f"{flag1},{flag2}")

        runner = CliRunner()
        result = runner.invoke(my_command, [])
        assert result.exit_code == 0
        assert "False,False" in result.output

    def test_sync_command_with_exclusive_one_flag(self) -> None:
        """Test synchronous command with exclusive decorator and one flag."""

        @command()
        @option("flag1", is_flag=True)
        @option("flag2", is_flag=True)
        @exclusive("flag1", "flag2")
        def my_command(flag1: bool, flag2: bool) -> None:
            click.echo(f"{flag1},{flag2}")

        runner = CliRunner()
        result = runner.invoke(my_command, ["--flag1"])
        assert result.exit_code == 0
        assert "True,False" in result.output

    def test_sync_command_with_exclusive_validates(self) -> None:
        """Test that exclusive validation works with synchronous commands."""

        @command()
        @option("flag1", is_flag=True)
        @option("flag2", is_flag=True)
        @exclusive("flag1", "flag2")
        def my_command(flag1: bool, flag2: bool) -> None:
            click.echo(f"{flag1},{flag2}")

        runner = CliRunner()
        result = runner.invoke(my_command, ["--flag1", "--flag2"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()


class TestValidationNodeWithAsyncCommands:
    """Test ValidationNode decorators with asynchronous commands."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_async_command_with_exclusive_no_flags(self) -> None:
        """
        Test async command with exclusive decorator works
        with no flags provided.
        """

        @command()
        @option("flag1", is_flag=True)
        @option("flag2", is_flag=True)
        @exclusive("flag1", "flag2")
        async def my_command(flag1: bool, flag2: bool) -> None:
            click.echo(f"{flag1},{flag2}")

        runner = CliRunner()
        result = runner.invoke(my_command, [])
        assert result.exit_code == 0
        assert "False,False" in result.output

    def test_async_command_with_exclusive_one_flag(self) -> None:
        """Test async command with exclusive decorator works with one flag."""

        @command()
        @option("flag1", is_flag=True)
        @option("flag2", is_flag=True)
        @exclusive("flag1", "flag2")
        async def my_command(flag1: bool, flag2: bool) -> None:
            click.echo(f"{flag1},{flag2}")

        runner = CliRunner()
        result = runner.invoke(my_command, ["--flag1"])
        assert result.exit_code == 0
        assert "True,False" in result.output

    def test_async_command_with_exclusive_validates_correctly(self) -> None:
        """Test that exclusive validation still works with async commands."""

        @command()
        @option("flag1", is_flag=True)
        @option("flag2", is_flag=True)
        @exclusive("flag1", "flag2")
        async def my_command(flag1: bool, flag2: bool) -> None:
            click.echo(f"{flag1},{flag2}")

        runner = CliRunner()
        result = runner.invoke(my_command, ["--flag1", "--flag2"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_async_command_with_multiple_flags(self) -> None:
        """Test async command with three mutually exclusive flags."""

        @command()
        @option("json", is_flag=True)
        @option("xml", is_flag=True)
        @option("yaml", is_flag=True)
        @exclusive("json", "xml", "yaml")
        async def export_data(json: bool, xml: bool, yaml: bool) -> None:
            click.echo(f"{json},{xml},{yaml}")

        runner = CliRunner()

        # No flags should work
        result = runner.invoke(export_data, [])
        assert result.exit_code == 0
        assert "False,False,False" in result.output

        # One flag should work
        result = runner.invoke(export_data, ["--json"])
        assert result.exit_code == 0
        assert "True,False,False" in result.output

        # Two flags should fail
        result = runner.invoke(export_data, ["--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()


__all__ = [
    "TestValidationNodeBase",
    "TestValidationNodeWithSyncCommands",
    "TestValidationNodeWithAsyncCommands",
]
