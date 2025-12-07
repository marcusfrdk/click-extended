"""Tests for the `divisible_by` decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.check.divisible_by import divisible_by


def test_divisible_by_int() -> None:
    """Test checking divisibility for integers."""

    @command()
    @argument("val", type=int)
    @divisible_by(n=5)
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["10"])
    assert result.exit_code == 0
    assert result.output.strip() == "10"

    result = runner.invoke(cli, ["12"])
    assert result.exit_code != 0
    assert "Value '12' is not divisible by '5'." in result.output


def test_divisible_by_float() -> None:
    """Test checking divisibility for floats."""

    @command()
    @argument("val", type=float)
    @divisible_by(n=0.5)
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1.5"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.5"

    result = runner.invoke(cli, ["1.2"])
    assert result.exit_code != 0
    assert "Value '1.2' is not divisible by '0.5'." in result.output
