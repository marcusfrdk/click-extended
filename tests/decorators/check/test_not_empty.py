"""Comprehensive tests for not_empty decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.check.length import length
from click_extended.decorators.check.not_empty import NotEmpty, not_empty
from click_extended.decorators.check.starts_with import starts_with
from click_extended.decorators.transform.add_prefix import add_prefix


class TestNotEmptyInit:
    """Test NotEmpty class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_not_empty_is_child_node(self) -> None:
        """Test that NotEmpty extends ChildNode."""
        node = NotEmpty(name="test")
        assert isinstance(node, ChildNode)

    def test_not_empty_has_handle_str(self) -> None:
        """Test that NotEmpty implements handle_str method."""
        node = NotEmpty(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestNotEmptyValidation:
    """Test not_empty decorator validation."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_valid_string_passes(self, cli_runner: CliRunner) -> None:
        """Test that non-empty string passes validation."""

        @command()
        @option("name", default="Alice")
        @not_empty()
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "Alice"])
        assert result.exit_code == 0
        assert "Name: Alice" in result.output

    def test_empty_string_fails(self, cli_runner: CliRunner) -> None:
        """Test that empty string fails validation."""

        @command()
        @option("name", default="")
        @not_empty()
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", ""])
        assert result.exit_code != 0
        assert (
            "Value cannot be empty or contain only whitespace" in result.output
        )

    def test_whitespace_only_fails(self, cli_runner: CliRunner) -> None:
        """Test that whitespace-only string fails validation."""

        @command()
        @option("text", default="   ")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "   "])
        assert result.exit_code != 0
        assert (
            "Value cannot be empty or contain only whitespace" in result.output
        )

    def test_tab_only_fails(self, cli_runner: CliRunner) -> None:
        """Test that tab-only string fails validation."""

        @command()
        @option("text", default="\t\t")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "\t\t"])
        assert result.exit_code != 0
        assert (
            "Value cannot be empty or contain only whitespace" in result.output
        )

    def test_newline_only_fails(self, cli_runner: CliRunner) -> None:
        """Test that newline-only string fails validation."""

        @command()
        @option("text", default="\n\n")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "\n\n"])
        assert result.exit_code != 0
        assert (
            "Value cannot be empty or contain only whitespace" in result.output
        )

    def test_mixed_whitespace_fails(self, cli_runner: CliRunner) -> None:
        """Test that mixed whitespace fails validation."""

        @command()
        @option("text", default=" \t\n ")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", " \t\n "])
        assert result.exit_code != 0
        assert (
            "Value cannot be empty or contain only whitespace" in result.output
        )


class TestNotEmptyWithContent:
    """Test not_empty decorator with various content types."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_single_character_passes(self, cli_runner: CliRunner) -> None:
        """Test that single character passes."""

        @command()
        @option("char", default="a")
        @not_empty()
        def cmd(char: str) -> None:
            click.echo(f"Char: {char}")

        result = cli_runner.invoke(cmd, ["--char", "a"])
        assert result.exit_code == 0

    def test_text_with_leading_whitespace_passes(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that text with leading whitespace passes."""

        @command()
        @option("text", default="  hello")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "  hello"])
        assert result.exit_code == 0

    def test_text_with_trailing_whitespace_passes(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that text with trailing whitespace passes."""

        @command()
        @option("text", default="hello  ")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello  "])
        assert result.exit_code == 0

    def test_text_with_embedded_whitespace_passes(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that text with embedded whitespace passes."""

        @command()
        @option("text", default="hello world")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

    def test_unicode_text_passes(self, cli_runner: CliRunner) -> None:
        """Test that unicode text passes."""

        @command()
        @option("text", default="你好")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "你好"])
        assert result.exit_code == 0

    def test_special_characters_pass(self, cli_runner: CliRunner) -> None:
        """Test that special characters pass."""

        @command()
        @option("text", default="!@#$%")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "!@#$%"])
        assert result.exit_code == 0

    def test_numeric_string_passes(self, cli_runner: CliRunner) -> None:
        """Test that numeric string passes."""

        @command()
        @option("text", default="12345")
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "12345"])
        assert result.exit_code == 0


class TestNotEmptyChaining:
    """Test not_empty decorator chaining with other decorators."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_with_length(self, cli_runner: CliRunner) -> None:
        """Test chaining not_empty with length."""

        @command()
        @option("password", default="secret123")
        @not_empty()
        @length(min=8, max=128)
        def cmd(password: str) -> None:
            click.echo(f"Password: {password}")

        result = cli_runner.invoke(cmd, ["--password", "secret123"])
        assert result.exit_code == 0

    def test_chain_with_starts_with(self, cli_runner: CliRunner) -> None:
        """Test chaining not_empty with starts_with."""

        @command()
        @option("url", default="https://example.com")
        @not_empty()
        @starts_with("https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_chain_with_add_prefix(self, cli_runner: CliRunner) -> None:
        """Test chaining not_empty with add_prefix."""

        @command()
        @option("name", default="Alice")
        @not_empty()
        @add_prefix("user_")
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "Alice"])
        assert result.exit_code == 0
        assert "Name: user_Alice" in result.output

    def test_empty_string_fails_before_length_check(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that empty string fails at not_empty before reaching length."""

        @command()
        @option("text", default="")
        @not_empty()
        @length(min=5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code != 0
        assert (
            "Value cannot be empty or contain only whitespace" in result.output
        )


class TestNotEmptyPractical:
    """Test practical use cases for not_empty decorator."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_username_validation(self, cli_runner: CliRunner) -> None:
        """Test not_empty for username validation."""

        @command()
        @option("username", default="john_doe")
        @not_empty()
        @length(min=3, max=20)
        def cmd(username: str) -> None:
            click.echo(f"Username: {username}")

        result = cli_runner.invoke(cmd, ["--username", "john_doe"])
        assert result.exit_code == 0

    def test_email_validation(self, cli_runner: CliRunner) -> None:
        """Test not_empty as part of email validation."""

        @command()
        @option("email", default="user@example.com")
        @not_empty()
        def cmd(email: str) -> None:
            click.echo(f"Email: {email}")

        result = cli_runner.invoke(cmd, ["--email", "user@example.com"])
        assert result.exit_code == 0

    def test_comment_validation(self, cli_runner: CliRunner) -> None:
        """Test not_empty for comment validation."""

        @command()
        @option("comment", default="Great work!")
        @not_empty()
        @length(max=500)
        def cmd(comment: str) -> None:
            click.echo(f"Comment: {comment}")

        result = cli_runner.invoke(cmd, ["--comment", "Great work!"])
        assert result.exit_code == 0

    def test_api_key_validation(self, cli_runner: CliRunner) -> None:
        """Test not_empty for API key validation."""

        @command()
        @option("api_key", default="sk_test_1234567890")
        @not_empty()
        @length(min=10)
        def cmd(api_key: str) -> None:
            click.echo("API key accepted")

        result = cli_runner.invoke(cmd, ["--api-key", "sk_test_1234567890"])
        assert result.exit_code == 0
        assert "API key accepted" in result.output
