"""Tests for the `to_percent` decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.math.to_percent import to_percent


def test_to_percent_string() -> None:
    """Test converting string percentage."""

    @command()
    @argument("val")
    @to_percent()
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["50%"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.5"


def test_to_percent_string_no_symbol() -> None:
    """Test converting string percentage without symbol."""

    @command()
    @argument("val")
    @to_percent()
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["50"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.5"


def test_to_percent_float() -> None:
    """Test converting float percentage."""

    @command()
    @argument("val", type=float)
    @to_percent()
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["50"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.5"


def test_to_percent_int() -> None:
    """Test converting int percentage."""

    @command()
    @argument("val", type=int)
    @to_percent()
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["50"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.5"


def test_to_percent_invalid() -> None:
    """Test converting invalid percentage."""
    try:

        @command()
        @argument("val")
        @to_percent()
        def cli(val: float) -> None:
            pass

        runner = CliRunner()
        runner.invoke(cli, ["invalid"])
    except ValueError as e:
        assert "Cannot convert 'invalid' to percent." in str(e)
