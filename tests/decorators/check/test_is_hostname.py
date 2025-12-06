import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_hostname() -> None:
    @command()
    @argument("value")
    @check.is_hostname()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["example.com"])
    assert result.exit_code == 0
    assert result.output == "example.com\n"

    result = runner.invoke(cli, ["localhost"])
    assert result.exit_code == 0
    assert result.output == "localhost\n"

    result = runner.invoke(cli, ["invalid_hostname"])
    assert result.exit_code != 0
    assert "Value 'invalid_hostname' is not a valid hostname." in result.output
