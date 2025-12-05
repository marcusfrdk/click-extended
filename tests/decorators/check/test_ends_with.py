"""Comprehensive tests for ends_with decorator."""

import re

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.check.ends_with import EndsWith, ends_with
from click_extended.decorators.check.length import length
from click_extended.decorators.check.starts_with import starts_with


class TestEndsWithInit:
    """Test EndsWith class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_ends_with_is_child_node(self) -> None:
        """Test that EndsWith extends ChildNode."""
        node = EndsWith(name="test")
        assert isinstance(node, ChildNode)

    def test_ends_with_has_handle_str(self) -> None:
        """Test that EndsWith implements handle_str method."""
        node = EndsWith(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestEndsWithExactMatching:
    """Test EndsWith with exact suffix matching."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_exact_single_suffix_match(self, cli_runner: CliRunner) -> None:
        """Test exact matching with single suffix."""

        @command()
        @option("filename", default="document.pdf")
        @ends_with(".pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.pdf"])
        assert result.exit_code == 0
        assert "File: document.pdf" in result.output

    def test_exact_single_suffix_no_match(self, cli_runner: CliRunner) -> None:
        """Test exact matching fails with wrong suffix."""

        @command()
        @option("filename", default="document.txt")
        @ends_with(".pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.txt"])
        assert result.exit_code != 0
        assert "Value must end with the pattern '.pdf'" in result.output

    def test_exact_multiple_suffixes_first_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exact matching with multiple suffixes (first matches)."""

        @command()
        @option("filename", default="image.jpg")
        @ends_with(".jpg", ".png")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "image.jpg"])
        assert result.exit_code == 0

    def test_exact_multiple_suffixes_second_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exact matching with multiple suffixes (second matches)."""

        @command()
        @option("filename", default="image.png")
        @ends_with(".jpg", ".png")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "image.png"])
        assert result.exit_code == 0

    def test_exact_multiple_suffixes_no_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exact matching fails when none of multiple suffixes match."""

        @command()
        @option("filename", default="image.gif")
        @ends_with(".jpg", ".png")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "image.gif"])
        assert result.exit_code != 0
        assert (
            "Value must end with one of the patterns '.jpg' or '.png'"
            in result.output
        )


class TestEndsWithGlobPatterns:
    """Test EndsWith with glob pattern matching."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_glob_asterisk_wildcard_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with * wildcard."""

        @command()
        @option("filename", default="report_2024.pdf")
        @ends_with("*_2024.pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "report_2024.pdf"])
        assert result.exit_code == 0

    def test_glob_asterisk_wildcard_no_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test glob pattern with * wildcard fails."""

        @command()
        @option("filename", default="report_2023.pdf")
        @ends_with("*_2024.pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "report_2023.pdf"])
        assert result.exit_code != 0
        assert "Value must end with the pattern '*_2024.pdf'" in result.output

    def test_glob_question_wildcard_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with ? wildcard (single character)."""

        @command()
        @option("filename", default="fileA.txt")
        @ends_with("file?.txt")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "fileA.txt"])
        assert result.exit_code == 0

    def test_glob_question_wildcard_no_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test glob pattern with ? wildcard fails (too many chars)."""

        @command()
        @option("filename", default="fileAB.txt")
        @ends_with("file?.txt")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "fileAB.txt"])
        assert result.exit_code != 0

    def test_glob_character_class_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with character class [abc]."""

        @command()
        @option("filename", default="reportA.pdf")
        @ends_with("report[ABC].pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "reportA.pdf"])
        assert result.exit_code == 0

    def test_glob_character_class_no_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with character class fails."""

        @command()
        @option("filename", default="reportD.pdf")
        @ends_with("report[ABC].pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "reportD.pdf"])
        assert result.exit_code != 0

    def test_glob_multiple_patterns(self, cli_runner: CliRunner) -> None:
        """Test multiple glob patterns (OR logic)."""

        @command()
        @option("filename", default="backup_prod.tar.gz")
        @ends_with("*_test.tar.gz", "*_prod.tar.gz")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "backup_prod.tar.gz"])
        assert result.exit_code == 0


class TestEndsWithRegexPatterns:
    """Test EndsWith with regex pattern matching."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_regex_simple_pattern_match(self, cli_runner: CliRunner) -> None:
        """Test regex pattern with simple alternation."""

        @command()
        @option("filename", default="document.pdf")
        @ends_with(re.compile(r"\.(pdf|docx)$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.pdf"])
        assert result.exit_code == 0

    def test_regex_alternation_first_option(
        self, cli_runner: CliRunner
    ) -> None:
        """Test regex pattern matches first option."""

        @command()
        @option("filename", default="file.jpg")
        @ends_with(re.compile(r"\.(jpg|png|gif)$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.jpg"])
        assert result.exit_code == 0

    def test_regex_alternation_second_option(
        self, cli_runner: CliRunner
    ) -> None:
        """Test regex pattern matches second option."""

        @command()
        @option("filename", default="file.png")
        @ends_with(re.compile(r"\.(jpg|png|gif)$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.png"])
        assert result.exit_code == 0

    def test_regex_pattern_no_match(self, cli_runner: CliRunner) -> None:
        """Test regex pattern fails to match."""

        @command()
        @option("filename", default="file.bmp")
        @ends_with(re.compile(r"\.(jpg|png|gif)$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.bmp"])
        assert result.exit_code != 0
        assert (
            r"Value must end with the pattern '\.(jpg|png|gif)$'"
            in result.output
        )

    def test_regex_with_digits(self, cli_runner: CliRunner) -> None:
        """Test regex pattern matching digits."""

        @command()
        @option("filename", default="backup.v123")
        @ends_with(re.compile(r"\.v\d+$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "backup.v123"])
        assert result.exit_code == 0

    def test_regex_multiple_patterns(self, cli_runner: CliRunner) -> None:
        """Test multiple regex patterns (OR logic)."""

        @command()
        @option("filename", default="archive.tar.gz")
        @ends_with(re.compile(r"\.zip$"), re.compile(r"\.tar\.gz$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "archive.tar.gz"])
        assert result.exit_code == 0


class TestEndsWithMixedPatterns:
    """Test EndsWith with mixed pattern types."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_mixed_exact_and_glob(self, cli_runner: CliRunner) -> None:
        """Test mixing exact strings and glob patterns."""

        @command()
        @option("filename", default="data.csv")
        @ends_with(".csv", "*.txt", "*_backup.json")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "data.csv"])
        assert result.exit_code == 0

    def test_mixed_exact_and_regex(self, cli_runner: CliRunner) -> None:
        """Test mixing exact strings and regex patterns."""

        @command()
        @option("filename", default="image.png")
        @ends_with(".txt", re.compile(r"\.(jpg|png)$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "image.png"])
        assert result.exit_code == 0

    def test_mixed_glob_and_regex(self, cli_runner: CliRunner) -> None:
        """Test mixing glob and regex patterns."""

        @command()
        @option("filename", default="test_123.log")
        @ends_with("*_prod.log", re.compile(r"_\d+\.log$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "test_123.log"])
        assert result.exit_code == 0

    def test_mixed_all_three_types(self, cli_runner: CliRunner) -> None:
        """Test mixing exact, glob, and regex patterns."""

        @command()
        @option("filename", default="report.pdf")
        @ends_with(".txt", "*_backup.json", re.compile(r"\.pdf$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "report.pdf"])
        assert result.exit_code == 0


class TestEndsWithChaining:
    """Test EndsWith chaining with other decorators."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_with_multiple_ends_with(self, cli_runner: CliRunner) -> None:
        """Test chaining multiple ends_with decorators."""

        @command()
        @option("filename", default="document.pdf")
        @ends_with(".pdf")
        @ends_with("ment.pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "document.pdf"])
        assert result.exit_code == 0

    def test_chain_with_max_length(self, cli_runner: CliRunner) -> None:
        """Test chaining ends_with with max_length."""

        @command()
        @option("filename", default="file.txt")
        @ends_with(".txt")
        @length(max=20)
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.txt"])
        assert result.exit_code == 0

    def test_chain_with_starts_with(self, cli_runner: CliRunner) -> None:
        """Test chaining ends_with with starts_with."""

        @command()
        @option("filename", default="data_export.csv")
        @starts_with("data_")
        @ends_with(".csv")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "data_export.csv"])
        assert result.exit_code == 0


class TestEndsWithErrorMessages:
    """Test EndsWith error message formatting."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_error_message_single_pattern(self, cli_runner: CliRunner) -> None:
        """Test error message with single pattern."""

        @command()
        @option("filename", default="file.txt")
        @ends_with(".pdf")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.txt"])
        assert result.exit_code != 0
        assert "Value must end with the pattern '.pdf'" in result.output

    def test_error_message_two_patterns(self, cli_runner: CliRunner) -> None:
        """Test error message with two patterns."""

        @command()
        @option("filename", default="file.txt")
        @ends_with(".jpg", ".png")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.txt"])
        assert result.exit_code != 0
        assert (
            "Value must end with one of the patterns '.jpg' or '.png'"
            in result.output
        )

    def test_error_message_three_patterns(self, cli_runner: CliRunner) -> None:
        """Test error message with three patterns."""

        @command()
        @option("filename", default="file.txt")
        @ends_with(".jpg", ".png", ".gif")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.txt"])
        assert result.exit_code != 0
        assert "one of the patterns '.jpg', '.png' or '.gif'" in result.output

    def test_error_message_with_regex_pattern(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message shows regex pattern string."""

        @command()
        @option("filename", default="file.txt")
        @ends_with(re.compile(r"\.(jpg|png)$"))
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "file.txt"])
        assert result.exit_code != 0
        assert (
            r"Value must end with the pattern '\.(jpg|png)$'" in result.output
        )


class TestEndsWithEdgeCases:
    """Test EndsWith edge cases."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_empty_string_value(self, cli_runner: CliRunner) -> None:
        """Test validation with empty string value."""

        @command()
        @option("text", default="")
        @ends_with("suffix")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code != 0

    def test_value_equals_suffix(self, cli_runner: CliRunner) -> None:
        """Test when value exactly equals the suffix."""

        @command()
        @option("text", default="suffix")
        @ends_with("suffix")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "suffix"])
        assert result.exit_code == 0

    def test_case_sensitive_matching(self, cli_runner: CliRunner) -> None:
        """Test that matching is case-sensitive."""

        @command()
        @option("text", default="Hello")
        @ends_with("HELLO")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "Hello"])
        assert result.exit_code != 0

    def test_special_characters_in_suffix(self, cli_runner: CliRunner) -> None:
        """Test suffix with special characters."""

        @command()
        @option("text", default="price$99")
        @ends_with("$99")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "price$99"])
        assert result.exit_code == 0

    def test_unicode_characters(self, cli_runner: CliRunner) -> None:
        """Test with unicode characters."""

        @command()
        @option("text", default="你好世界")
        @ends_with("世界")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "你好世界"])
        assert result.exit_code == 0

    def test_glob_pattern_without_leading_content(
        self, cli_runner: CliRunner
    ) -> None:
        """Test glob pattern matches even without content before pattern."""

        @command()
        @option("text", default="_test")
        @ends_with("*_test")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "_test"])
        assert result.exit_code == 0

    def test_multiple_dots_in_filename(self, cli_runner: CliRunner) -> None:
        """Test filename with multiple dots."""

        @command()
        @option("filename", default="archive.tar.gz")
        @ends_with(".tar.gz")
        def cmd(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(cmd, ["--filename", "archive.tar.gz"])
        assert result.exit_code == 0
