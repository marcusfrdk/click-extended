"""Comprehensive tests for remove_prefix decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.transform.remove_prefix import (
    RemovePrefix,
    remove_prefix,
)
from click_extended.decorators.transform.strip import strip


class TestRemovePrefixInit:
    """Test RemovePrefix class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_prefix_is_child_node(self) -> None:
        """Test that RemovePrefix extends ChildNode."""
        node = RemovePrefix(name="test")
        assert isinstance(node, ChildNode)

    def test_remove_prefix_has_handle_str(self) -> None:
        """Test that RemovePrefix implements handle_str method."""
        node = RemovePrefix(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestRemovePrefixBasic:
    """Test remove_prefix decorator basic functionality."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_simple_prefix(self, cli_runner: CliRunner) -> None:
        """Test removing a simple prefix."""

        @command()
        @option("text", default="Mr. John")
        @remove_prefix("Mr. ")
        def cmd(text: str) -> None:
            click.echo(f"Name: {text}")

        result = cli_runner.invoke(cmd, ["--text", "Mr. John"])
        assert result.exit_code == 0
        assert "Name: John" in result.output

    def test_remove_prefix_not_present(self, cli_runner: CliRunner) -> None:
        """Test behavior when prefix is not present."""

        @command()
        @option("text", default="John")
        @remove_prefix("Mr. ")
        def cmd(text: str) -> None:
            click.echo(f"Name: {text}")

        result = cli_runner.invoke(cmd, ["--text", "John"])
        assert result.exit_code == 0
        assert "Name: John" in result.output

    def test_remove_prefix_case_sensitive(self, cli_runner: CliRunner) -> None:
        """Test that removal is case-sensitive."""

        @command()
        @option("text", default="mr. John")
        @remove_prefix("Mr. ")
        def cmd(text: str) -> None:
            click.echo(f"Name: {text}")

        result = cli_runner.invoke(cmd, ["--text", "mr. John"])
        assert result.exit_code == 0
        assert "Name: mr. John" in result.output

    def test_remove_single_character_prefix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test removing a single character prefix."""

        @command()
        @option("text", default="/path")
        @remove_prefix("/")
        def cmd(text: str) -> None:
            click.echo(f"Path: {text}")

        result = cli_runner.invoke(cmd, ["--text", "/path"])
        assert result.exit_code == 0
        assert "Path: path" in result.output

    def test_remove_entire_string_as_prefix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test removing prefix when it's the entire string."""

        @command()
        @option("text", default="prefix")
        @remove_prefix("prefix")
        def cmd(text: str) -> None:
            click.echo(f"Result: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", "prefix"])
        assert result.exit_code == 0
        assert "Result: ''" in result.output


class TestRemovePrefixURLs:
    """Test remove_prefix with URLs and protocols."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_http_protocol(self, cli_runner: CliRunner) -> None:
        """Test removing http:// protocol."""

        @command()
        @option("url", default="http://example.com")
        @remove_prefix("http://")
        def cmd(url: str) -> None:
            click.echo(f"Domain: {url}")

        result = cli_runner.invoke(cmd, ["--url", "http://example.com"])
        assert result.exit_code == 0
        assert "Domain: example.com" in result.output

    def test_remove_https_protocol(self, cli_runner: CliRunner) -> None:
        """Test removing https:// protocol."""

        @command()
        @option("url", default="https://example.com")
        @remove_prefix("https://")
        def cmd(url: str) -> None:
            click.echo(f"Domain: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0
        assert "Domain: example.com" in result.output

    def test_remove_www_prefix(self, cli_runner: CliRunner) -> None:
        """Test removing www. prefix."""

        @command()
        @option("domain", default="www.example.com")
        @remove_prefix("www.")
        def cmd(domain: str) -> None:
            click.echo(f"Domain: {domain}")

        result = cli_runner.invoke(cmd, ["--domain", "www.example.com"])
        assert result.exit_code == 0
        assert "Domain: example.com" in result.output


class TestRemovePrefixChaining:
    """Test chaining remove_prefix decorator."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_multiple_remove_prefix(self, cli_runner: CliRunner) -> None:
        """Test chaining multiple remove_prefix calls."""

        @command()
        @option("url", default="https://www.example.com")
        @remove_prefix("https://")
        @remove_prefix("www.")
        def cmd(url: str) -> None:
            click.echo(f"Domain: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://www.example.com"])
        assert result.exit_code == 0
        assert "Domain: example.com" in result.output

    def test_chain_with_strip(self, cli_runner: CliRunner) -> None:
        """Test chaining with strip decorator."""

        @command()
        @option("text", default="  prefix-text  ")
        @strip()
        @remove_prefix("prefix-")
        def cmd(text: str) -> None:
            click.echo(f"Result: {text}")

        result = cli_runner.invoke(cmd, ["--text", "  prefix-text  "])
        assert result.exit_code == 0
        assert "Result: text" in result.output


class TestRemovePrefixEdgeCases:
    """Test edge cases for remove_prefix."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_prefix_empty_string(self, cli_runner: CliRunner) -> None:
        """Test remove_prefix with empty string."""

        @command()
        @option("text", default="")
        @remove_prefix("prefix")
        def cmd(text: str) -> None:
            click.echo(f"Result: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0
        assert "Result: ''" in result.output

    def test_remove_prefix_with_special_chars(
        self, cli_runner: CliRunner
    ) -> None:
        """Test remove_prefix with special characters."""

        @command()
        @option("text", default="***important***")
        @remove_prefix("***")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "***important***"])
        assert result.exit_code == 0
        assert "Text: important***" in result.output

    def test_remove_prefix_only_once(self, cli_runner: CliRunner) -> None:
        """Test that prefix is only removed once."""

        @command()
        @option("text", default="prefixprefixtext")
        @remove_prefix("prefix")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "prefixprefixtext"])
        assert result.exit_code == 0
        assert "Text: prefixtext" in result.output


class TestRemovePrefixPractical:
    """Test practical use cases for remove_prefix."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_clean_url_protocol(self, cli_runner: CliRunner) -> None:
        """Test removing URL protocol."""

        @command()
        @option("url", default="https://example.com")
        @remove_prefix("https://")
        def cmd(url: str) -> None:
            click.echo(f"Domain: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0
        assert "Domain: example.com" in result.output

    def test_normalize_path_prefix(self, cli_runner: CliRunner) -> None:
        """Test normalizing file path prefix."""

        @command()
        @option("path", default="./relative/path")
        @remove_prefix("./")
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "./relative/path"])
        assert result.exit_code == 0
        assert "Path: relative/path" in result.output

    def test_clean_command_prefix(self, cli_runner: CliRunner) -> None:
        """Test cleaning command line prefix."""

        @command()
        @option("output", default="$ command output")
        @remove_prefix("$ ")
        def cmd(output: str) -> None:
            click.echo(f"Output: {output}")

        result = cli_runner.invoke(cmd, ["--output", "$ command output"])
        assert result.exit_code == 0
        assert "Output: command output" in result.output
