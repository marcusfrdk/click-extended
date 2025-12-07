"""Tests for the `basename` decorator."""

from pathlib import Path

import click
from click.testing import CliRunner

from click_extended import argument, command, option
from click_extended.decorators.transform.basename import basename
from click_extended.decorators.transform.to_path import to_path


def test_basename_str() -> None:
    """Test that `basename` works with strings."""

    @command()
    @option("--path")
    @basename()
    def cli(path: Path) -> None:
        click.echo(path)

    runner = CliRunner()
    result = runner.invoke(cli, ["--path", "/foo/bar/baz.txt"])
    assert result.exit_code == 0
    assert result.output == "baz.txt\n"


def test_basename_path() -> None:
    """Test that `basename` works with Path objects."""

    @command()
    @option("--path")
    @to_path(exists=False)
    @basename()
    def cli(path: Path) -> None:
        click.echo(path)

    runner = CliRunner()
    result = runner.invoke(cli, ["--path", "/foo/bar/baz.txt"])
    assert result.exit_code == 0
    assert result.output == "baz.txt\n"


def test_basename_argument() -> None:
    """Test that `basename` works with arguments."""

    @command()
    @argument("path")
    @basename()
    def cli(path: Path) -> None:
        click.echo(path)

    runner = CliRunner()
    result = runner.invoke(cli, ["/foo/bar/baz.txt"])
    assert result.exit_code == 0
    assert result.output == "baz.txt\n"
