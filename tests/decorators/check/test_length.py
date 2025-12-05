"""Comprehensive tests for length decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.add.add_prefix import add_prefix
from click_extended.decorators.check.length import Length, length
from click_extended.decorators.check.starts_with import starts_with


class TestLengthInit:
    """Test Length class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_length_is_child_node(self) -> None:
        """Test that Length extends ChildNode."""
        node = Length(name="test")
        assert isinstance(node, ChildNode)

    def test_length_has_handle_str(self) -> None:
        """Test that Length implements handle_str method."""
        node = Length(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestLengthMinOnly:
    """Test length decorator with minimum length only."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_min_length_valid(self, cli_runner: CliRunner) -> None:
        """Test that string meeting minimum length passes."""

        @command()
        @option("text", default="hello")
        @length(min=5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: hello" in result.output

    def test_min_length_exact(self, cli_runner: CliRunner) -> None:
        """Test that string at exact minimum length passes."""

        @command()
        @option("text", default="test")
        @length(min=4)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "test"])
        assert result.exit_code == 0

    def test_min_length_too_short(self, cli_runner: CliRunner) -> None:
        """Test that string below minimum length fails."""

        @command()
        @option("text", default="hi")
        @length(min=5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hi"])
        assert result.exit_code != 0
        assert (
            "Value is too short, must be at least 5 characters" in result.output
        )

    def test_min_length_empty_string(self, cli_runner: CliRunner) -> None:
        """Test that empty string fails minimum length check."""

        @command()
        @option("text", default="")
        @length(min=1)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code != 0
        assert (
            "Value is too short, must be at least 1 character" in result.output
        )


class TestLengthMaxOnly:
    """Test length decorator with maximum length only."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_max_length_valid(self, cli_runner: CliRunner) -> None:
        """Test that string within maximum length passes."""

        @command()
        @option("text", default="hello")
        @length(max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: hello" in result.output

    def test_max_length_exact(self, cli_runner: CliRunner) -> None:
        """Test that string at exact maximum length passes."""

        @command()
        @option("text", default="12345678")
        @length(max=8)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "12345678"])
        assert result.exit_code == 0

    def test_max_length_too_long(self, cli_runner: CliRunner) -> None:
        """Test that string exceeding maximum length fails."""

        @command()
        @option("text", default="verylongstring")
        @length(max=5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "verylongstring"])
        assert result.exit_code != 0
        assert (
            "Value is too long, must be at most 5 characters" in result.output
        )

    def test_max_length_empty_string(self, cli_runner: CliRunner) -> None:
        """Test that empty string passes maximum length check."""

        @command()
        @option("text", default="")
        @length(max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0


class TestLengthBothBounds:
    """Test length decorator with both minimum and maximum length."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_both_bounds_valid(self, cli_runner: CliRunner) -> None:
        """Test that string within both bounds passes."""

        @command()
        @option("password", default="secret123")
        @length(min=8, max=20)
        def cmd(password: str) -> None:
            click.echo(f"Password: {password}")

        result = cli_runner.invoke(cmd, ["--password", "secret123"])
        assert result.exit_code == 0
        assert "Password: secret123" in result.output

    def test_both_bounds_at_min(self, cli_runner: CliRunner) -> None:
        """Test that string at minimum bound passes."""

        @command()
        @option("text", default="12345")
        @length(min=5, max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "12345"])
        assert result.exit_code == 0

    def test_both_bounds_at_max(self, cli_runner: CliRunner) -> None:
        """Test that string at maximum bound passes."""

        @command()
        @option("text", default="1234567890")
        @length(min=5, max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "1234567890"])
        assert result.exit_code == 0

    def test_both_bounds_below_min(self, cli_runner: CliRunner) -> None:
        """Test that string below minimum fails."""

        @command()
        @option("text", default="hi")
        @length(min=5, max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hi"])
        assert result.exit_code != 0
        assert (
            "Value is too short, must be at least 5 characters" in result.output
        )

    def test_both_bounds_above_max(self, cli_runner: CliRunner) -> None:
        """Test that string above maximum fails."""

        @command()
        @option("text", default="verylongstring")
        @length(min=5, max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "verylongstring"])
        assert result.exit_code != 0
        assert (
            "Value is too long, must be at most 10 characters" in result.output
        )


class TestLengthErrorCases:
    """Test length decorator error handling."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_neither_min_nor_max_raises_error(self) -> None:
        """Test that specifying neither min nor max raises ValueError."""
        try:
            length()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "At least one of 'min' or 'max' must be specified" in str(e)

    def test_min_zero(self, cli_runner: CliRunner) -> None:
        """Test that min=0 works correctly."""

        @command()
        @option("text", default="")
        @length(min=0, max=5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0

    def test_max_zero(self, cli_runner: CliRunner) -> None:
        """Test that max=0 only allows empty strings."""

        @command()
        @option("text", default="a")
        @length(max=0)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "a"])
        assert result.exit_code != 0
        assert (
            "Value is too long, must be at most 0 characters" in result.output
        )


class TestLengthEdgeCases:
    """Test length decorator edge cases."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_unicode_characters(self, cli_runner: CliRunner) -> None:
        """Test length with unicode characters."""

        @command()
        @option("text", default="你好世界")
        @length(min=2, max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "你好世界"])
        assert result.exit_code == 0

    def test_special_characters(self, cli_runner: CliRunner) -> None:
        """Test length with special characters."""

        @command()
        @option("text", default="!@#$%^&*()")
        @length(min=5, max=15)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "!@#$%^&*()"])
        assert result.exit_code == 0

    def test_whitespace_counts(self, cli_runner: CliRunner) -> None:
        """Test that whitespace is counted in length."""

        @command()
        @option("text", default="hello world")
        @length(min=11, max=11)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

    def test_newlines_count(self, cli_runner: CliRunner) -> None:
        """Test that newlines are counted in length."""

        @command()
        @option("text", default="hello\nworld")
        @length(min=11, max=11)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello\nworld"])
        assert result.exit_code == 0


class TestLengthChaining:
    """Test length decorator chaining with other decorators."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_with_multiple_length(self, cli_runner: CliRunner) -> None:
        """Test chaining multiple length decorators."""

        @command()
        @option("text", default="hello")
        @length(min=3)
        @length(max=10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0

    def test_chain_with_starts_with(self, cli_runner: CliRunner) -> None:
        """Test chaining length with starts_with."""

        @command()
        @option("url", default="https://example.com")
        @starts_with("https://")
        @length(min=10, max=100)
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_chain_with_add_prefix(self, cli_runner: CliRunner) -> None:
        """Test chaining length with add_prefix."""

        @command()
        @option("name", default="Alice")
        @add_prefix("user_")
        @length(min=5, max=20)
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "Alice"])
        assert result.exit_code == 0
        assert "Name: user_Alice" in result.output


class TestLengthPractical:
    """Test practical use cases for length decorator."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_password_validation(self, cli_runner: CliRunner) -> None:
        """Test length for password validation."""

        @command()
        @option("password", default="MyP@ssw0rd123")
        @length(min=8, max=128)
        def cmd(password: str) -> None:
            click.echo("Password accepted")

        result = cli_runner.invoke(cmd, ["--password", "MyP@ssw0rd123"])
        assert result.exit_code == 0
        assert "Password accepted" in result.output

    def test_username_validation(self, cli_runner: CliRunner) -> None:
        """Test length for username validation."""

        @command()
        @option("username", default="john_doe")
        @length(min=3, max=20)
        def cmd(username: str) -> None:
            click.echo(f"Username: {username}")

        result = cli_runner.invoke(cmd, ["--username", "john_doe"])
        assert result.exit_code == 0

    def test_tweet_length(self, cli_runner: CliRunner) -> None:
        """Test length for tweet-like character limits."""

        @command()
        @option("tweet", default="Hello Twitter!")
        @length(max=280)
        def cmd(tweet: str) -> None:
            click.echo(f"Tweet: {tweet}")

        result = cli_runner.invoke(cmd, ["--tweet", "Hello Twitter!"])
        assert result.exit_code == 0

    def test_filename_length(self, cli_runner: CliRunner) -> None:
        """Test length for filename validation."""

        @command()
        @option("filename", default="document.txt")
        @length(min=1, max=255)
        def cmd(filename: str) -> None:
            click.echo(f"Filename: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.txt"])
        assert result.exit_code == 0
