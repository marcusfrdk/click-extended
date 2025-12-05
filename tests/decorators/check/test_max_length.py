"""Comprehensive tests for max_length decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.check.max_length import MaxLength, max_length


class TestMaxLengthInit:
    """Test MaxLength class initialization."""

    def test_max_length_is_child_node(self) -> None:
        """Test that MaxLength extends ChildNode."""
        from click_extended.core.nodes.child_node import ChildNode

        node = MaxLength(name="test")
        assert isinstance(node, ChildNode)

    def test_max_length_has_handle_str(self) -> None:
        """Test that MaxLength implements handle_str method."""
        node = MaxLength(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestMaxLengthHandleStr:
    """Test MaxLength.handle_str() validation logic."""

    def test_handle_str_allows_string_within_limit(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str allows strings shorter than max length."""

        @command()
        @option("text", default="hello")
        @max_length(10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: hello" in result.output

    def test_handle_str_allows_string_at_exact_limit(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str allows strings exactly at max length."""

        @command()
        @option("text", default="12345")
        @max_length(5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "12345"])
        assert result.exit_code == 0
        assert "Text: 12345" in result.output

    def test_handle_str_rejects_string_exceeding_limit(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str rejects strings longer than max length."""

        @command()
        @option("text", default="hello")
        @max_length(3)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code != 0
        assert "Value is too long" in result.output
        assert "at most '3' characters" in result.output

    def test_handle_str_allows_empty_string_with_zero_limit(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str allows empty string when max length is 0."""

        @command()
        @option("text", default="")
        @max_length(0)
        def cmd(text: str) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0
        assert "Text: ''" in result.output

    def test_handle_str_rejects_any_string_with_zero_limit(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str rejects any non-empty string when max length is 0."""

        @command()
        @option("text", default="")
        @max_length(0)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "a"])
        assert result.exit_code != 0
        assert "Value is too long" in result.output

    def test_handle_str_with_unicode_characters(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str counts unicode characters correctly."""

        @command()
        @option("text", default="hello")
        @max_length(5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "héllo"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "🎉🎊🎈🎁🎀"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "🎉🎊🎈🎁🎀🎂"])
        assert result.exit_code != 0

    def test_handle_str_with_whitespace(self, cli_runner: CliRunner) -> None:
        """Test handle_str includes whitespace in length count."""

        @command()
        @option("text", default="hello")
        @max_length(11)
        def cmd(text: str) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "hello  world"])
        assert result.exit_code != 0

    def test_handle_str_returns_original_value(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str returns the original value unchanged."""

        @command()
        @option("text", default="hello")
        @max_length(10)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "WORLD"])
        assert result.exit_code == 0
        assert "Text: WORLD" in result.output


class TestMaxLengthDecorator:
    """Test max_length() decorator function."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_max_length_returns_decorator(self) -> None:
        """Test max_length() returns a decorator function."""
        decorator = max_length(10)
        assert callable(decorator)

    def test_max_length_decorator_application(self) -> None:
        """Test max_length decorator can be applied to functions."""

        @max_length(5)
        def test_func() -> None:
            pass

        assert callable(test_func)

    def test_max_length_stores_length_parameter(
        self, cli_runner: CliRunner
    ) -> None:
        """Test max_length stores the length parameter correctly."""

        @command()
        @option("text", default="hello")
        @max_length(8)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "12345678"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "123456789"])
        assert result.exit_code != 0


class TestMaxLengthWithOptions:
    """Test max_length with option decorators."""

    def test_max_length_with_required_option(
        self, cli_runner: CliRunner
    ) -> None:
        """Test max_length works with required options."""

        @command()
        @option("name", required=True)
        @max_length(10)
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "Alice"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--name", "VeryLongName"])
        assert result.exit_code != 0

    def test_max_length_with_default_option(
        self, cli_runner: CliRunner
    ) -> None:
        """Test max_length validates default option values."""

        @command()
        @option("text", default="hi")
        @max_length(5)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Text: hi" in result.output

    def test_max_length_with_multiple_options(
        self, cli_runner: CliRunner
    ) -> None:
        """Test max_length can be applied to multiple options."""

        @command()
        @option("first", default="")
        @max_length(5)
        @option("second", default="")
        @max_length(10)
        def cmd(first: str, second: str) -> None:
            click.echo(f"First: {first}, Second: {second}")

        result = cli_runner.invoke(cmd, ["--first", "hi", "--second", "hello"])
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cmd, ["--first", "toolong", "--second", "hello"]
        )
        assert result.exit_code != 0


class TestMaxLengthWithArguments:
    """Test max_length with argument decorators."""

    def test_max_length_with_argument(self, cli_runner: CliRunner) -> None:
        """Test max_length works with arguments."""
        from click_extended.core.decorators.argument import argument

        @command()
        @argument("name")
        @max_length(8)
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["Alice"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["VeryLongName"])
        assert result.exit_code != 0


class TestMaxLengthChaining:
    """Test max_length with other decorators."""

    def test_max_length_with_other_validators(
        self, cli_runner: CliRunner
    ) -> None:
        """Test max_length chains with other validation decorators."""
        from click_extended.decorators.check.min_length import min_length

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

    def test_max_length_with_transformers(self, cli_runner: CliRunner) -> None:
        """Test max_length works before transformers."""
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Uppercase(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("text", default="")
        @max_length(5)
        @Uppercase.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: HELLO" in result.output


class TestMaxLengthErrorMessages:
    """Test max_length error message formatting."""

    def test_error_message_includes_limit(self, cli_runner: CliRunner) -> None:
        """Test error message shows the maximum length."""

        @command()
        @option("text", default="")
        @max_length(7)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "toolongtext"])
        assert result.exit_code != 0
        assert "at most '7' characters" in result.output

    def test_error_message_clear_and_helpful(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message is clear about the issue."""

        @command()
        @option("username", default="")
        @max_length(15)
        def cmd(username: str) -> None:
            click.echo(f"Username: {username}")

        result = cli_runner.invoke(
            cmd, ["--username", "verylongusernamethatexceedslimit"]
        )
        assert result.exit_code != 0
        assert "Value is too long" in result.output


class TestMaxLengthEdgeCases:
    """Test max_length edge cases and boundary conditions."""

    def test_max_length_with_large_limit(self, cli_runner: CliRunner) -> None:
        """Test max_length with very large limit."""

        @command()
        @option("text", default="")
        @max_length(10000)
        def cmd(text: str) -> None:
            click.echo("OK")

        long_text = "a" * 9999
        result = cli_runner.invoke(cmd, ["--text", long_text])
        assert result.exit_code == 0

        too_long_text = "a" * 10001
        result = cli_runner.invoke(cmd, ["--text", too_long_text])
        assert result.exit_code != 0

    def test_max_length_with_newlines(self, cli_runner: CliRunner) -> None:
        """Test max_length counts newlines as characters."""

        @command()
        @option("text", default="")
        @max_length(11)
        def cmd(text: str) -> None:
            click.echo("OK")

        result = cli_runner.invoke(cmd, ["--text", "hello\nworld"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--text", "hello\nworld\n"])
        assert result.exit_code != 0

    def test_max_length_with_tabs(self, cli_runner: CliRunner) -> None:
        """Test max_length counts tabs as single characters."""

        @command()
        @option("text", default="")
        @max_length(7)
        def cmd(text: str) -> None:
            click.echo("OK")

        result = cli_runner.invoke(cmd, ["--text", "hello\tworld"])
        assert result.exit_code != 0
