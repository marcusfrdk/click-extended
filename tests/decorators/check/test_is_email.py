import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_email() -> None:
    @command()
    @argument("value")
    @check.is_email()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["test@example.com"])
    assert result.exit_code == 0
    assert result.output == "test@example.com\n"

    result = runner.invoke(cli, ["not-an-email"])
    assert result.exit_code != 0
    assert "Value 'not-an-email' is not a valid email address" in result.output
