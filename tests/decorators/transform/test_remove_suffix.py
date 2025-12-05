"""Comprehensive tests for remove_suffix decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.transform.remove_suffix import (
    RemoveSuffix,
    remove_suffix,
)
from click_extended.decorators.transform.strip import strip


class TestRemoveSuffixInit:
    """Test RemoveSuffix class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_suffix_is_child_node(self) -> None:
        """Test that RemoveSuffix extends ChildNode."""
        node = RemoveSuffix(name="test")
        assert isinstance(node, ChildNode)

    def test_remove_suffix_has_handle_str(self) -> None:
        """Test that RemoveSuffix implements handle_str method."""
        node = RemoveSuffix(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestRemoveSuffixBasic:
    """Test remove_suffix decorator basic functionality."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_simple_suffix(self, cli_runner: CliRunner) -> None:
        """Test removing a simple suffix."""

        @command()
        @option("filename", default="document.txt")
        @remove_suffix(".txt")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.txt"])
        assert result.exit_code == 0
        assert "Name: document" in result.output

    def test_remove_suffix_not_present(self, cli_runner: CliRunner) -> None:
        """Test behavior when suffix is not present."""

        @command()
        @option("filename", default="document.pdf")
        @remove_suffix(".txt")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.pdf"])
        assert result.exit_code == 0
        assert "Name: document.pdf" in result.output

    def test_remove_suffix_case_sensitive(self, cli_runner: CliRunner) -> None:
        """Test that removal is case-sensitive."""

        @command()
        @option("filename", default="document.TXT")
        @remove_suffix(".txt")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.TXT"])
        assert result.exit_code == 0
        assert "Name: document.TXT" in result.output

    def test_remove_single_character_suffix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test removing a single character suffix."""

        @command()
        @option("path", default="path/")
        @remove_suffix("/")
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "path/"])
        assert result.exit_code == 0
        assert "Path: path" in result.output

    def test_remove_entire_string_as_suffix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test removing suffix when it's the entire string."""

        @command()
        @option("text", default="suffix")
        @remove_suffix("suffix")
        def cmd(text: str) -> None:
            click.echo(f"Result: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", "suffix"])
        assert result.exit_code == 0
        assert "Result: ''" in result.output


class TestRemoveSuffixFileExtensions:
    """Test remove_suffix with file extensions."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_py_extension(self, cli_runner: CliRunner) -> None:
        """Test removing .py extension."""

        @command()
        @option("filename", default="script.py")
        @remove_suffix(".py")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "script.py"])
        assert result.exit_code == 0
        assert "Name: script" in result.output

    def test_remove_json_extension(self, cli_runner: CliRunner) -> None:
        """Test removing .json extension."""

        @command()
        @option("filename", default="config.json")
        @remove_suffix(".json")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "config.json"])
        assert result.exit_code == 0
        assert "Name: config" in result.output

    def test_remove_tar_gz_extension(self, cli_runner: CliRunner) -> None:
        """Test removing compound extension."""

        @command()
        @option("filename", default="archive.tar.gz")
        @remove_suffix(".tar.gz")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "archive.tar.gz"])
        assert result.exit_code == 0
        assert "Name: archive" in result.output


class TestRemoveSuffixChaining:
    """Test chaining remove_suffix decorator."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_multiple_remove_suffix(self, cli_runner: CliRunner) -> None:
        """Test chaining multiple remove_suffix calls."""

        @command()
        @option("filename", default="document.backup.txt")
        @remove_suffix(".txt")
        @remove_suffix(".backup")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.backup.txt"])
        assert result.exit_code == 0
        assert "Name: document" in result.output

    def test_chain_with_strip(self, cli_runner: CliRunner) -> None:
        """Test chaining with strip decorator."""

        @command()
        @option("text", default="  text-suffix  ")
        @strip()
        @remove_suffix("-suffix")
        def cmd(text: str) -> None:
            click.echo(f"Result: {text}")

        result = cli_runner.invoke(cmd, ["--text", "  text-suffix  "])
        assert result.exit_code == 0
        assert "Result: text" in result.output


class TestRemoveSuffixEdgeCases:
    """Test edge cases for remove_suffix."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_remove_suffix_empty_string(self, cli_runner: CliRunner) -> None:
        """Test remove_suffix with empty string."""

        @command()
        @option("text", default="")
        @remove_suffix("suffix")
        def cmd(text: str) -> None:
            click.echo(f"Result: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0
        assert "Result: ''" in result.output

    def test_remove_suffix_with_special_chars(
        self, cli_runner: CliRunner
    ) -> None:
        """Test remove_suffix with special characters."""

        @command()
        @option("text", default="***important***")
        @remove_suffix("***")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "***important***"])
        assert result.exit_code == 0
        assert "Text: ***important" in result.output

    def test_remove_suffix_only_once(self, cli_runner: CliRunner) -> None:
        """Test that suffix is only removed once."""

        @command()
        @option("text", default="textsuffixsuffix")
        @remove_suffix("suffix")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "textsuffixsuffix"])
        assert result.exit_code == 0
        assert "Text: textsuffix" in result.output


class TestRemoveSuffixPractical:
    """Test practical use cases for remove_suffix."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_get_filename_without_extension(
        self, cli_runner: CliRunner
    ) -> None:
        """Test extracting filename without extension."""

        @command()
        @option("file", default="report.pdf")
        @remove_suffix(".pdf")
        def cmd(file: str) -> None:
            click.echo(f"Filename: {file}")

        result = cli_runner.invoke(cmd, ["--file", "report.pdf"])
        assert result.exit_code == 0
        assert "Filename: report" in result.output

    def test_normalize_path_suffix(self, cli_runner: CliRunner) -> None:
        """Test normalizing file path suffix."""

        @command()
        @option("path", default="relative/path/")
        @remove_suffix("/")
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "relative/path/"])
        assert result.exit_code == 0
        assert "Path: relative/path" in result.output

    def test_clean_trailing_slash(self, cli_runner: CliRunner) -> None:
        """Test removing trailing slash from URLs."""

        @command()
        @option("url", default="https://example.com/")
        @remove_suffix("/")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com/"])
        assert result.exit_code == 0
        assert "URL: https://example.com" in result.output
