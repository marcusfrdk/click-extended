import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_hex_color() -> None:
    @command()
    @argument("value")
    @check.is_hex_color()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["#FFFFFF"])
    assert result.exit_code == 0
    assert result.output == "#FFFFFF\n"

    result = runner.invoke(cli, ["FFFFFF"])
    assert result.exit_code == 0
    assert result.output == "FFFFFF\n"

    result = runner.invoke(cli, ["#FFF"])
    assert result.exit_code == 0
    assert result.output == "#FFF\n"

    result = runner.invoke(cli, ["#FFFFFFFF"])
    assert result.exit_code == 0
    assert result.output == "#FFFFFFFF\n"

    result = runner.invoke(cli, ["not-a-color"])
    assert result.exit_code != 0
    assert "Value 'not-a-color' is not a valid hex color." in result.output
