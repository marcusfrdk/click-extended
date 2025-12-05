"""Comprehensive tests for choice decorator."""

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.misc.choice import Choice, choice


class TestChoiceInit:
    """Test Choice class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_choice_is_child_node(self) -> None:
        """Test that Choice extends ChildNode."""
        node = Choice(name="test")
        assert isinstance(node, ChildNode)

    def test_choice_has_handle_methods(self) -> None:
        """Test that Choice implements str, int, and float handlers."""
        node = Choice(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)
        assert hasattr(node, "handle_int")
        assert callable(node.handle_int)
        assert hasattr(node, "handle_float")
        assert callable(node.handle_float)

    def test_choice_requires_at_least_one_value(self) -> None:
        """Test that choice raises ValueError when no values provided."""
        with pytest.raises(ValueError) as exc_info:
            choice()
        assert "At least one choice must be provided" in str(exc_info.value)


class TestChoiceStringValidation:
    """Test choice decorator with string values."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_valid_choice_passes(self, cli_runner: CliRunner) -> None:
        """Test that valid choice passes validation."""

        @command()
        @option("color", default="red")
        @choice("red", "green", "blue")
        def cmd(color: str) -> None:
            click.echo(f"Color: {color}")

        result = cli_runner.invoke(cmd, ["--color", "red"])
        assert result.exit_code == 0
        assert "Color: red" in result.output

    def test_invalid_choice_fails(self, cli_runner: CliRunner) -> None:
        """Test that invalid choice fails validation."""

        @command()
        @option("color", default="yellow")
        @choice("red", "green", "blue")
        def cmd(color: str) -> None:
            click.echo(f"Color: {color}")

        result = cli_runner.invoke(cmd, ["--color", "yellow"])
        assert result.exit_code != 0
        assert "Value must be one of 'red', 'green' or 'blue'" in result.output
        assert "got 'yellow'" in result.output

    def test_two_choices(self, cli_runner: CliRunner) -> None:
        """Test choice with two options."""

        @command()
        @option("answer", default="yes")
        @choice("yes", "no")
        def cmd(answer: str) -> None:
            click.echo(f"Answer: {answer}")

        result = cli_runner.invoke(cmd, ["--answer", "yes"])
        assert result.exit_code == 0

    def test_single_choice(self, cli_runner: CliRunner) -> None:
        """Test choice with single option."""

        @command()
        @option("mode", default="production")
        @choice("production")
        def cmd(mode: str) -> None:
            click.echo(f"Mode: {mode}")

        result = cli_runner.invoke(cmd, ["--mode", "production"])
        assert result.exit_code == 0

    def test_many_choices(self, cli_runner: CliRunner) -> None:
        """Test choice with many options."""

        @command()
        @option("day", default="Monday")
        @choice(
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
        def cmd(day: str) -> None:
            click.echo(f"Day: {day}")

        result = cli_runner.invoke(cmd, ["--day", "Friday"])
        assert result.exit_code == 0


class TestChoiceCaseSensitive:
    """Test choice decorator with case sensitivity."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_case_sensitive_default(self, cli_runner: CliRunner) -> None:
        """Test that choice is case-sensitive by default."""

        @command()
        @option("color", default="RED")
        @choice("red", "green", "blue")
        def cmd(color: str) -> None:
            click.echo(f"Color: {color}")

        result = cli_runner.invoke(cmd, ["--color", "RED"])
        assert result.exit_code != 0
        assert "Value must be one of 'red', 'green' or 'blue'" in result.output

    def test_case_insensitive_match(self, cli_runner: CliRunner) -> None:
        """Test case-insensitive matching."""

        @command()
        @option("level", default="DEBUG")
        @choice("debug", "info", "warning", "error", case_sensitive=False)
        def cmd(level: str) -> None:
            click.echo(f"Level: {level}")

        result = cli_runner.invoke(cmd, ["--level", "DEBUG"])
        assert result.exit_code == 0

    def test_case_insensitive_mixed_case(self, cli_runner: CliRunner) -> None:
        """Test case-insensitive with mixed case input."""

        @command()
        @option("answer", default="YeS")
        @choice("yes", "no", case_sensitive=False)
        def cmd(answer: str) -> None:
            click.echo(f"Answer: {answer}")

        result = cli_runner.invoke(cmd, ["--answer", "YeS"])
        assert result.exit_code == 0

    def test_case_insensitive_lowercase_choice(
        self, cli_runner: CliRunner
    ) -> None:
        """Test case-insensitive with lowercase defined choice."""

        @command()
        @option("command", default="start")
        @choice("start", "stop", "restart", case_sensitive=False)
        def cmd(command: str) -> None:
            click.echo(f"Command: {command}")

        result = cli_runner.invoke(cmd, ["--command", "START"])
        assert result.exit_code == 0

    def test_case_insensitive_invalid_still_fails(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that case-insensitive still rejects invalid choices."""

        @command()
        @option("level", default="TRACE")
        @choice("debug", "info", "warning", "error", case_sensitive=False)
        def cmd(level: str) -> None:
            click.echo(f"Level: {level}")

        result = cli_runner.invoke(cmd, ["--level", "TRACE"])
        assert result.exit_code != 0


class TestChoiceNumericValues:
    """Test choice decorator with numeric values."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_integer_choices(self, cli_runner: CliRunner) -> None:
        """Test choice with integer values."""

        @command()
        @option("port", type=int, default=8080)
        @choice(80, 443, 8080, 8443)
        def cmd(port: int) -> None:
            click.echo(f"Port: {port}")

        result = cli_runner.invoke(cmd, ["--port", "8080"])
        assert result.exit_code == 0

    def test_integer_invalid(self, cli_runner: CliRunner) -> None:
        """Test choice with invalid integer."""

        @command()
        @option("port", type=int, default=3000)
        @choice(80, 443, 8080, 8443)
        def cmd(port: int) -> None:
            click.echo(f"Port: {port}")

        result = cli_runner.invoke(cmd, ["--port", "3000"])
        assert result.exit_code != 0
        assert (
            "Value must be one of '80', '443', '8080' or '8443'"
            in result.output
        )

    def test_float_choices(self, cli_runner: CliRunner) -> None:
        """Test choice with float values."""

        @command()
        @option("rate", type=float, default=1.5)
        @choice(0.5, 1.0, 1.5, 2.0)
        def cmd(rate: float) -> None:
            click.echo(f"Rate: {rate}")

        result = cli_runner.invoke(cmd, ["--rate", "1.5"])
        assert result.exit_code == 0


class TestChoiceTypeValidation:
    """Test choice decorator type validation."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_invalid_type_raises_error(self) -> None:
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError) as exc_info:
            choice("red", "green", [1, 2, 3])  # type: ignore
        assert "All choice values must be str, int, or float" in str(
            exc_info.value
        )
        assert "got list" in str(exc_info.value)

    def test_dict_type_raises_error(self) -> None:
        """Test that dict type raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            choice("red", {"key": "value"})  # type: ignore
        assert "All choice values must be str, int, or float" in str(
            exc_info.value
        )
        assert "got dict" in str(exc_info.value)

    def test_none_type_raises_error(self) -> None:
        """Test that None type raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            choice("red", None)  # type: ignore
        assert "All choice values must be str, int, or float" in str(
            exc_info.value
        )
        assert "got NoneType" in str(exc_info.value)

    def test_mixed_string_and_integer_valid(
        self, cli_runner: CliRunner
    ) -> None:
        """Test choice with mixed string and integer values."""

        @command()
        @option("value", default="auto")
        @choice("auto", 1, 2, 3)
        def cmd(value: str | int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "auto"])
        assert result.exit_code == 0

    def test_mixed_string_and_float_valid(self, cli_runner: CliRunner) -> None:
        """Test choice with mixed string and float values."""

        @command()
        @option("value", default="auto")
        @choice("auto", 1.5, 2.0, 3.5)
        def cmd(value: str | float) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "auto"])
        assert result.exit_code == 0


class TestChoiceErrorMessages:
    """Test error messages for choice decorator."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_error_message_single_choice(self, cli_runner: CliRunner) -> None:
        """Test error message with single choice."""

        @command()
        @option("mode", default="invalid")
        @choice("production")
        def cmd(mode: str) -> None:
            click.echo(f"Mode: {mode}")

        result = cli_runner.invoke(cmd, ["--mode", "invalid"])
        assert result.exit_code != 0
        assert "Value must be 'production'" in result.output

    def test_error_message_two_choices(self, cli_runner: CliRunner) -> None:
        """Test error message with two choices."""

        @command()
        @option("answer", default="maybe")
        @choice("yes", "no")
        def cmd(answer: str) -> None:
            click.echo(f"Answer: {answer}")

        result = cli_runner.invoke(cmd, ["--answer", "maybe"])
        assert result.exit_code != 0
        assert "Value must be one of 'yes' or 'no'" in result.output

    def test_error_message_three_choices(self, cli_runner: CliRunner) -> None:
        """Test error message with three choices."""

        @command()
        @option("size", default="xl")
        @choice("small", "medium", "large")
        def cmd(size: str) -> None:
            click.echo(f"Size: {size}")

        result = cli_runner.invoke(cmd, ["--size", "xl"])
        assert result.exit_code != 0
        assert (
            "Value must be one of 'small', 'medium' or 'large'" in result.output
        )

    def test_error_message_shows_invalid_value(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that error message shows the invalid value."""

        @command()
        @option("color", default="purple")
        @choice("red", "green", "blue")
        def cmd(color: str) -> None:
            click.echo(f"Color: {color}")

        result = cli_runner.invoke(cmd, ["--color", "purple"])
        assert result.exit_code != 0
        assert "got 'purple'" in result.output


class TestChoiceChaining:
    """Test choice decorator chaining with other decorators."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_with_not_empty(self, cli_runner: CliRunner) -> None:
        """Test chaining choice with not_empty."""
        from click_extended.decorators.check.not_empty import not_empty

        @command()
        @option("color", default="red")
        @not_empty()
        @choice("red", "green", "blue")
        def cmd(color: str) -> None:
            click.echo(f"Color: {color}")

        result = cli_runner.invoke(cmd, ["--color", "red"])
        assert result.exit_code == 0

    def test_chain_with_length(self, cli_runner: CliRunner) -> None:
        """Test chaining choice with length."""
        from click_extended.decorators.check.length import length

        @command()
        @option("code", default="USA")
        @choice("USA", "CAN", "MEX", "GBR", "FRA")
        @length(min=3, max=3)
        def cmd(code: str) -> None:
            click.echo(f"Country: {code}")

        result = cli_runner.invoke(cmd, ["--code", "USA"])
        assert result.exit_code == 0


class TestChoicePractical:
    """Test practical use cases for choice decorator."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_log_level_validation(self, cli_runner: CliRunner) -> None:
        """Test choice for log level validation."""

        @command()
        @option("log-level", default="INFO")
        @choice("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        def cmd(log_level: str) -> None:
            click.echo(f"Log level: {log_level}")

        result = cli_runner.invoke(cmd, ["--log-level", "INFO"])
        assert result.exit_code == 0

    def test_environment_validation(self, cli_runner: CliRunner) -> None:
        """Test choice for environment validation."""

        @command()
        @option("env", default="development")
        @choice("development", "staging", "production")
        def cmd(env: str) -> None:
            click.echo(f"Environment: {env}")

        result = cli_runner.invoke(cmd, ["--env", "production"])
        assert result.exit_code == 0

    def test_file_format_validation(self, cli_runner: CliRunner) -> None:
        """Test choice for file format validation."""

        @command()
        @option("format", default="json")
        @choice("json", "xml", "yaml", "csv")
        def cmd(format: str) -> None:
            click.echo(f"Format: {format}")

        result = cli_runner.invoke(cmd, ["--format", "json"])
        assert result.exit_code == 0

    def test_http_method_validation(self, cli_runner: CliRunner) -> None:
        """Test choice for HTTP method validation."""

        @command()
        @option("method", default="GET")
        @choice("GET", "POST", "PUT", "DELETE", "PATCH")
        def cmd(method: str) -> None:
            click.echo(f"Method: {method}")

        result = cli_runner.invoke(cmd, ["--method", "POST"])
        assert result.exit_code == 0

    def test_boolean_choice_as_strings(self, cli_runner: CliRunner) -> None:
        """Test choice for boolean-like string values."""

        @command()
        @option("enabled", default="true")
        @choice("true", "false", case_sensitive=False)
        def cmd(enabled: str) -> None:
            click.echo(f"Enabled: {enabled}")

        result = cli_runner.invoke(cmd, ["--enabled", "TRUE"])
        assert result.exit_code == 0
