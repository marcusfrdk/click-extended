import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_byte_size


def test_convert_byte_size_decimal() -> None:
    @command()
    @argument("value", type=float)
    @convert_byte_size(from_unit="kB", to_unit="B")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 kB = 1000 B
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_byte_size_binary() -> None:
    @command()
    @argument("value", type=float)
    @convert_byte_size(from_unit="KiB", to_unit="B")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 KiB = 1024 B
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1024.0"


def test_convert_byte_size_mixed() -> None:
    @command()
    @argument("value", type=float)
    @convert_byte_size(from_unit="KiB", to_unit="kB")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 KiB = 1024 B = 1.024 kB
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.024"


def test_convert_byte_size_large() -> None:
    @command()
    @argument("value", type=float)
    @convert_byte_size(from_unit="GB", to_unit="MB")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 GB = 1000 MB
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_byte_size_large_binary() -> None:
    @command()
    @argument("value", type=float)
    @convert_byte_size(from_unit="GiB", to_unit="MiB")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 GiB = 1024 MiB
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1024.0"
