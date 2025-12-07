import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert import convert_bits


def test_convert_bits_decimal() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="kB", to_unit="B")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 kB = 1000 B
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_bits_binary() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="KiB", to_unit="B")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 KiB = 1024 B
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1024.0"


def test_convert_bits_mixed() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="KiB", to_unit="kB")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 KiB = 1024 B = 1.024 kB
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.024"


def test_convert_bits_large() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="GB", to_unit="MB")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 GB = 1000 MB
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_bits_large_binary() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="GiB", to_unit="MiB")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 GiB = 1024 MiB
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1024.0"


def test_convert_bits_byte_to_bit() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="B", to_unit="b")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 B = 8 b
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "8.0"


def test_convert_bits_bit_to_byte() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="b", to_unit="B")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 8 b = 1 B
    result = runner.invoke(cli, ["8"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.0"


def test_convert_bits_kb_to_b() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="kb", to_unit="b")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 kb = 1000 b
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_bits_mb_to_kb() -> None:
    @command()
    @argument("value", type=float)
    @convert_bits(from_unit="Mb", to_unit="kb")
    def cli(value: float) -> None:
        click.echo(f"{value}")

    runner = CliRunner()
    # 1 Mb = 1000 kb
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"
