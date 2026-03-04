"""Tests for is_numeric decorator."""

from unittest.mock import Mock

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.core.other.context import Context
from click_extended.decorators import check
from click_extended.decorators.check.is_numeric import IsNumeric


class TestIsNumericUnit:
    """Unit tests for IsNumeric node."""

    def test_is_numeric_integer_string(self) -> None:
        node = IsNumeric(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_str("42", ctx) == "42"

    def test_is_numeric_float_string(self) -> None:
        node = IsNumeric(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_str("3.14", ctx) == "3.14"

    def test_is_numeric_negative_string(self) -> None:
        node = IsNumeric(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_str("-7", ctx) == "-7"

    def test_is_numeric_scientific_notation(self) -> None:
        node = IsNumeric(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_str("1e10", ctx) == "1e10"

    def test_is_numeric_invalid_string(self) -> None:
        node = IsNumeric(name="test")
        ctx = Mock(spec=Context)
        with pytest.raises(ValueError, match="Value 'hello' is not numeric."):
            node.handle_str("hello", ctx)

    def test_is_numeric_empty_string(self) -> None:
        node = IsNumeric(name="test")
        ctx = Mock(spec=Context)
        with pytest.raises(ValueError, match="Value '' is not numeric."):
            node.handle_str("", ctx)

    def test_is_numeric_alphanumeric_string(self) -> None:
        node = IsNumeric(name="test")
        ctx = Mock(spec=Context)
        with pytest.raises(ValueError, match="Value '12abc' is not numeric."):
            node.handle_str("12abc", ctx)


class TestIsNumericCLI:
    """CLI-level tests for is_numeric decorator."""

    def test_is_numeric_valid_value(self, cli_runner: CliRunner) -> None:
        """Test is_numeric passes with a valid numeric string."""

        @command()
        @argument("value")
        @check.is_numeric()
        def cmd(value: str) -> None:
            click.echo(value)

        result = cli_runner.invoke(cmd, ["123"])
        assert result.exit_code == 0
        assert result.output == "123\n"

    def test_is_numeric_valid_float(self, cli_runner: CliRunner) -> None:
        """Test is_numeric passes with a float string."""

        @command()
        @argument("value")
        @check.is_numeric()
        def cmd(value: str) -> None:
            click.echo(value)

        result = cli_runner.invoke(cmd, ["3.14"])
        assert result.exit_code == 0
        assert result.output == "3.14\n"

    def test_is_numeric_invalid_value(self, cli_runner: CliRunner) -> None:
        """Test is_numeric fails with a non-numeric string."""

        @command()
        @argument("value")
        @check.is_numeric()
        def cmd(value: str) -> None:
            click.echo(value)

        result = cli_runner.invoke(cmd, ["notanumber"])
        assert result.exit_code != 0
        assert "Value 'notanumber' is not numeric." in result.output
