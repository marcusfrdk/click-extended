"""Tests for power decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.power import power


class TestPower:
    """Test power decorator."""

    def test_power(self, cli_runner: CliRunner) -> None:
        """Test power decorator."""

        @command()
        @option("val", type=int)
        @power(2)
        def cmd(val: int) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10"])
        assert result.exit_code == 0
        assert "Value: 100" in result.output
