import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_weight


def test_convert_weight_mass_to_mass() -> None:
    @command()
    @argument("value", type=float)
    @convert_weight(from_unit="kg", to_unit="g")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1kg -> 1000g
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_weight_force_to_force() -> None:
    @command()
    @argument("value", type=float)
    @convert_weight(from_unit="kn", to_unit="n")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1kN -> 1000N
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_weight_mass_to_force() -> None:
    @command()
    @argument("value", type=float)
    @convert_weight(from_unit="kg", to_unit="n")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1kg * 9.80665 m/s^2 = 9.80665 N
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(9.80665)


def test_convert_weight_force_to_mass() -> None:
    @command()
    @argument("value", type=float)
    @convert_weight(from_unit="n", to_unit="kg")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 9.80665 N / 9.80665 m/s^2 = 1 kg
    result = runner.invoke(cli, ["9.80665"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(1.0)


def test_convert_weight_custom_gravity() -> None:
    @command()
    @argument("value", type=float)
    @convert_weight(from_unit="kg", to_unit="n", gravity=10.0)
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1kg * 10 m/s^2 = 10 N
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "10.0"


def test_convert_weight_lb_to_kg() -> None:
    @command()
    @argument("value", type=float)
    @convert_weight(from_unit="lb", to_unit="kg")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 lb = 0.45359237 kg
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(0.45359237)
