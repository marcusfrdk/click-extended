import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_json() -> None:
    @command()
    @argument("value")
    @check.is_json()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ['{"key": "value"}'])
    assert result.exit_code == 0
    assert result.output == '{"key": "value"}\n'

    result = runner.invoke(cli, ["not-json"])
    assert result.exit_code != 0
    assert "Value 'not-json' is not valid JSON." in result.output
