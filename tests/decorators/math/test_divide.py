"""Tests for divide decorator."""

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.divide import divide


class TestDivide:
    """Test divide decorator."""

    def test_divide(self, cli_runner: CliRunner) -> None:
        """Test divide decorator."""

        @command()
        @option("val", type=int)
        @divide(2)
        def cmd(val: float) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10"])
        assert result.exit_code == 0
        assert "Value: 5.0" in result.output

    def test_divide_zero(self, cli_runner: CliRunner) -> None:
        """Test divide by zero."""

        @command()
        @option("val", type=int)
        @divide(0)
        def cmd(val: float) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--val", "10"])
        assert result.exit_code != 0
        # Click wraps exceptions in SystemExit(1) when not in standalone mode sometimes,
        # or just prints the exception. Let's check the output/exception string.
        assert (
            "division by zero" in str(result.exception)
            or "division by zero" in result.output
        )
