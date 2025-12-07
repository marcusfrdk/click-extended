"""Tests for the `convert_pressure` decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert.convert_pressure import convert_pressure


def test_convert_pressure_metric() -> None:
    """Test converting metric pressure units."""

    @command()
    @argument("pressure", type=float)
    @convert_pressure(from_unit="kPa", to_unit="Pa")
    def cli(pressure: float) -> None:
        click.echo(f"{pressure}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_pressure_imperial() -> None:
    """Test converting imperial pressure units."""

    @command()
    @argument("pressure", type=float)
    @convert_pressure(from_unit="psi", to_unit="Pa")
    def cli(pressure: float) -> None:
        click.echo(f"{pressure}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 psi = 6894.757293168 Pa
    assert result.output.strip() == "6894.757293168"


def test_convert_pressure_atmosphere() -> None:
    """Test converting atmosphere pressure units."""

    @command()
    @argument("pressure", type=float)
    @convert_pressure(from_unit="atm", to_unit="Pa")
    def cli(pressure: float) -> None:
        click.echo(f"{pressure}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "101325.0"


def test_convert_pressure_mixed() -> None:
    """Test converting between different pressure units."""

    @command()
    @argument("pressure", type=float)
    @convert_pressure(from_unit="bar", to_unit="kPa")
    def cli(pressure: float) -> None:
        click.echo(f"{pressure}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 bar = 100 kPa
    assert result.output.strip() == "100.0"


def test_convert_pressure_invalid_unit() -> None:
    """Test converting with invalid units."""
    try:

        @command()
        @argument("pressure", type=float)
        @convert_pressure(from_unit="invalid", to_unit="Pa")  # type: ignore
        def cli(pressure: float) -> None:  # type: ignore
            pass

    except ValueError as e:
        assert "Unknown unit 'invalid'" in str(e)
