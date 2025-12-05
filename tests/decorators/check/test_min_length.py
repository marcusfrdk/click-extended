"""Comprehensive tests for min_length decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.check.min_length import MinLength, min_length


class TestMinLengthInit:
    """Test MinLength class initialization."""

    def test_min_length_is_child_node(self) -> None:
        """Test that MinLength extends ChildNode."""
        from click_extended.core.nodes.child_node import ChildNode

        node = MinLength(name="test")
        assert isinstance(node, ChildNode)

    def test_min_length_has_handle_str(self) -> None:
        """Test that MinLength implements handle_str method."""
        node = MinLength(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestMinLengthHandleStr:
    """Test MinLength.handle_str() validation logic."""

    def test_handle_str_allows_string_above_minimum(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str allows strings longer than minimum length."""

        @command()
        @option("text", default="hello")
        @min_length(3)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: hello" in result.output

    def test_handle_str_allows_string_at_exact_minimum(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str allows strings exactly at minimum length."""

        @command()
        @option("text", default="12345")
        @min_length(5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "12345"])
        assert result.exit_code == 0
        assert "Text: 12345" in result.output

    def test_handle_str_rejects_string_below_minimum(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str rejects strings shorter than minimum length."""

        @command()
        @option("text", default="hello")
        @min_length(10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code != 0
        assert "Value is too short" in result.output
        assert "at least '10' characters" in result.output

    def test_handle_str_allows_empty_string_with_zero_minimum(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str allows empty string when min length is 0."""

        @command()
        @option("text", default="")
        @min_length(0)
        def cmd(text: str) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0
        assert "Text: ''" in result.output

    def test_handle_str_rejects_empty_string_with_positive_minimum(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str rejects empty string when min length > 0."""

        @command()
        @option("text", default="")
        @min_length(1)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code != 0
        assert "Value is too short" in result.output

    def test_handle_str_with_unicode_characters(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str counts unicode characters correctly."""

        @command()
        @option("text", default="hello")
        @min_length(5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "héllo"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "🎉🎊🎈🎁🎀"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "🎉🎊"])
        assert result.exit_code != 0

    def test_handle_str_with_whitespace(self, cli_runner: CliRunner) -> None:
        """Test handle_str includes whitespace in length count."""

        @command()
        @option("text", default="hello")
        @min_length(11)
        def cmd(text: str) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code != 0

    def test_handle_str_returns_original_value(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str returns the original value unchanged."""

        @command()
        @option("text", default="hello")
        @min_length(3)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "WORLD"])
        assert result.exit_code == 0
        assert "Text: WORLD" in result.output


class TestMinLengthDecorator:
    """Test min_length() decorator function."""

    def test_min_length_returns_decorator(self) -> None:
        """Test min_length() returns a decorator function."""
        decorator = min_length(10)
        assert callable(decorator)

    def test_min_length_decorator_application(self) -> None:
        """Test min_length decorator can be applied to functions."""

        @min_length(5)
        def test_func() -> None:
            pass

        assert callable(test_func)

    def test_min_length_stores_length_parameter(
        self, cli_runner: CliRunner
    ) -> None:
        """Test min_length stores the length parameter correctly."""

        @command()
        @option("text", default="hello")
        @min_length(8)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "12345678"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "1234567"])
        assert result.exit_code != 0


class TestMinLengthWithOptions:
    """Test min_length with option decorators."""

    def test_min_length_with_required_option(
        self, cli_runner: CliRunner
    ) -> None:
        """Test min_length works with required options."""

        @command()
        @option("name", required=True)
        @min_length(3)
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "Alice"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--name", "Al"])
        assert result.exit_code != 0

    def test_min_length_with_default_option(
        self, cli_runner: CliRunner
    ) -> None:
        """Test min_length validates default option values."""

        @command()
        @option("text", default="hello")
        @min_length(3)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Text: hello" in result.output

    def test_min_length_with_multiple_options(
        self, cli_runner: CliRunner
    ) -> None:
        """Test min_length can be applied to multiple options."""

        @command()
        @option("first", default="")
        @min_length(2)
        @option("second", default="")
        @min_length(5)
        def cmd(first: str, second: str) -> None:
            click.echo(f"First: {first}, Second: {second}")

        result = cli_runner.invoke(cmd, ["--first", "hi", "--second", "hello"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--first", "h", "--second", "hello"])
        assert result.exit_code != 0


class TestMinLengthWithArguments:
    """Test min_length with argument decorators."""

    def test_min_length_with_argument(self, cli_runner: CliRunner) -> None:
        """Test min_length works with arguments."""
        from click_extended.core.decorators.argument import argument

        @command()
        @argument("name")
        @min_length(3)
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["Alice"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["Al"])
        assert result.exit_code != 0


class TestMinLengthChaining:
    """Test min_length with other decorators."""

    def test_min_length_with_other_validators(
        self, cli_runner: CliRunner
    ) -> None:
        """Test min_length chains with other validation decorators."""
        from click_extended.decorators.check.max_length import max_length

        @command()
        @option("password", default="")
        @min_length(8)
        @max_length(20)
        def cmd(password: str) -> None:
            click.echo(f"Password length: {len(password)}")

        result = cli_runner.invoke(cmd, ["--password", "short"])
        assert result.exit_code != 0

        result = cli_runner.invoke(cmd, ["--password", "valid_password"])
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cmd, ["--password", "this_is_way_too_long_password"]
        )
        assert result.exit_code != 0

    def test_min_length_with_transformers(self, cli_runner: CliRunner) -> None:
        """Test min_length works before transformers."""
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Uppercase(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("text", default="")
        @min_length(5)
        @Uppercase.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: HELLO" in result.output


class TestMinLengthErrorMessages:
    """Test min_length error message formatting."""

    def test_error_message_includes_minimum(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message shows the minimum length."""

        @command()
        @option("text", default="")
        @min_length(10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "short"])
        assert result.exit_code != 0
        assert "at least '10' characters" in result.output

    def test_error_message_clear_and_helpful(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message is clear about the issue."""

        @command()
        @option("username", default="")
        @min_length(5)
        def cmd(username: str) -> None:
            click.echo(f"Username: {username}")

        result = cli_runner.invoke(cmd, ["--username", "abc"])
        assert result.exit_code != 0
        assert "Value is too short" in result.output


class TestMinLengthEdgeCases:
    """Test min_length edge cases and boundary conditions."""

    def test_min_length_with_large_minimum(self, cli_runner: CliRunner) -> None:
        """Test min_length with very large minimum."""

        @command()
        @option("text", default="")
        @min_length(10000)
        def cmd(text: str) -> None:
            click.echo("OK")

        long_text = "a" * 10001
        result = cli_runner.invoke(cmd, ["--text", long_text])
        assert result.exit_code == 0

        short_text = "a" * 9999
        result = cli_runner.invoke(cmd, ["--text", short_text])
        assert result.exit_code != 0

    def test_min_length_with_newlines(self, cli_runner: CliRunner) -> None:
        """Test min_length counts newlines as characters."""

        @command()
        @option("text", default="")
        @min_length(11)
        def cmd(text: str) -> None:
            click.echo("OK")

        result = cli_runner.invoke(cmd, ["--text", "hello\nworld"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "hello\nworl"])
        assert result.exit_code != 0

    def test_min_length_with_tabs(self, cli_runner: CliRunner) -> None:
        """Test min_length counts tabs as single characters."""

        @command()
        @option("text", default="")
        @min_length(11)
        def cmd(text: str) -> None:
            click.echo("OK")

        result = cli_runner.invoke(cmd, ["--text", "hello\tworld"])
        assert result.exit_code == 0


class TestMinLengthPasswordValidation:
    """Test min_length for real-world password validation scenario."""

    def test_password_minimum_length_enforcement(
        self, cli_runner: CliRunner
    ) -> None:
        """Test min_length enforces password policies."""

        @command()
        @option("password", required=True)
        @min_length(8)
        def register(password: str) -> None:
            click.echo("Registration successful!")

        result = cli_runner.invoke(register, ["--password", "pass"])
        assert result.exit_code != 0
        assert "too short" in result.output

        result = cli_runner.invoke(register, ["--password", "password123"])
        assert result.exit_code == 0
        assert "Registration successful!" in result.output
