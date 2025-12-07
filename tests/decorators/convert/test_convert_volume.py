import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_volume


def test_convert_volume_metric() -> None:
    @command()
    @argument("value", type=float)
    @convert_volume(from_unit="L", to_unit="mL")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 L = 1000 mL
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_volume_us_liquid() -> None:
    @command()
    @argument("value", type=float)
    @convert_volume(from_unit="gal", to_unit="qt")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 gal = 4 qt
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "4.0"


def test_convert_volume_imperial() -> None:
    @command()
    @argument("value", type=float)
    @convert_volume(from_unit="imp_gal", to_unit="imp_pt")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 imp_gal = 8 imp_pt
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "8.0"


def test_convert_volume_cooking() -> None:
    @command()
    @argument("value", type=float)
    @convert_volume(from_unit="tbsp", to_unit="tsp")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 tbsp = 3 tsp
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "3.0"


def test_convert_volume_mixed() -> None:
    @command()
    @argument("value", type=float)
    @convert_volume(from_unit="gal", to_unit="L")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 gal = 3.785411784 L
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(3.785411784)


def test_convert_volume_swedish() -> None:
    @command()
    @argument("value", type=float)
    @convert_volume(from_unit="msk", to_unit="tsk")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 msk (15ml) = 3 tsk (5ml)
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "3.0"
