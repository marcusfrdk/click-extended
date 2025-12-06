import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.decorators import check


def test_mac_address() -> None:
    @command()
    @argument("value")
    @check.is_mac_address()
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["00:1A:2B:3C:4D:5E"])
    assert result.exit_code == 0
    assert result.output == "00:1A:2B:3C:4D:5E\n"

    result = runner.invoke(cli, ["00-1A-2B-3C-4D-5E"])
    assert result.exit_code == 0
    assert result.output == "00-1A-2B-3C-4D-5E\n"

    result = runner.invoke(cli, ["001A.2B3C.4D5E"])
    assert result.exit_code == 0
    assert result.output == "001A.2B3C.4D5E\n"

    result = runner.invoke(cli, ["not-a-mac"])
    assert result.exit_code != 0
    assert "Value 'not-a-mac' is not a valid MAC address." in result.output
