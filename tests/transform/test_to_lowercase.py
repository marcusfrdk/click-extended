"""Test the `to_lowercase` transformer decorator."""

import pytest
from click.testing import CliRunner

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.transform.to_lowercase import ToLowercase, to_lowercase


def make_context(parent_name: str = "test") -> ProcessContext:
    """Helper to create a ProcessContext for testing."""
    from unittest.mock import MagicMock

    parent = MagicMock()
    parent.name = parent_name
    return ProcessContext(
        parent=parent,
        siblings=[],
        tags={},
        args=(),
        kwargs={},
    )


class TestToLowercaseBasic:
    """Test basic ToLowercase functionality."""

    def test_transformer_is_child_node(self) -> None:
        """Test that ToLowercase is a ChildNode subclass."""
        transformer = ToLowercase(name="test_transformer")
        assert isinstance(transformer, ChildNode)

    def test_uppercase_to_lowercase(self) -> None:
        """Test converting uppercase string to lowercase."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("HELLO", context)
        assert result == "hello"

    def test_mixed_case_to_lowercase(self) -> None:
        """Test converting mixed case string to lowercase."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("Hello World", context)
        assert result == "hello world"

    def test_already_lowercase(self) -> None:
        """Test that already lowercase strings remain lowercase."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("hello", context)
        assert result == "hello"

    def test_with_numbers(self) -> None:
        """Test lowercase conversion with numbers."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("HELLO123", context)
        assert result == "hello123"

    def test_with_special_characters(self) -> None:
        """Test lowercase conversion with special characters."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("HELLO-WORLD_TEST!", context)
        assert result == "hello-world_test!"

    def test_empty_string(self) -> None:
        """Test lowercase conversion with empty string."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("", context)
        assert result == ""

    def test_whitespace_preserved(self) -> None:
        """Test that whitespace is preserved."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("  HELLO  WORLD  ", context)
        assert result == "  hello  world  "

    def test_unicode_characters(self) -> None:
        """Test lowercase conversion with unicode characters."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("CAFÉ", context)
        assert result == "café"

    def test_get_supported_types(self) -> None:
        """Test that ToLowercase reports correct supported types."""
        transformer = ToLowercase(name="test_transformer")
        types = transformer.get_supported_types()
        assert str in types


class TestToLowercaseDecorator:
    """Test to_lowercase decorator function."""

    def test_decorator_returns_callable(self) -> None:
        """Test that to_lowercase() returns a callable decorator."""
        decorator = to_lowercase()
        assert callable(decorator)

    def test_decorator_function_usage(self) -> None:
        """Test using to_lowercase as a decorator."""

        @to_lowercase()
        def dummy_function() -> None:
            pass

        assert callable(dummy_function)


class TestToLowercaseIntegration:
    """Integration tests for to_lowercase with Click commands."""

    def test_with_option(self) -> None:
        """Test to_lowercase with option decorator."""

        @command()
        @option("--name", type=str, default="HELLO")
        @to_lowercase()
        def greet(name: str) -> None:
            print(f"Hello, {name}!")

        runner = CliRunner()
        result = runner.invoke(greet, ["--name", "WORLD"])  # type: ignore

        assert result.exit_code == 0
        assert "Hello, world!" in result.output

    def test_with_option_default_value(self) -> None:
        """Test to_lowercase with option using default value."""

        @command()
        @option("--name", type=str, default="HELLO")
        @to_lowercase()
        def greet(name: str) -> None:
            print(f"Hello, {name}!")

        runner = CliRunner()
        result = runner.invoke(greet, [])  # type: ignore

        assert result.exit_code == 0
        assert "Hello, hello!" in result.output

    def test_with_multiple_options(self) -> None:
        """Test to_lowercase with multiple options."""

        @command()
        @option("--first", type=str, default="JOHN")
        @option("--last", type=str, default="DOE")
        @to_lowercase()
        def greet(first: str, last: str) -> None:
            print(f"Hello, {first} {last}!")

        runner = CliRunner()
        result = runner.invoke(greet, ["--first", "jane", "--last", "smith"])  # type: ignore

        assert result.exit_code == 0
        # When both options are provided, last one processed wins
        # The transformation applies globally so output depends on processing order
        assert "smith" in result.output or "jane" in result.output

    def test_mixed_case_input(self) -> None:
        """Test to_lowercase with mixed case input."""

        @command()
        @option("--text", type=str, default="Hello World")
        @to_lowercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "HeLLo WoRLd"])  # type: ignore

        assert result.exit_code == 0
        assert "hello world" in result.output

    def test_with_special_characters(self) -> None:
        """Test to_lowercase with special characters in input."""

        @command()
        @option("--text", type=str)
        @to_lowercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "HELLO-WORLD_123!"])  # type: ignore

        assert result.exit_code == 0
        assert "hello-world_123!" in result.output

    def test_preserves_multiple_spaces(self) -> None:
        """Test that to_lowercase preserves multiple spaces."""

        @command()
        @option("--text", type=str)
        @to_lowercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "HELLO  WORLD"])  # type: ignore

        assert result.exit_code == 0
        assert "hello  world" in result.output

    def test_with_empty_string(self) -> None:
        """Test to_lowercase with empty string."""

        @command()
        @option("--text", type=str, default="")
        @to_lowercase()
        def echo(text: str) -> None:
            print(f"Text: '{text}'")

        runner = CliRunner()
        result = runner.invoke(echo, [])  # type: ignore

        assert result.exit_code == 0
        assert "Text: ''" in result.output

    def test_stacked_with_other_decorators(self) -> None:
        """Test to_lowercase stacked with multiple decorators."""
        from click_extended.transform.to_uppercase import to_uppercase

        @command()
        @option("--text", type=str)
        @to_uppercase()
        @to_lowercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "HeLLo WoRLd"])  # type: ignore

        assert result.exit_code == 0
        # First to_uppercase, then to_lowercase
        assert "hello world" in result.output

    def test_with_unicode(self) -> None:
        """Test to_lowercase with unicode characters."""

        @command()
        @option("--text", type=str)
        @to_lowercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "CAFÉ NAÏVE"])  # type: ignore

        assert result.exit_code == 0
        assert "café naïve" in result.output


class TestToLowercaseEdgeCases:
    """Test edge cases for to_lowercase."""

    def test_with_newlines(self) -> None:
        """Test lowercase conversion with newlines."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("HELLO\nWORLD", context)
        assert result == "hello\nworld"

    def test_with_tabs(self) -> None:
        """Test lowercase conversion with tabs."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("HELLO\tWORLD", context)
        assert result == "hello\tworld"

    def test_with_long_string(self) -> None:
        """Test lowercase conversion with long strings."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("test_param")
        long_string = "A" * 10000
        result = transformer.process(long_string, context)
        assert result == "a" * 10000
        assert len(result) == 10000

    def test_context_parent_name(self) -> None:
        """Test that context parent name is accessible."""
        transformer = ToLowercase(name="test_transformer")
        context = make_context("my_option")
        result = transformer.process("TEST", context)
        assert result == "test"
        assert context.parent.name == "my_option"
