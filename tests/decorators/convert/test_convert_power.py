"""Tests for the `convert_power` decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert.convert_power import convert_power


def test_convert_power_metric() -> None:
    """Test converting metric power units."""

    @command()
    @argument("power", type=float)
    @convert_power(from_unit="kW", to_unit="W")
    def cli(power: float) -> None:
        click.echo(f"{power}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "1000.0"


def test_convert_power_mechanical() -> None:
    """Test converting mechanical power units."""

    @command()
    @argument("power", type=float)
    @convert_power(from_unit="hp", to_unit="W")
    def cli(power: float) -> None:
        click.echo(f"{power}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 hp = 745.69987158227022 W
    assert result.output.strip() == "745.6998715822702"


def test_convert_power_logarithmic_dbw() -> None:
    """Test converting logarithmic power units (dBW)."""

    @command()
    @argument("power", type=float)
    @convert_power(from_unit="dBW", to_unit="W")
    def cli(power: float) -> None:
        click.echo(f"{power}")

    runner = CliRunner()
    result = runner.invoke(cli, ["0"])
    assert result.exit_code == 0
    # 0 dBW = 1 W
    assert result.output.strip() == "1.0"

    result = runner.invoke(cli, ["10"])
    assert result.exit_code == 0
    # 10 dBW = 10 W
    assert result.output.strip() == "10.0"


def test_convert_power_logarithmic_dbm() -> None:
    """Test converting logarithmic power units (dBm)."""

    @command()
    @argument("power", type=float)
    @convert_power(from_unit="dBm", to_unit="W")
    def cli(power: float) -> None:
        click.echo(f"{power}")

    runner = CliRunner()
    result = runner.invoke(cli, ["30"])
    assert result.exit_code == 0
    # 30 dBm = 1 W
    assert result.output.strip() == "1.0"


def test_convert_power_mixed() -> None:
    """Test converting between different power units."""

    @command()
    @argument("power", type=float)
    @convert_power(from_unit="hp", to_unit="kW")
    def cli(power: float) -> None:
        click.echo(f"{power}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 hp = 0.74569987158227022 kW
    assert result.output.strip() == "0.7456998715822702"


def test_convert_power_invalid_unit() -> None:
    """Test converting with invalid units."""
    try:

        @command()
        @argument("power", type=float)
        @convert_power(from_unit="invalid", to_unit="W")  # type: ignore
        def cli(power: float) -> None:  # type: ignore
            pass

    except ValueError as e:
        assert "Unknown unit 'invalid'" in str(e)


def test_convert_power_negative_log() -> None:
    """Test converting negative power to logarithmic units."""
    try:

        @command()
        @argument("power", type=float)
        @convert_power(from_unit="W", to_unit="dBW")
        def cli(power: float) -> None:
            pass

        runner = CliRunner()
        runner.invoke(cli, ["-1"])
    except ValueError as e:
        assert "Power must be positive for logarithmic conversion" in str(e)
