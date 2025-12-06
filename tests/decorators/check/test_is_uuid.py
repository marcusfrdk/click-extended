import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_uuid() -> None:
    @command()
    @argument("value")
    @check.is_uuid()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["123e4567-e89b-12d3-a456-426614174000"])
    assert result.exit_code == 0
    assert result.output == "123e4567-e89b-12d3-a456-426614174000\n"

    result = runner.invoke(cli, ["not-a-uuid"])
    assert result.exit_code != 0
    assert "Value 'not-a-uuid' is not a valid UUID." in result.output
