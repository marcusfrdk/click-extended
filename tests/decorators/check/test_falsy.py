"""Tests for the falsy decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.check.falsy import falsy


class TestFalsy:
    """Test falsy decorator."""

    def test_falsy_valid(self, cli_runner: CliRunner) -> None:
        """Test falsy with valid value."""

        @command()
        @option("val", default="")
        @falsy()
        def cmd(val: str) -> None:
            click.echo(f"Value: '{val}'")

        result = cli_runner.invoke(cmd, ["--val", ""])
        assert result.exit_code == 0
        assert "Value: ''" in result.output

    def test_falsy_invalid(self, cli_runner: CliRunner) -> None:
        """Test falsy with invalid value."""

        @command()
        @option("val", default=None)
        @falsy()
        def cmd(val: str | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--val", "something"])
        assert result.exit_code != 0
        assert "Value 'something' is not falsy." in result.output
