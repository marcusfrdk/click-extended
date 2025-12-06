import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_regex() -> None:
    @command()
    @argument("value")
    @check.regex(r"^\d{3}$")
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["123"])
    assert result.exit_code == 0
    assert result.output == "123\n"

    result = runner.invoke(cli, ["abc"])
    assert result.exit_code != 0
    assert "Value 'abc' does not match any of the patterns" in result.output
