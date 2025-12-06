import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_url() -> None:
    @command()
    @argument("value")
    @check.is_url()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["https://example.com"])
    assert result.exit_code == 0
    assert result.output == "https://example.com\n"

    result = runner.invoke(cli, ["not-a-url"])
    assert result.exit_code != 0
    assert "Value 'not-a-url' is not a valid URL." in result.output
