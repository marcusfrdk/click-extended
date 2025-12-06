import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_port() -> None:
    @command()
    @argument("value", type=int)
    @check.is_port()
    def cli(value: int) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["8080"])
    assert result.exit_code == 0
    assert result.output == "8080\n"

    result = runner.invoke(cli, ["70000"])
    assert result.exit_code != 0
    assert (
        "Value '70000' is not a valid port number (1-65535)." in result.output
    )

    result = runner.invoke(cli, ["--", "-1"])
    assert result.exit_code != 0
    assert "Value '-1' is not a valid port number (1-65535)." in result.output
