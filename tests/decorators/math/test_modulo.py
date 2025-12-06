"""Tests for modulo decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.modulo import modulo


class TestModulo:
    """Test modulo decorator."""

    def test_modulo(self, cli_runner: CliRunner) -> None:
        """Test modulo decorator."""

        @command()
        @option("val", type=int)
        @modulo(3)
        def cmd(val: int) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10"])
        assert result.exit_code == 0
        assert "Value: 1" in result.output
