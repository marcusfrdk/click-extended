"""Comprehensive tests for strip, lstrip, and rstrip decorators."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.transform.strip import (
    LStrip,
    RStrip,
    Strip,
    lstrip,
    rstrip,
    strip,
)


class TestStripInit:
    """Test Strip class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_strip_is_child_node(self) -> None:
        """Test that Strip extends ChildNode."""
        node = Strip(name="test")
        assert isinstance(node, ChildNode)

    def test_strip_has_handle_str(self) -> None:
        """Test that Strip implements handle_str method."""
        node = Strip(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestStripWhitespace:
    """Test strip decorator with whitespace."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_strip_leading_whitespace(self, cli_runner: CliRunner) -> None:
        """Test stripping leading whitespace."""

        @command()
        @option("text", default="  hello")
        @strip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  hello"])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_strip_trailing_whitespace(self, cli_runner: CliRunner) -> None:
        """Test stripping trailing whitespace."""

        @command()
        @option("text", default="hello  ")
        @strip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "hello  "])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_strip_both_ends_whitespace(self, cli_runner: CliRunner) -> None:
        """Test stripping whitespace from both ends."""

        @command()
        @option("text", default="  hello  ")
        @strip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  hello  "])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_strip_tabs_and_newlines(self, cli_runner: CliRunner) -> None:
        """Test stripping tabs and newlines."""

        @command()
        @option("text", default="\t\nhello\n\t")
        @strip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "\t\nhello\n\t"])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_strip_no_whitespace(self, cli_runner: CliRunner) -> None:
        """Test strip with no whitespace to remove."""

        @command()
        @option("text", default="hello")
        @strip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "'hello'" in result.output


class TestStripCustomChars:
    """Test strip decorator with custom characters."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_strip_slashes(self, cli_runner: CliRunner) -> None:
        """Test stripping slashes."""

        @command()
        @option("path", default="///path///")
        @strip("/")
        def cmd(path: str) -> None:
            click.echo(f"'{path}'")

        result = cli_runner.invoke(cmd, ["--path", "///path///"])
        assert result.exit_code == 0
        assert "'path'" in result.output

    def test_strip_dots(self, cli_runner: CliRunner) -> None:
        """Test stripping dots."""

        @command()
        @option("text", default="...hello...")
        @strip(".")
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "...hello..."])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_strip_multiple_chars(self, cli_runner: CliRunner) -> None:
        """Test stripping multiple character types."""

        @command()
        @option("text", default="***###hello###***")
        @strip("*#")
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "***###hello###***"])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_strip_preserves_internal_chars(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that strip only removes from ends, not internal."""

        @command()
        @option("text", default="xxx/hello/world/xxx")
        @strip("x")
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "xxx/hello/world/xxx"])
        assert result.exit_code == 0
        assert "'/hello/world/'" in result.output


class TestLStripInit:
    """Test LStrip class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_lstrip_is_child_node(self) -> None:
        """Test that LStrip extends ChildNode."""
        node = LStrip(name="test")
        assert isinstance(node, ChildNode)

    def test_lstrip_has_handle_str(self) -> None:
        """Test that LStrip implements handle_str method."""
        node = LStrip(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestLStripWhitespace:
    """Test lstrip decorator with whitespace."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_lstrip_leading_whitespace(self, cli_runner: CliRunner) -> None:
        """Test stripping only leading whitespace."""

        @command()
        @option("text", default="  hello  ")
        @lstrip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  hello  "])
        assert result.exit_code == 0
        assert "'hello  '" in result.output

    def test_lstrip_no_trailing_effect(self, cli_runner: CliRunner) -> None:
        """Test that lstrip doesn't affect trailing whitespace."""

        @command()
        @option("text", default="hello  ")
        @lstrip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "hello  "])
        assert result.exit_code == 0
        assert "'hello  '" in result.output


class TestLStripCustomChars:
    """Test lstrip decorator with custom characters."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_lstrip_slashes(self, cli_runner: CliRunner) -> None:
        """Test stripping leading slashes only."""

        @command()
        @option("path", default="///path///")
        @lstrip("/")
        def cmd(path: str) -> None:
            click.echo(f"'{path}'")

        result = cli_runner.invoke(cmd, ["--path", "///path///"])
        assert result.exit_code == 0
        assert "'path///'" in result.output

    def test_lstrip_preserves_trailing(self, cli_runner: CliRunner) -> None:
        """Test that lstrip preserves trailing characters."""

        @command()
        @option("text", default="xxxhelloxxx")
        @lstrip("x")
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "xxxhelloxxx"])
        assert result.exit_code == 0
        assert "'helloxxx'" in result.output


class TestRStripInit:
    """Test RStrip class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_rstrip_is_child_node(self) -> None:
        """Test that RStrip extends ChildNode."""
        node = RStrip(name="test")
        assert isinstance(node, ChildNode)

    def test_rstrip_has_handle_str(self) -> None:
        """Test that RStrip implements handle_str method."""
        node = RStrip(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestRStripWhitespace:
    """Test rstrip decorator with whitespace."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_rstrip_trailing_whitespace(self, cli_runner: CliRunner) -> None:
        """Test stripping only trailing whitespace."""

        @command()
        @option("text", default="  hello  ")
        @rstrip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  hello  "])
        assert result.exit_code == 0
        assert "'  hello'" in result.output

    def test_rstrip_no_leading_effect(self, cli_runner: CliRunner) -> None:
        """Test that rstrip doesn't affect leading whitespace."""

        @command()
        @option("text", default="  hello")
        @rstrip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  hello"])
        assert result.exit_code == 0
        assert "'  hello'" in result.output


class TestRStripCustomChars:
    """Test rstrip decorator with custom characters."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_rstrip_slashes(self, cli_runner: CliRunner) -> None:
        """Test stripping trailing slashes only."""

        @command()
        @option("path", default="///path///")
        @rstrip("/")
        def cmd(path: str) -> None:
            click.echo(f"'{path}'")

        result = cli_runner.invoke(cmd, ["--path", "///path///"])
        assert result.exit_code == 0
        assert "'///path'" in result.output

    def test_rstrip_preserves_leading(self, cli_runner: CliRunner) -> None:
        """Test that rstrip preserves leading characters."""

        @command()
        @option("text", default="xxxhelloxxx")
        @rstrip("x")
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "xxxhelloxxx"])
        assert result.exit_code == 0
        assert "'xxxhello'" in result.output


class TestStripChaining:
    """Test chaining strip decorators."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_lstrip_rstrip(self, cli_runner: CliRunner) -> None:
        """Test chaining lstrip and rstrip."""

        @command()
        @option("text", default="  hello  ")
        @lstrip()
        @rstrip()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  hello  "])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_chain_with_not_empty(self, cli_runner: CliRunner) -> None:
        """Test chaining strip with not_empty."""
        from click_extended.decorators.check.not_empty import not_empty

        @command()
        @option("text", default="  hello  ")
        @strip()
        @not_empty()
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  hello  "])
        assert result.exit_code == 0
        assert "'hello'" in result.output

    def test_strip_different_chars_each_side(
        self, cli_runner: CliRunner
    ) -> None:
        """Test stripping different characters from each side."""

        @command()
        @option("text", default="***hello###")
        @lstrip("*")
        @rstrip("#")
        def cmd(text: str) -> None:
            click.echo(f"'{text}'")

        result = cli_runner.invoke(cmd, ["--text", "***hello###"])
        assert result.exit_code == 0
        assert "'hello'" in result.output


class TestStripPractical:
    """Test practical use cases for strip decorators."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_clean_user_input(self, cli_runner: CliRunner) -> None:
        """Test cleaning user input with strip."""

        @command()
        @option("name", default="  John Doe  ")
        @strip()
        def cmd(name: str) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(cmd, ["--name", "  John Doe  "])
        assert result.exit_code == 0
        assert "Hello, John Doe!" in result.output

    def test_normalize_path(self, cli_runner: CliRunner) -> None:
        """Test normalizing paths by stripping slashes."""

        @command()
        @option("path", default="/path/to/file/")
        @strip("/")
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "/path/to/file/"])
        assert result.exit_code == 0
        assert "Path: path/to/file" in result.output

    def test_remove_file_extension_markers(self, cli_runner: CliRunner) -> None:
        """Test removing file extension markers."""

        @command()
        @option("filename", default="...filename...")
        @strip(".")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "...filename..."])
        assert result.exit_code == 0
        assert "File: filename" in result.output

    def test_clean_csv_data(self, cli_runner: CliRunner) -> None:
        """Test cleaning CSV-like data."""

        @command()
        @option("value", default='  "data"  ')
        @strip()
        @strip('"')
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", '  "data"  '])
        assert result.exit_code == 0
        assert "Value: data" in result.output
