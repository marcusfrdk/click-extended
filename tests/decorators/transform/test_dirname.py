"""Tests for the `dirname` decorator."""

from pathlib import Path

import click
from click.testing import CliRunner

from click_extended import argument, command, option
from click_extended.decorators.transform.dirname import dirname
from click_extended.decorators.transform.to_path import to_path


def test_dirname_str() -> None:
    """Test that `dirname` works with strings."""

    @command()
    @option("--path")
    @dirname()
    def cli(path: Path) -> None:
        click.echo(path)

    runner = CliRunner()
    result = runner.invoke(cli, ["--path", "/foo/bar/baz.txt"])
    assert result.exit_code == 0
    assert result.output == "/foo/bar\n"


def test_dirname_path() -> None:
    """Test that `dirname` works with Path objects."""

    @command()
    @option("--path")
    @to_path(exists=False)
    @dirname()
    def cli(path: Path) -> None:
        click.echo(path)

    runner = CliRunner()
    result = runner.invoke(cli, ["--path", "/foo/bar/baz.txt"])
    assert result.exit_code == 0
    assert result.output == "/foo/bar\n"


def test_dirname_argument() -> None:
    """Test that `dirname` works with arguments."""

    @command()
    @argument("path")
    @dirname()
    def cli(path: Path) -> None:
        click.echo(path)

    runner = CliRunner()
    result = runner.invoke(cli, ["/foo/bar/baz.txt"])
    assert result.exit_code == 0
    assert result.output == "/foo/bar\n"
