"""Tests for subtract decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.subtract import subtract


class TestSubtract:
    """Test subtract decorator."""

    def test_subtract(self, cli_runner: CliRunner) -> None:
        """Test subtract decorator."""

        @command()
        @option("val", type=int)
        @subtract(5)
        def cmd(val: int) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10"])
        assert result.exit_code == 0
        assert "Value: 5" in result.output
