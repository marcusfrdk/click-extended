import re

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


def test_regex_multiple_patterns() -> None:
    """Test regex with multiple patterns."""

    @command()
    @argument("value")
    @check.regex(r"^\d{3}$", r"^[a-z]{3}$")
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()
    result = runner.invoke(cli, ["123"])
    assert result.exit_code == 0
    assert result.output == "123\n"

    result = runner.invoke(cli, ["abc"])
    assert result.exit_code == 0
    assert result.output == "abc\n"

    result = runner.invoke(cli, ["ABC"])
    assert result.exit_code != 0
    assert "Value 'ABC' does not match any of the patterns" in result.output


def test_regex_with_flags_ignorecase() -> None:
    """Test regex with re.IGNORECASE flag."""

    @command()
    @argument("value")
    @check.regex(r"^hello$", flags=re.IGNORECASE)
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()

    # Should match lowercase
    result = runner.invoke(cli, ["hello"])
    assert result.exit_code == 0
    assert result.output == "hello\n"

    # Should match uppercase due to IGNORECASE flag
    result = runner.invoke(cli, ["HELLO"])
    assert result.exit_code == 0
    assert result.output == "HELLO\n"

    # Should match mixed case
    result = runner.invoke(cli, ["HeLLo"])
    assert result.exit_code == 0
    assert result.output == "HeLLo\n"

    # Should not match different word
    result = runner.invoke(cli, ["world"])
    assert result.exit_code != 0
    assert "Value 'world' does not match any of the patterns" in result.output


def test_regex_with_compiled_pattern() -> None:
    """Test regex with pre-compiled Pattern object."""
    pattern = re.compile(r"^\d{3}-\d{4}$")

    @command()
    @argument("value")
    @check.regex(pattern)
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()

    result = runner.invoke(cli, ["123-4567"])
    assert result.exit_code == 0
    assert result.output == "123-4567\n"

    result = runner.invoke(cli, ["123-456"])
    assert result.exit_code != 0
    assert "Value '123-456' does not match any of the patterns" in result.output


def test_regex_with_compiled_pattern_with_flags() -> None:
    """Test regex with pre-compiled Pattern object that has flags."""
    pattern = re.compile(r"^test$", re.IGNORECASE)

    @command()
    @argument("value")
    @check.regex(pattern)
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()

    # Compiled pattern already has IGNORECASE
    result = runner.invoke(cli, ["TEST"])
    assert result.exit_code == 0
    assert result.output == "TEST\n"

    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 0
    assert result.output == "test\n"


def test_regex_mixed_string_and_compiled() -> None:
    """Test regex with mix of string and compiled patterns."""
    compiled = re.compile(r"^\d{3}$")

    @command()
    @argument("value")
    @check.regex(r"^[a-z]{3}$", compiled)
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()

    # Should match string pattern
    result = runner.invoke(cli, ["abc"])
    assert result.exit_code == 0
    assert result.output == "abc\n"

    # Should match compiled pattern
    result = runner.invoke(cli, ["123"])
    assert result.exit_code == 0
    assert result.output == "123\n"

    # Should not match either
    result = runner.invoke(cli, ["ABC"])
    assert result.exit_code != 0
    assert "Value 'ABC' does not match any of the patterns" in result.output


def test_regex_with_multiline_flag() -> None:
    """Test regex with re.MULTILINE flag."""

    @command()
    @argument("value")
    @check.regex(r"^test$", flags=re.MULTILINE)
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()

    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 0
    assert result.output == "test\n"


def test_regex_with_multiple_flags() -> None:
    """Test regex with multiple flags combined."""

    @command()
    @argument("value")
    @check.regex(r"^hello world$", flags=re.IGNORECASE | re.MULTILINE)
    def cli(value: str) -> None:
        click.echo(value)

    runner = CliRunner()

    result = runner.invoke(cli, ["HELLO WORLD"])
    assert result.exit_code == 0
    assert result.output == "HELLO WORLD\n"

    result = runner.invoke(cli, ["hello world"])
    assert result.exit_code == 0
    assert result.output == "hello world\n"


def test_regex_email_pattern() -> None:
    """Test regex with email pattern."""

    @command()
    @argument("email")
    @check.regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    def cli(email: str) -> None:
        click.echo(email)

    runner = CliRunner()

    result = runner.invoke(cli, ["user@example.com"])
    assert result.exit_code == 0
    assert result.output == "user@example.com\n"

    result = runner.invoke(cli, ["test.user+tag@sub.domain.co.uk"])
    assert result.exit_code == 0
    assert result.output == "test.user+tag@sub.domain.co.uk\n"

    result = runner.invoke(cli, ["invalid-email"])
    assert result.exit_code != 0
    assert (
        "Value 'invalid-email' does not match any of the patterns"
        in result.output
    )
