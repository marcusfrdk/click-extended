"""Tests for ceil decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.ceil import ceil


class TestCeil:
    """Test ceil decorator."""

    def test_ceil(self, cli_runner: CliRunner) -> None:
        """Test ceil decorator."""

        @command()
        @option("val", type=float)
        @ceil()
        def cmd(val: int) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10.1"])
        assert result.exit_code == 0
        assert "Value: 11" in result.output
