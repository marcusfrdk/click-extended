import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_ipv6() -> None:
    @command()
    @argument("value")
    @check.is_ipv6()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"])
    assert result.exit_code == 0
    assert result.output == "2001:0db8:85a3:0000:0000:8a2e:0370:7334\n"

    result = runner.invoke(cli, ["not-an-ipv6"])
    assert result.exit_code != 0
    assert "Value 'not-an-ipv6' is not a valid IPv6 address." in result.output
