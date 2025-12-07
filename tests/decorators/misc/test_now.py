"""Tests for the `now` decorator."""

from datetime import datetime

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.decorators.misc.now import now


def test_now_default_utc() -> None:
    """Test injecting current time in UTC."""

    @command()
    @now("current_time")
    def cli(current_time: datetime) -> None:
        click.echo(f"{current_time.tzinfo}")
        click.echo(f"{type(current_time).__name__}")

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "UTC" in result.output
    assert "datetime" in result.output


def test_now_specific_timezone() -> None:
    """Test injecting current time in specific timezone."""

    @command()
    @now("current_time", tz="Europe/Stockholm")
    def cli(current_time: datetime) -> None:
        click.echo(f"{current_time.tzinfo}")

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "Europe/Stockholm" in result.output


def test_now_invalid_timezone() -> None:
    """Test error handling for invalid timezone."""

    @command()
    @now("current_time", tz="Invalid/Timezone")
    def cli(current_time: datetime) -> None:
        pass

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code != 0
    assert (
        "Invalid timezone 'Invalid/Timezone'" in str(result.exception)
        or "Invalid timezone 'Invalid/Timezone'" in result.output
    )
