import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_temperature


def test_convert_temperature_c_to_f() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="C", to_unit="F")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 0C -> 32F
    result = runner.invoke(cli, ["0"])
    assert result.exit_code == 0
    assert result.output.strip() == "32.0"

    # 100C -> 212F
    result = runner.invoke(cli, ["100"])
    assert result.exit_code == 0
    assert result.output.strip() == "212.0"


def test_convert_temperature_f_to_c() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="F", to_unit="C")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 32F -> 0C
    result = runner.invoke(cli, ["32"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.0"


def test_convert_temperature_c_to_k() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="C", to_unit="K")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 0C -> 273.15K
    result = runner.invoke(cli, ["0"])
    assert result.exit_code == 0
    assert result.output.strip() == "273.15"


def test_convert_temperature_k_to_c() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="K", to_unit="C")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 273.15K -> 0C
    result = runner.invoke(cli, ["273.15"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(0.0)


def test_convert_temperature_c_to_r() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="C", to_unit="R")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 0C -> 491.67R
    result = runner.invoke(cli, ["0"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(491.67)


def test_convert_temperature_c_to_re() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="C", to_unit="Re")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 100C -> 80Re
    result = runner.invoke(cli, ["100"])
    assert result.exit_code == 0
    assert result.output.strip() == "80.0"


def test_convert_temperature_c_to_de() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="C", to_unit="De")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 100C -> 0De
    result = runner.invoke(cli, ["100"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.0"

    # 0C -> 150De
    result = runner.invoke(cli, ["0"])
    assert result.exit_code == 0
    assert result.output.strip() == "150.0"


def test_convert_temperature_absolute_zero() -> None:
    @command()
    @argument("value", type=float)
    @convert_temperature(from_unit="C", to_unit="K")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # -273.15C -> 0K (OK)
    result = runner.invoke(cli, ["--", "-273.15"])
    assert result.exit_code == 0
    assert float(result.output.strip()) == pytest.approx(0.0)

    # -274C -> Error
    result = runner.invoke(cli, ["--", "-274"])
    assert result.exit_code != 0
    assert "Temperature cannot be below absolute zero" in result.output
