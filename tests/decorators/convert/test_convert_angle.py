"""Tests for the `convert_angle` decorator."""

import math

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert.convert_angle import convert_angle


def test_convert_angle_metric() -> None:
    """Test converting metric angle units."""

    @command()
    @argument("angle", type=float)
    @convert_angle(from_unit="grad", to_unit="deg")
    def cli(angle: float) -> None:
        click.echo(f"{angle}")

    runner = CliRunner()
    result = runner.invoke(cli, ["100"])
    assert result.exit_code == 0
    # 100 grad = 90 deg
    assert result.output.strip() == "90.0"


def test_convert_angle_radian() -> None:
    """Test converting radian angle units."""

    @command()
    @argument("angle", type=float)
    @convert_angle(from_unit="deg", to_unit="rad")
    def cli(angle: float) -> None:
        click.echo(f"{angle}")

    runner = CliRunner()
    result = runner.invoke(cli, ["180"])
    assert result.exit_code == 0
    # 180 deg = pi rad
    # Use approx comparison due to float precision in output
    output = float(result.output.strip())
    assert math.isclose(output, math.pi, rel_tol=1e-9)


def test_convert_angle_turn() -> None:
    """Test converting turn angle units."""

    @command()
    @argument("angle", type=float)
    @convert_angle(from_unit="turn", to_unit="deg")
    def cli(angle: float) -> None:
        click.echo(f"{angle}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 turn = 360 deg
    assert result.output.strip() == "360.0"


def test_convert_angle_arc() -> None:
    """Test converting arc angle units."""

    @command()
    @argument("angle", type=float)
    @convert_angle(from_unit="arcmin", to_unit="deg")
    def cli(angle: float) -> None:
        click.echo(f"{angle}")

    runner = CliRunner()
    result = runner.invoke(cli, ["60"])
    assert result.exit_code == 0
    # 60 arcmin = 1 deg
    assert result.output.strip() == "1.0"


def test_convert_angle_mixed() -> None:
    """Test converting between different angle units."""

    @command()
    @argument("angle", type=float)
    @convert_angle(from_unit="turn", to_unit="rad")
    def cli(angle: float) -> None:
        click.echo(f"{angle}")

    runner = CliRunner()
    result = runner.invoke(cli, ["0.5"])
    assert result.exit_code == 0
    # 0.5 turn = 180 deg = pi rad
    output = float(result.output.strip())
    assert math.isclose(output, math.pi, rel_tol=1e-9)


def test_convert_angle_invalid_unit() -> None:
    """Test converting with invalid units."""
    try:

        @command()
        @argument("angle", type=float)
        @convert_angle(from_unit="invalid", to_unit="deg")  # type: ignore
        def cli(angle: float) -> None:  # type: ignore
            pass

    except ValueError as e:
        assert "Unknown unit 'invalid'" in str(e)
