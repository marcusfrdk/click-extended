"""Tests for sqrt decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.sqrt import sqrt


class TestSqrt:
    """Test sqrt decorator."""

    def test_sqrt(self, cli_runner: CliRunner) -> None:
        """Test sqrt decorator."""

        @command()
        @option("val", type=int)
        @sqrt()
        def cmd(val: float) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "16"])
        assert result.exit_code == 0
        assert "Value: 4.0" in result.output

    def test_sqrt_negative(self, cli_runner: CliRunner) -> None:
        """Test sqrt decorator with negative number."""

        @command()
        @option("val", type=int)
        @sqrt()
        def cmd(val: complex) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "-16"])
        assert result.exit_code == 0
        assert "Value: 4j" in result.output
