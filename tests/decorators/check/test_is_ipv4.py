import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_ipv4() -> None:
    @command()
    @argument("value")
    @check.is_ipv4()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["192.168.1.1"])
    assert result.exit_code == 0
    assert result.output == "192.168.1.1\n"

    result = runner.invoke(cli, ["256.256.256.256"])
    assert result.exit_code != 0
    assert (
        "Value '256.256.256.256' is not a valid IPv4 address." in result.output
    )
