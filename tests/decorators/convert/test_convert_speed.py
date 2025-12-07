import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_speed


def test_convert_speed_metric() -> None:
    @command()
    @argument("value", type=float)
    @convert_speed(from_unit="kmh", to_unit="mps")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 36 km/h = 10 m/s
    result = runner.invoke(cli, ["36"])
    assert result.exit_code == 0
    assert result.output.strip() == "10.0"


def test_convert_speed_imperial() -> None:
    @command()
    @argument("value", type=float)
    @convert_speed(from_unit="mph", to_unit="kmh")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 mph = 1.609344 km/h
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(1.609344)


def test_convert_speed_nautical() -> None:
    @command()
    @argument("value", type=float)
    @convert_speed(from_unit="kn", to_unit="kmh")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 knot = 1.852 km/h
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.852"


def test_convert_speed_mach() -> None:
    @command()
    @argument("value", type=float)
    @convert_speed(from_unit="mach", to_unit="mps")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 mach = 343 m/s
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "343.0"


def test_convert_speed_light() -> None:
    @command()
    @argument("value", type=float)
    @convert_speed(from_unit="c", to_unit="mps")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 c = 299792458 m/s
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "299792458.0"
