import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_time


def test_convert_time_numeric() -> None:
    @command()
    @argument("value", type=float)
    @convert_time(from_unit="m", to_unit="s")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    result = runner.invoke(cli, ["2"])
    assert result.exit_code == 0
    assert result.output.strip() == "120.0"


def test_convert_time_string() -> None:
    @command()
    @argument("value")
    @convert_time(from_unit="s", to_unit="m")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # "120s" -> 2m
    result = runner.invoke(cli, ["120s"])
    assert result.exit_code == 0
    assert result.output.strip() == "2.0"

    # "2m" -> 2m
    result = runner.invoke(cli, ["2m"])
    assert result.exit_code == 0
    assert result.output.strip() == "2.0"

    # "1h" -> 60m
    result = runner.invoke(cli, ["1h"])
    assert result.exit_code == 0
    assert result.output.strip() == "60.0"

    # "1m 30s" -> 1.5m
    result = runner.invoke(cli, ["1m 30s"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.5"


def test_convert_time_string_no_unit() -> None:
    @command()
    @argument("value")
    @convert_time(from_unit="m", to_unit="s")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    result = runner.invoke(cli, ["2"])
    assert result.exit_code == 0
    assert result.output.strip() == "120.0"


def test_convert_time_invalid_unit() -> None:
    @command()
    @argument("value")
    @convert_time(from_unit="s", to_unit="m")
    def cli(value: float) -> None:
        pass

    runner = CliRunner()
    result = runner.invoke(cli, ["10x"])
    assert result.exit_code != 0
    assert "Unknown unit 'x' in string." in result.output
