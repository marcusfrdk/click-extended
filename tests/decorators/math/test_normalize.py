"""Tests for the `normalize` decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators.math.normalize import normalize


def test_normalize_default() -> None:
    """Test normalizing to 0-1."""

    @command()
    @argument("val", type=float)
    @normalize(min_val=0, max_val=100)
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["50"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.5"


def test_normalize_custom_range() -> None:
    """Test normalizing to custom range."""

    @command()
    @argument("val", type=float)
    @normalize(min_val=0, max_val=100, new_min=10, new_max=20)
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["50"])
    assert result.exit_code == 0
    # 50 in 0-100 is 0.5. 0.5 in 10-20 is 15.
    assert result.output.strip() == "15.0"


def test_normalize_out_of_bounds() -> None:
    """Test normalizing value outside input range."""

    @command()
    @argument("val", type=float)
    @normalize(min_val=0, max_val=100)
    def cli(val: float) -> None:
        click.echo(f"{val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["150"])
    assert result.exit_code == 0
    # 150 in 0-100 is 1.5.
    assert result.output.strip() == "1.5"
