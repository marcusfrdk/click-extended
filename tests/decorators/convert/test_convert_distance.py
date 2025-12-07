import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_distance


def test_convert_distance_metric() -> None:
    @command()
    @argument("value", type=float)
    @convert_distance(from_unit="km", to_unit="m")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 km = 1000 m
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_distance_imperial() -> None:
    @command()
    @argument("value", type=float)
    @convert_distance(from_unit="ft", to_unit="in")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 ft = 12 in
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "12.0"


def test_convert_distance_mixed() -> None:
    @command()
    @argument("value", type=float)
    @convert_distance(from_unit="in", to_unit="cm")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 in = 2.54 cm
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "2.54"


def test_convert_distance_astronomical() -> None:
    @command()
    @argument("value", type=float)
    @convert_distance(from_unit="ly", to_unit="m")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 ly = 9460730472580800 m
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "9460730472580800.0"


def test_convert_distance_swedish_mile() -> None:
    @command()
    @argument("value", type=float)
    @convert_distance(from_unit="mil", to_unit="km")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 mil = 10 km
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "10.0"
