"""Tests for multiply decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.multiply import multiply


class TestMultiply:
    """Test multiply decorator."""

    def test_multiply(self, cli_runner: CliRunner) -> None:
        """Test multiply decorator."""

        @command()
        @option("val", type=int)
        @multiply(5)
        def cmd(val: int) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10"])
        assert result.exit_code == 0
        assert "Value: 50" in result.output

    def test_multiply_str(self, cli_runner: CliRunner) -> None:
        """Test multiply decorator with string."""

        @command()
        @option("val")
        @multiply(3)
        def cmd(val: str) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "abc"])
        assert result.exit_code == 0
        assert "Value: abcabcabc" in result.output
