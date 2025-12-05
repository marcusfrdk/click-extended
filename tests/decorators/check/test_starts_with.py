"""Comprehensive tests for starts_with decorator."""

import re

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.decorators.check.max_length import max_length
from click_extended.decorators.check.starts_with import StartsWith, starts_with


class TestStartsWithInit:
    """Test StartsWith class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_starts_with_is_child_node(self) -> None:
        """Test that StartsWith extends ChildNode."""
        node = StartsWith(name="test")
        assert isinstance(node, ChildNode)

    def test_starts_with_has_handle_str(self) -> None:
        """Test that StartsWith implements handle_str method."""
        node = StartsWith(name="test")
        assert hasattr(node, "handle_str")
        assert callable(node.handle_str)


class TestStartsWithExactMatching:
    """Test StartsWith with exact prefix matching."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_exact_single_prefix_match(self, cli_runner: CliRunner) -> None:
        """Test exact matching with single prefix."""

        @command()
        @option("url", default="https://example.com")
        @starts_with("https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0
        assert "URL: https://example.com" in result.output

    def test_exact_single_prefix_no_match(self, cli_runner: CliRunner) -> None:
        """Test exact matching fails with wrong prefix."""

        @command()
        @option("url", default="ftp://example.com")
        @starts_with("https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ftp://example.com"])
        assert result.exit_code != 0
        assert "Value must start with the pattern 'https://'" in result.output

    def test_exact_multiple_prefixes_first_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exact matching with multiple prefixes (first matches)."""

        @command()
        @option("url", default="http://example.com")
        @starts_with("http://", "https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "http://example.com"])
        assert result.exit_code == 0

    def test_exact_multiple_prefixes_second_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exact matching with multiple prefixes (second matches)."""

        @command()
        @option("url", default="https://example.com")
        @starts_with("http://", "https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_exact_multiple_prefixes_no_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exact matching fails when none of multiple prefixes match."""

        @command()
        @option("url", default="ftp://example.com")
        @starts_with("http://", "https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ftp://example.com"])
        assert result.exit_code != 0
        assert (
            "Value must start with one of the patterns 'http://' or 'https://'"
            in result.output
        )


class TestStartsWithGlobPatterns:
    """Test StartsWith with glob pattern matching."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_glob_asterisk_wildcard_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with * wildcard."""

        @command()
        @option("name", default="user_123")
        @starts_with("user_*")
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "user_123"])
        assert result.exit_code == 0

    def test_glob_asterisk_wildcard_no_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test glob pattern with * wildcard fails."""

        @command()
        @option("name", default="admin_123")
        @starts_with("user_*")
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "admin_123"])
        assert result.exit_code != 0
        assert "Value must start with the pattern 'user_*'" in result.output

    def test_glob_question_wildcard_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with ? wildcard (single character)."""

        @command()
        @option("code", default="A1234")
        @starts_with("?1234")
        def cmd(code: str) -> None:
            click.echo(f"Code: {code}")

        result = cli_runner.invoke(cmd, ["--code", "A1234"])
        assert result.exit_code == 0

    def test_glob_question_wildcard_no_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test glob pattern with ? wildcard fails (too many chars)."""

        @command()
        @option("code", default="AB1234")
        @starts_with("?1234")
        def cmd(code: str) -> None:
            click.echo(f"Code: {code}")

        result = cli_runner.invoke(cmd, ["--code", "AB1234"])
        assert result.exit_code != 0

    def test_glob_character_class_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with character class [abc]."""

        @command()
        @option("grade", default="A_student")
        @starts_with("[ABC]_student")
        def cmd(grade: str) -> None:
            click.echo(f"Grade: {grade}")

        result = cli_runner.invoke(cmd, ["--grade", "A_student"])
        assert result.exit_code == 0

    def test_glob_character_class_no_match(self, cli_runner: CliRunner) -> None:
        """Test glob pattern with character class fails."""

        @command()
        @option("grade", default="D_student")
        @starts_with("[ABC]_student")
        def cmd(grade: str) -> None:
            click.echo(f"Grade: {grade}")

        result = cli_runner.invoke(cmd, ["--grade", "D_student"])
        assert result.exit_code != 0

    def test_glob_multiple_patterns(self, cli_runner: CliRunner) -> None:
        """Test multiple glob patterns (OR logic)."""

        @command()
        @option("name", default="admin_456")
        @starts_with("user_*", "admin_*")
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "admin_456"])
        assert result.exit_code == 0


class TestStartsWithRegexPatterns:
    """Test StartsWith with regex pattern matching."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_regex_simple_pattern_match(self, cli_runner: CliRunner) -> None:
        """Test regex pattern with simple alternation."""

        @command()
        @option("url", default="https://example.com")
        @starts_with(re.compile(r"https?://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_regex_alternation_http(self, cli_runner: CliRunner) -> None:
        """Test regex pattern matches http."""

        @command()
        @option("url", default="http://example.com")
        @starts_with(re.compile(r"https?://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "http://example.com"])
        assert result.exit_code == 0

    def test_regex_alternation_https(self, cli_runner: CliRunner) -> None:
        """Test regex pattern matches https."""

        @command()
        @option("url", default="https://example.com")
        @starts_with(re.compile(r"https?://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_regex_pattern_no_match(self, cli_runner: CliRunner) -> None:
        """Test regex pattern fails to match."""

        @command()
        @option("url", default="ftp://example.com")
        @starts_with(re.compile(r"https?://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ftp://example.com"])
        assert result.exit_code != 0
        assert "Value must start with the pattern 'https?://'" in result.output

    def test_regex_complex_pattern(self, cli_runner: CliRunner) -> None:
        """Test complex regex pattern with groups."""

        @command()
        @option("email", default="user@example.com")
        @starts_with(re.compile(r"[a-zA-Z0-9._%+-]+@"))
        def cmd(email: str) -> None:
            click.echo(f"Email: {email}")

        result = cli_runner.invoke(cmd, ["--email", "user@example.com"])
        assert result.exit_code == 0

    def test_regex_multiple_patterns(self, cli_runner: CliRunner) -> None:
        """Test multiple regex patterns (OR logic)."""

        @command()
        @option("url", default="ftp://example.com")
        @starts_with(re.compile(r"https?://"), re.compile(r"ftp://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ftp://example.com"])
        assert result.exit_code == 0


class TestStartsWithMixedPatterns:
    """Test StartsWith with mixed pattern types."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_mixed_exact_and_glob(self, cli_runner: CliRunner) -> None:
        """Test mixing exact strings and glob patterns."""

        @command()
        @option("name", default="www.example.com")
        @starts_with("www.", "*.local", "dev_*")
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "www.example.com"])
        assert result.exit_code == 0

    def test_mixed_exact_and_regex(self, cli_runner: CliRunner) -> None:
        """Test mixing exact strings and regex patterns."""

        @command()
        @option("url", default="https://example.com")
        @starts_with("www.", re.compile(r"https?://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_mixed_glob_and_regex(self, cli_runner: CliRunner) -> None:
        """Test mixing glob and regex patterns."""

        @command()
        @option("name", default="user_123")
        @starts_with("admin_*", re.compile(r"user_\d+"))
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "user_123"])
        assert result.exit_code == 0

    def test_mixed_all_three_types(self, cli_runner: CliRunner) -> None:
        """Test mixing exact, glob, and regex patterns."""

        @command()
        @option("url", default="ftp://example.com")
        @starts_with("www.", "local_*", re.compile(r"ftp://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ftp://example.com"])
        assert result.exit_code == 0


class TestStartsWithChaining:
    """Test StartsWith chaining with other decorators."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_chain_with_multiple_starts_with(
        self, cli_runner: CliRunner
    ) -> None:
        """Test chaining multiple starts_with decorators."""

        @command()
        @option("url", default="https://example.com")
        @starts_with("https://")
        @starts_with("https://example")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_chain_with_max_length(self, cli_runner: CliRunner) -> None:
        """Test chaining starts_with with max_length."""

        @command()
        @option("code", default="ABC123")
        @starts_with("ABC")
        @max_length(10)
        def cmd(code: str) -> None:
            click.echo(f"Code: {code}")

        result = cli_runner.invoke(cmd, ["--code", "ABC123"])
        assert result.exit_code == 0


class TestStartsWithErrorMessages:
    """Test StartsWith error message formatting."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_error_message_single_pattern(self, cli_runner: CliRunner) -> None:
        """Test error message with single pattern."""

        @command()
        @option("url", default="ftp://example.com")
        @starts_with("https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ftp://example.com"])
        assert result.exit_code != 0
        assert "Value must start with the pattern 'https://'" in result.output

    def test_error_message_two_patterns(self, cli_runner: CliRunner) -> None:
        """Test error message with two patterns."""

        @command()
        @option("url", default="ftp://example.com")
        @starts_with("http://", "https://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ftp://example.com"])
        assert result.exit_code != 0
        assert (
            "Value must start with one of the patterns 'http://' or 'https://'"
            in result.output
        )

    def test_error_message_three_patterns(self, cli_runner: CliRunner) -> None:
        """Test error message with three patterns."""

        @command()
        @option("url", default="ssh://example.com")
        @starts_with("http://", "https://", "ftp://")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ssh://example.com"])
        assert result.exit_code != 0
        assert (
            "one of the patterns 'http://', 'https://' or 'ftp://'"
            in result.output
        )

    def test_error_message_with_regex_pattern(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message shows regex pattern string."""

        @command()
        @option("url", default="ssh://example.com")
        @starts_with(re.compile(r"https?://"))
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "ssh://example.com"])
        assert result.exit_code != 0
        assert "Value must start with the pattern 'https?://'" in result.output


class TestStartsWithEdgeCases:
    """Test StartsWith edge cases."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_empty_string_value(self, cli_runner: CliRunner) -> None:
        """Test validation with empty string value."""

        @command()
        @option("text", default="")
        @starts_with("prefix")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code != 0

    def test_value_equals_prefix(self, cli_runner: CliRunner) -> None:
        """Test when value exactly equals the prefix."""

        @command()
        @option("text", default="prefix")
        @starts_with("prefix")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "prefix"])
        assert result.exit_code == 0

    def test_case_sensitive_matching(self, cli_runner: CliRunner) -> None:
        """Test that matching is case-sensitive."""

        @command()
        @option("text", default="Hello")
        @starts_with("hello")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "Hello"])
        assert result.exit_code != 0

    def test_special_characters_in_prefix(self, cli_runner: CliRunner) -> None:
        """Test prefix with special characters."""

        @command()
        @option("text", default="$variable_name")
        @starts_with("$variable")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "$variable_name"])
        assert result.exit_code == 0

    def test_unicode_characters(self, cli_runner: CliRunner) -> None:
        """Test with unicode characters."""

        @command()
        @option("text", default="你好世界")
        @starts_with("你好")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "你好世界"])
        assert result.exit_code == 0

    def test_glob_pattern_without_trailing_content(
        self, cli_runner: CliRunner
    ) -> None:
        """Test glob pattern matches even without content after pattern."""

        @command()
        @option("text", default="user_")
        @starts_with("user_*")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "user_"])
        assert result.exit_code == 0
