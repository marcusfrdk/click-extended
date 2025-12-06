"""Tests for floor decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.floor import floor


class TestFloor:
    """Test floor decorator."""

    def test_floor(self, cli_runner: CliRunner) -> None:
        """Test floor decorator."""

        @command()
        @option("val", type=float)
        @floor()
        def cmd(val: int) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10.9"])
        assert result.exit_code == 0
        assert "Value: 10" in result.output
