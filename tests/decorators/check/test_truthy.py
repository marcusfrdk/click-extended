"""Tests for the truthy decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.check.truthy import truthy


class TestTruthy:
    """Test truthy decorator."""

    def test_truthy_valid(self, cli_runner: CliRunner) -> None:
        """Test truthy with valid value."""

        @command()
        @option("val", default=None)
        @truthy()
        def cmd(val: str | None) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "something"])
        assert result.exit_code == 0
        assert "Value: something" in result.output

    def test_truthy_invalid(self, cli_runner: CliRunner) -> None:
        """Test truthy with invalid value."""

        @command()
        @option("val", default="")
        @truthy()
        def cmd(val: str) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--val", ""])
        assert result.exit_code != 0
        assert "Value '' is not truthy." in result.output
