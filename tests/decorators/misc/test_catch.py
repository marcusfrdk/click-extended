"""Tests for catch decorator."""

import asyncio
from typing import Any

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.misc.catch import catch


class TestCatchBasic:
    """Test basic catch functionality."""

    def test_catch_single_exception_with_handler(
        self, cli_runner: CliRunner
    ) -> None:
        """Test catching a single exception type with handler."""
        caught_exceptions: list[str] = []

        def handler(e: Exception) -> None:
            caught_exceptions.append(str(e))

        @command()
        @catch(ValueError, handler=handler)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            raise ValueError(f"Invalid value: {name}")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code == 0
        assert len(caught_exceptions) == 1
        assert "Invalid value: test" in caught_exceptions[0]

    def test_catch_without_handler_silently_suppresses(
        self, cli_runner: CliRunner
    ) -> None:
        """Test catching exception without handler silently suppresses it."""

        @command()
        @catch(ValueError)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            raise ValueError("This should be suppressed")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code == 0
        assert result.output == ""

    def test_catch_multiple_exception_types(
        self, cli_runner: CliRunner
    ) -> None:
        """Test catching multiple exception types with one handler."""
        caught_exceptions: list[str] = []

        def handler(e: Exception) -> None:
            caught_exceptions.append(type(e).__name__)

        @command()
        @catch(ValueError, TypeError, handler=handler)
        @option("error_type", type=str, default="value")
        def cmd(error_type: str) -> None:
            if error_type == "value":
                raise ValueError("value error")
            elif error_type == "type":
                raise TypeError("type error")

        # Test ValueError
        result = cli_runner.invoke(cmd, ["--error-type", "value"])
        assert result.exit_code == 0
        assert "ValueError" in caught_exceptions

        # Test TypeError
        caught_exceptions.clear()
        result = cli_runner.invoke(cmd, ["--error-type", "type"])
        assert result.exit_code == 0
        assert "TypeError" in caught_exceptions

    def test_catch_no_exception_passes_through(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that execution proceeds normally when no exception occurs."""

        @command()
        @catch(ValueError)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "hello"])
        assert result.exit_code == 0
        assert "Name: hello" in result.output


class TestCatchWithContext:
    """Test catch decorator with context parameter."""

    def test_handler_receives_context(self, cli_runner: CliRunner) -> None:
        """Test handler can receive both exception and context."""
        received_context: list[bool] = []

        def handler(e: Exception, ctx: Any) -> None:
            received_context.append(ctx is not None)

        @command()
        @catch(ValueError, handler=handler)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            raise ValueError("test")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code == 0
        assert len(received_context) == 1


class TestCatchReraise:
    """Test catch decorator reraise functionality."""

    def test_reraise_after_handler(self, cli_runner: CliRunner) -> None:
        """Test re-raising exception after handler executes."""
        handler_called: list[bool] = []

        def handler(e: Exception) -> None:
            handler_called.append(True)
            click.echo(f"Handler called: {e}")

        @command()
        @catch(ValueError, handler=handler, reraise=True)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            raise ValueError("test error")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code != 0
        assert len(handler_called) == 1
        assert "Handler called" in result.output
        assert "test error" in result.output


class TestCatchStacking:
    """Test stacking multiple catch decorators."""

    def test_topmost_matching_catch_handles_first(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that topmost matching catch handles the exception (top-down order)."""
        handlers_called: list[str] = []

        def inner_handler(e: Exception) -> None:
            handlers_called.append("inner")

        def outer_handler(e: Exception) -> None:
            handlers_called.append("outer")

        @command()
        @catch(Exception, handler=outer_handler)
        @catch(ValueError, handler=inner_handler)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            raise ValueError("test")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code == 0
        # Topmost catch is checked first (top-down), so only outer should handle
        assert handlers_called == ["outer"]

    def test_multiple_catch_different_exceptions(
        self, cli_runner: CliRunner
    ) -> None:
        """Test multiple catch decorators handling different exceptions."""
        handlers_called: list[str] = []

        def value_handler(e: Exception) -> None:
            handlers_called.append("ValueError")

        def type_handler(e: Exception) -> None:
            handlers_called.append("TypeError")

        @command()
        @catch(TypeError, handler=type_handler)
        @catch(ValueError, handler=value_handler)
        @option("error_type", type=str, default="value")
        def cmd(error_type: str) -> None:
            if "value" in error_type:
                raise ValueError("value error")
            elif "type" in error_type:
                raise TypeError("type error")

        # Test ValueError caught by inner catch
        result = cli_runner.invoke(cmd, ["--error-type", "value"])
        assert result.exit_code == 0
        assert handlers_called == ["ValueError"]

        # Test TypeError caught by outer catch
        handlers_called.clear()
        result = cli_runner.invoke(cmd, ["--error-type", "type"])
        assert result.exit_code == 0
        assert handlers_called == ["TypeError"]


class TestCatchEdgeCases:
    """Test edge cases and error conditions."""

    def test_catch_with_no_exception_types_catches_all(
        self, cli_runner: CliRunner
    ) -> None:
        """Test catch with no exception types catches all exceptions."""
        handler_called: list[str] = []

        def handler(e: Exception) -> None:
            handler_called.append(type(e).__name__)

        @command()
        @catch(handler=handler)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            raise RuntimeError("custom error")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code == 0
        assert "RuntimeError" in handler_called

    def test_catch_with_invalid_exception_type_raises_error(self) -> None:
        """Test that invalid exception types raise TypeError."""
        with pytest.raises(TypeError, match="requires exception types"):
            catch("not an exception")  # type: ignore

        with pytest.raises(TypeError, match="requires exception types"):
            catch(ValueError, "also not an exception")  # type: ignore

    def test_catch_with_argument(self, cli_runner: CliRunner) -> None:
        """Test catch decorator works with arguments."""
        handler_called: list[bool] = []

        def handler(e: Exception) -> None:
            handler_called.append(True)

        @command()
        @catch(ValueError, handler=handler)
        @argument("name")
        def cmd(name: str) -> None:
            if name == "error":
                raise ValueError("error")
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["error"])
        assert result.exit_code == 0
        assert len(handler_called) == 1


class TestCatchAsync:
    """Test catch decorator with async handlers and functions."""

    def test_catch_with_async_handler(self, cli_runner: CliRunner) -> None:
        """Test catch works with async handler function."""
        handler_called: list[bool] = []

        async def async_handler(e: Exception) -> None:
            await asyncio.sleep(0)
            handler_called.append(True)

        @command()
        @catch(ValueError, handler=async_handler)
        @option("--name", type=str, default="test")
        def cmd(name: str) -> None:
            raise ValueError("test")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code == 0

    def test_catch_with_async_command(self, cli_runner: CliRunner) -> None:
        """Test catch works with async command function."""
        handler_called: list[bool] = []

        def handler(e: Exception) -> None:
            handler_called.append(True)
            click.echo(f"Caught: {e}")

        @command()
        @catch(ValueError, handler=handler)
        @option("--name", type=str, default="test")
        async def cmd(name: str) -> None:
            await asyncio.sleep(0)
            raise ValueError("async error")

        result = cli_runner.invoke(cmd, ["--name", "test"])
        assert result.exit_code == 0
        assert len(handler_called) == 1
        assert "Caught: async error" in result.output


class TestCatchPracticalExamples:
    """Real-world usage examples."""

    def test_catch_validation_error_with_fallback(
        self, cli_runner: CliRunner
    ) -> None:
        """Example: Catch validation errors and log them."""
        errors_logged: list[str] = []

        def log_error(e: Exception) -> None:
            errors_logged.append(str(e))
            click.echo(f"Warning: {e}")

        @command()
        @catch(ValueError, handler=log_error)
        @option("--count", type=int, default=-5)
        def cmd(count: int) -> None:
            if count < 0:
                raise ValueError(f"Must be positive, got {count}")
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["--count", "-5"])
        assert result.exit_code == 0
        assert "Warning: Must be positive" in result.output
        assert len(errors_logged) == 1

    def test_catch_with_cleanup_actions(self, cli_runner: CliRunner) -> None:
        """Example: Perform cleanup when catching exceptions."""
        cleanup_performed: list[bool] = []

        def cleanup_handler(e: Exception) -> None:
            cleanup_performed.append(True)
            click.echo("Cleanup performed")

        @command()
        @catch(RuntimeError, handler=cleanup_handler)
        @option("--file", type=str, default="test.txt")
        def cmd(file: str) -> None:
            raise RuntimeError(f"Could not process {file}")

        result = cli_runner.invoke(cmd, ["--file", "data.txt"])
        assert result.exit_code == 0
        assert "Cleanup performed" in result.output
        assert len(cleanup_performed) == 1
