"""Tests for the `convert_energy` decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert.convert_energy import convert_energy


def test_convert_energy_metric() -> None:
    """Test converting metric energy units."""

    @command()
    @argument("energy", type=float)
    @convert_energy(from_unit="kJ", to_unit="J")
    def cli(energy: float) -> None:
        click.echo(f"{energy}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_energy_watt_hour() -> None:
    """Test converting watt-hour energy units."""

    @command()
    @argument("energy", type=float)
    @convert_energy(from_unit="kWh", to_unit="J")
    def cli(energy: float) -> None:
        click.echo(f"{energy}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 kWh = 3.6e6 J
    assert result.output.strip() == "3600000.0"


def test_convert_energy_calorie() -> None:
    """Test converting calorie energy units."""

    @command()
    @argument("energy", type=float)
    @convert_energy(from_unit="kcal", to_unit="cal")
    def cli(energy: float) -> None:
        click.echo(f"{energy}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_energy_mixed() -> None:
    """Test converting between different energy units."""

    @command()
    @argument("energy", type=float)
    @convert_energy(from_unit="Wh", to_unit="kJ")
    def cli(energy: float) -> None:
        click.echo(f"{energy}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 Wh = 3600 J = 3.6 kJ
    assert result.output.strip() == "3.6"


def test_convert_energy_invalid_unit() -> None:
    """Test converting with invalid units."""
    try:

        @command()
        @argument("energy", type=float)
        @convert_energy(from_unit="invalid", to_unit="J")  # type: ignore
        def cli(energy: float) -> None:  # type: ignore
            pass

    except ValueError as e:
        assert "Unknown unit 'invalid'" in str(e)
