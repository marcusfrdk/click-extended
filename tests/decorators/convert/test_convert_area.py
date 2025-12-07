"""Tests for the `convert_area` decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.convert.convert_area import convert_area


def test_convert_area_metric() -> None:
    """Test converting metric area units."""

    @command()
    @argument("area", type=float)
    @convert_area(from_unit="m2", to_unit="km2")
    def cli(area: float) -> None:
        click.echo(f"{area}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1000000"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.0"


def test_convert_area_imperial() -> None:
    """Test converting imperial area units."""

    @command()
    @argument("area", type=float)
    @convert_area(from_unit="acre", to_unit="ft2")
    def cli(area: float) -> None:
        click.echo(f"{area}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    # 1 acre = 43560 ft2
    assert result.output.strip() == "43560.0"


def test_convert_area_mixed() -> None:
    """Test converting between metric and imperial area units."""

    @command()
    @argument("area", type=float)
    @convert_area(from_unit="ha", to_unit="m2")
    def cli(area: float) -> None:
        click.echo(f"{area}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "10000.0"


def test_convert_area_small() -> None:
    """Test converting small area units."""

    @command()
    @argument("area", type=float)
    @convert_area(from_unit="cm2", to_unit="mm2")
    def cli(area: float) -> None:
        click.echo(f"{area}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "100.0"


def test_convert_area_historical() -> None:
    """Test converting historical area units."""

    @command()
    @argument("area", type=float)
    @convert_area(from_unit="tunnland", to_unit="m2")
    def cli(area: float) -> None:
        click.echo(f"{area}")

    runner = CliRunner()
    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 0
    assert result.output.strip() == "4936.4"


def test_convert_area_invalid_unit() -> None:
    """Test converting with invalid units."""
    try:

        @command()
        @argument("area", type=float)
        @convert_area(from_unit="invalid", to_unit="m2")  # type: ignore
        def cli(area: float) -> None:  # type: ignore
            pass

    except ValueError as e:
        assert "Unknown unit 'invalid'" in str(e)
