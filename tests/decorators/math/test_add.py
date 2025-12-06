"""Tests for add decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.math.add import add


class TestAdd:
    """Test add decorator."""

    def test_add(self, cli_runner: CliRunner) -> None:
        """Test add decorator."""

        @command()
        @option("val", type=int)
        @add(5)
        def cmd(val: int) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "10"])
        assert result.exit_code == 0
        assert "Value: 15" in result.output

    def test_add_str(self, cli_runner: CliRunner) -> None:
        """Test add decorator with string."""

        @command()
        @option("val")
        @add(" world")
        def cmd(val: str) -> None:
            click.echo(f"Value: {val}")

        result = cli_runner.invoke(cmd, ["--val", "hello"])
        assert result.exit_code == 0
        assert "Value: hello world" in result.output
