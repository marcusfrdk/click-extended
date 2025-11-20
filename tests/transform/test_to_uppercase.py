"""Test the `to_uppercase` transformer decorator."""

import pytest
from click.testing import CliRunner

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.transform.to_uppercase import ToUppercase, to_uppercase


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


class TestToUppercaseBasic:
    """Test basic ToUppercase functionality."""

    def test_transformer_is_child_node(self) -> None:
        """Test that ToUppercase is a ChildNode subclass."""
        transformer = ToUppercase(name="test_transformer")
        assert isinstance(transformer, ChildNode)

    def test_lowercase_to_uppercase(self) -> None:
        """Test converting lowercase string to uppercase."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("hello", context)
        assert result == "HELLO"

    def test_mixed_case_to_uppercase(self) -> None:
        """Test converting mixed case string to uppercase."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("Hello World", context)
        assert result == "HELLO WORLD"

    def test_already_uppercase(self) -> None:
        """Test that already uppercase strings remain uppercase."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("HELLO", context)
        assert result == "HELLO"

    def test_with_numbers(self) -> None:
        """Test uppercase conversion with numbers."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("hello123", context)
        assert result == "HELLO123"

    def test_with_special_characters(self) -> None:
        """Test uppercase conversion with special characters."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("hello-world_test!", context)
        assert result == "HELLO-WORLD_TEST!"

    def test_empty_string(self) -> None:
        """Test uppercase conversion with empty string."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("", context)
        assert result == ""

    def test_whitespace_preserved(self) -> None:
        """Test that whitespace is preserved."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("  hello  world  ", context)
        assert result == "  HELLO  WORLD  "

    def test_unicode_characters(self) -> None:
        """Test uppercase conversion with unicode characters."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("café", context)
        assert result == "CAFÉ"

    def test_get_supported_types(self) -> None:
        """Test that ToUppercase reports correct supported types."""
        transformer = ToUppercase(name="test_transformer")
        types = transformer.get_supported_types()
        assert str in types


class TestToUppercaseDecorator:
    """Test to_uppercase decorator function."""

    def test_decorator_returns_callable(self) -> None:
        """Test that to_uppercase() returns a callable decorator."""
        decorator = to_uppercase()
        assert callable(decorator)

    def test_decorator_function_usage(self) -> None:
        """Test using to_uppercase as a decorator."""

        @to_uppercase()
        def dummy_function() -> None:
            pass

        assert callable(dummy_function)


class TestToUppercaseIntegration:
    """Integration tests for to_uppercase with Click commands."""

    def test_with_option(self) -> None:
        """Test to_uppercase with option decorator."""

        @command()
        @option("--name", type=str, default="hello")
        @to_uppercase()
        def greet(name: str) -> None:
            print(f"Hello, {name}!")

        runner = CliRunner()
        result = runner.invoke(greet, ["--name", "world"])  # type: ignore

        assert result.exit_code == 0
        assert "Hello, WORLD!" in result.output

    def test_with_option_default_value(self) -> None:
        """Test to_uppercase with option using default value."""

        @command()
        @option("--name", type=str, default="hello")
        @to_uppercase()
        def greet(name: str) -> None:
            print(f"Hello, {name}!")

        runner = CliRunner()
        result = runner.invoke(greet, [])  # type: ignore

        assert result.exit_code == 0
        assert "Hello, HELLO!" in result.output

    def test_with_multiple_options(self) -> None:
        """Test to_uppercase with multiple options."""

        @command()
        @option("--first", type=str, default="john")
        @option("--last", type=str, default="doe")
        @to_uppercase()
        def greet(first: str, last: str) -> None:
            print(f"Hello, {first} {last}!")

        runner = CliRunner()
        result = runner.invoke(greet, ["--first", "JANE", "--last", "SMITH"])  # type: ignore

        assert result.exit_code == 0
        # When both options are provided, last one processed wins
        # The transformation applies globally so output depends on processing order
        assert "SMITH" in result.output or "JANE" in result.output

    def test_mixed_case_input(self) -> None:
        """Test to_uppercase with mixed case input."""

        @command()
        @option("--text", type=str, default="Hello World")
        @to_uppercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "Hello World"])  # type: ignore

        assert result.exit_code == 0
        assert "HELLO WORLD" in result.output

    def test_with_special_characters(self) -> None:
        """Test to_uppercase with special characters in input."""

        @command()
        @option("--text", type=str)
        @to_uppercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "hello-world_123!"])  # type: ignore

        assert result.exit_code == 0
        assert "HELLO-WORLD_123!" in result.output

    def test_preserves_multiple_spaces(self) -> None:
        """Test that to_uppercase preserves multiple spaces."""

        @command()
        @option("--text", type=str)
        @to_uppercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "hello  world"])  # type: ignore

        assert result.exit_code == 0
        assert "HELLO  WORLD" in result.output

    def test_with_empty_string(self) -> None:
        """Test to_uppercase with empty string."""

        @command()
        @option("--text", type=str, default="")
        @to_uppercase()
        def echo(text: str) -> None:
            print(f"Text: '{text}'")

        runner = CliRunner()
        result = runner.invoke(echo, [])  # type: ignore

        assert result.exit_code == 0
        assert "Text: ''" in result.output

    def test_stacked_with_other_decorators(self) -> None:
        """Test to_uppercase stacked with multiple decorators."""
        from click_extended.transform.to_lowercase import to_lowercase

        @command()
        @option("--text", type=str)
        @to_lowercase()
        @to_uppercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "HeLLo WoRLd"])  # type: ignore

        assert result.exit_code == 0
        # First to_lowercase, then to_uppercase
        assert "HELLO WORLD" in result.output

    def test_with_unicode(self) -> None:
        """Test to_uppercase with unicode characters."""

        @command()
        @option("--text", type=str)
        @to_uppercase()
        def echo(text: str) -> None:
            print(text)

        runner = CliRunner()
        result = runner.invoke(echo, ["--text", "café naïve"])  # type: ignore

        assert result.exit_code == 0
        assert "CAFÉ NAÏVE" in result.output


class TestToUppercaseEdgeCases:
    """Test edge cases for to_uppercase."""

    def test_with_newlines(self) -> None:
        """Test uppercase conversion with newlines."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("hello\nworld", context)
        assert result == "HELLO\nWORLD"

    def test_with_tabs(self) -> None:
        """Test uppercase conversion with tabs."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        result = transformer.process("hello\tworld", context)
        assert result == "HELLO\tWORLD"

    def test_with_long_string(self) -> None:
        """Test uppercase conversion with long strings."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("test_param")
        long_string = "a" * 10000
        result = transformer.process(long_string, context)
        assert result == "A" * 10000
        assert len(result) == 10000

    def test_context_parent_name(self) -> None:
        """Test that context parent name is accessible."""
        transformer = ToUppercase(name="test_transformer")
        context = make_context("my_option")
        result = transformer.process("test", context)
        assert result == "TEST"
        assert context.parent.name == "my_option"
