"""Comprehensive tests for confirm_if decorator."""

import os
from typing import Any
from unittest.mock import patch

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other._tree import Tree
from click_extended.core.other.context import Context
from click_extended.decorators.misc.confirm_if import ConfirmIf, confirm_if


class TestConfirmIfInit:
    """Test ConfirmIf class initialization."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_confirm_if_is_child_node(self) -> None:
        """Test that ConfirmIf extends ChildNode."""
        node = ConfirmIf(name="test")
        assert isinstance(node, ChildNode)

    def test_confirm_if_has_handle_all_method(self) -> None:
        """Test that ConfirmIf implements handle_all handler."""
        node = ConfirmIf(name="test")
        assert hasattr(node, "handle_all")
        assert callable(node.handle_all)


class TestConfirmIfValueOnlyPredicate:
    """Test confirm_if decorator with value-only predicate function."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_predicate_false_skips_confirmation(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that False predicate skips confirmation."""

        @command()
        @option("count", type=int, default=50)
        @confirm_if("Proceed?", lambda x: x > 100)
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["--count", "50"])
        assert result.exit_code == 0
        assert "Count: 50" in result.output
        assert "Proceed?" not in result.output

    def test_predicate_true_prompts_confirmation(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that True predicate prompts for confirmation."""

        @command()
        @option("count", type=int, default=150)
        @confirm_if("Proceed?", lambda x: x > 100)
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["--count", "150"], input="y\n")
        assert result.exit_code == 0
        assert "Proceed?" in result.output
        assert "Count: 150" in result.output

    def test_truthy_response_continues(self, cli_runner: CliRunner) -> None:
        """Test that truthy response allows continuation."""

        @command()
        @option("value", type=int, default=200)
        @confirm_if("Continue?", lambda x: x > 100)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        # Test 'y'
        result = cli_runner.invoke(cmd, ["--value", "200"], input="y\n")
        assert result.exit_code == 0
        assert "Value: 200" in result.output

        # Test 'yes'
        result = cli_runner.invoke(cmd, ["--value", "200"], input="yes\n")
        assert result.exit_code == 0
        assert "Value: 200" in result.output

    def test_non_truthy_response_aborts(self, cli_runner: CliRunner) -> None:
        """Test that any non-truthy response aborts execution."""

        @command()
        @option("value", type=int, default=200)
        @confirm_if("Continue?", lambda x: x > 100)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        # Test 'n'
        result = cli_runner.invoke(cmd, ["--value", "200"], input="n\n")
        assert result.exit_code == 1
        assert "Value: 200" not in result.output

        # Test 'no'
        result = cli_runner.invoke(cmd, ["--value", "200"], input="no\n")
        assert result.exit_code == 1
        assert "Value: 200" not in result.output

        # Test arbitrary string
        result = cli_runner.invoke(cmd, ["--value", "200"], input="maybe\n")
        assert result.exit_code == 1
        assert "Value: 200" not in result.output


class TestConfirmIfValueContextPredicate:
    """Test confirm_if decorator with value+context predicate function."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_context_aware_predicate(self, cli_runner: CliRunner) -> None:
        """Test predicate that uses context to check other parameters."""

        def validator(val: Any, ctx: Context) -> bool:
            return not ctx.get_parent("force").get_value()  # type: ignore

        @command()
        @option("force", is_flag=True)
        @option("file", default="test.txt")
        @confirm_if("Delete {value}?", validator)
        def cmd(force: bool, file: str) -> None:
            click.echo(f"Deleted {file}")

        result = cli_runner.invoke(
            cmd, ["--file", "important.txt"], input="y\n"
        )
        assert result.exit_code == 0
        assert "Delete important.txt?" in result.output
        assert "Deleted important.txt" in result.output

        result = cli_runner.invoke(cmd, ["--force", "--file", "important.txt"])
        assert result.exit_code == 0
        assert "Delete important.txt?" not in result.output
        assert "Deleted important.txt" in result.output


class TestConfirmIfPromptFormatting:
    """Test confirm_if decorator prompt formatting with value."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_prompt_with_value_placeholder(self, cli_runner: CliRunner) -> None:
        """Test that {value} placeholder is replaced in prompt."""

        @command()
        @option("filename", default="data.txt")
        @confirm_if("Delete {value}?", lambda x: True)
        def cmd(filename: str) -> None:
            click.echo(f"Deleted {filename}")

        result = cli_runner.invoke(
            cmd, ["--filename", "important.log"], input="y\n"
        )
        assert result.exit_code == 0
        assert "Delete important.log?" in result.output

    def test_prompt_without_placeholder(self, cli_runner: CliRunner) -> None:
        """Test prompt without {value} placeholder works."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Are you sure?", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="yes\n")
        assert result.exit_code == 0
        assert "Are you sure?" in result.output


class TestConfirmIfPromptAutoFormatting:
    """Test automatic prompt formatting."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_adds_yn_suffix(self, cli_runner: CliRunner) -> None:
        """Test that (y/n): is automatically added to prompts."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Delete file", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="y\n")
        assert result.exit_code == 0
        assert "Delete file (y/n):" in result.output

    def test_removes_trailing_colon(self, cli_runner: CliRunner) -> None:
        """Test that trailing colons are removed before adding (y/n):."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Continue:", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="yes\n")
        assert result.exit_code == 0
        assert "Continue (y/n):" in result.output
        assert "Continue: (y/n):" not in result.output

    def test_removes_question_mark_colon(self, cli_runner: CliRunner) -> None:
        """Test handling of prompts ending with question mark and colon."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Are you sure?:", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="y\n")
        assert result.exit_code == 0
        assert "Are you sure? (y/n):" in result.output

    def test_custom_truthy_shows_in_hint(self, cli_runner: CliRunner) -> None:
        """Test that custom truthy values show in prompt hint."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Proceed", lambda x: x > 50, truthy=["ok", "proceed"])
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="ok\n")
        assert result.exit_code == 0
        assert "Proceed (ok/n):" in result.output
        assert "(y/n):" not in result.output


class TestConfirmIfDefaultTruthyValues:
    """Test default truthy values (y, yes, ok, 1)."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_y_is_truthy(self, cli_runner: CliRunner) -> None:
        """Test that 'y' is accepted."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Continue", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="y\n")
        assert result.exit_code == 0

    def test_yes_is_truthy(self, cli_runner: CliRunner) -> None:
        """Test that 'yes' is accepted."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Continue", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="yes\n")
        assert result.exit_code == 0

    def test_ok_is_truthy(self, cli_runner: CliRunner) -> None:
        """Test that 'ok' is accepted."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Continue", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="ok\n")
        assert result.exit_code == 0

    def test_1_is_truthy(self, cli_runner: CliRunner) -> None:
        """Test that '1' is accepted."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Continue", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="1\n")
        assert result.exit_code == 0


class TestConfirmIfCustomTruthy:
    """Test confirm_if decorator with custom truthy values."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_custom_truthy_values(self, cli_runner: CliRunner) -> None:
        """Test custom truthy response values."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if(
            "Proceed?",
            lambda x: x > 50,
            truthy=["ok", "proceed", "continue"],
        )
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        # Test custom truthy values work
        result = cli_runner.invoke(cmd, ["--value", "100"], input="ok\n")
        assert result.exit_code == 0
        assert "Value: 100" in result.output

        result = cli_runner.invoke(cmd, ["--value", "100"], input="proceed\n")
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "100"], input="continue\n")
        assert result.exit_code == 0

    def test_non_custom_truthy_aborts(self, cli_runner: CliRunner) -> None:
        """Test that non-custom-truthy values abort."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if(
            "Proceed?",
            lambda x: x > 50,
            truthy=["ok", "proceed"],
        )
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        # Default 'yes' should not work with custom truthy list
        result = cli_runner.invoke(cmd, ["--value", "100"], input="yes\n")
        assert result.exit_code == 1

        # Arbitrary string should abort
        result = cli_runner.invoke(cmd, ["--value", "100"], input="cancel\n")
        assert result.exit_code == 1

    def test_case_insensitive_matching(self, cli_runner: CliRunner) -> None:
        """Test that response matching is case-insensitive."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Proceed?", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="Y\n")
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "100"], input="YES\n")
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "100"], input="Yes\n")
        assert result.exit_code == 0

        # Non-truthy responses should abort (even common negative responses)
        result = cli_runner.invoke(cmd, ["--value", "100"], input="N\n")
        assert result.exit_code == 1

        result = cli_runner.invoke(cmd, ["--value", "100"], input="NO\n")
        assert result.exit_code == 1


class TestConfirmIfTestingMode:
    """Test confirm_if decorator in testing mode."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_testing_mode_auto_confirms(self, cli_runner: CliRunner) -> None:
        """Test that CLICK_EXTENDED_TESTING=1 auto-confirms without prompting."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Proceed?", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        with patch.dict(os.environ, {"CLICK_EXTENDED_TESTING": "1"}):
            result = cli_runner.invoke(cmd, ["--value", "100"])
            assert result.exit_code == 0
            assert "Value: 100" in result.output
            assert "Proceed?" not in result.output

    def test_testing_mode_disabled_prompts_normally(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that without CLICK_EXTENDED_TESTING, prompting works normally."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Proceed?", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        with patch.dict(os.environ, {"CLICK_EXTENDED_TESTING": "0"}):
            result = cli_runner.invoke(cmd, ["--value", "100"], input="y\n")
            assert result.exit_code == 0
            assert "Proceed?" in result.output


class TestConfirmIfValueTypes:
    """Test confirm_if decorator with various value types."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_with_string_value(self, cli_runner: CliRunner) -> None:
        """Test confirm_if with string values."""

        @command()
        @option("path", default="/etc/config")
        @confirm_if("Modify {value}?", lambda x: x.startswith("/etc"))
        def cmd(path: str) -> None:
            click.echo(f"Modified {path}")

        result = cli_runner.invoke(
            cmd, ["--path", "/etc/important"], input="yes\n"
        )
        assert result.exit_code == 0
        assert "Modify /etc/important?" in result.output

    def test_with_integer_value(self, cli_runner: CliRunner) -> None:
        """Test confirm_if with integer values."""

        @command()
        @option("count", type=int, default=1000)
        @confirm_if("Process {value} items?", lambda x: x > 500)
        def cmd(count: int) -> None:
            click.echo(f"Processing {count} items")

        result = cli_runner.invoke(cmd, ["--count", "1000"], input="y\n")
        assert result.exit_code == 0
        assert "Process 1000 items?" in result.output

    def test_with_float_value(self, cli_runner: CliRunner) -> None:
        """Test confirm_if with float values."""

        @command()
        @option("amount", type=float, default=99.99)
        @confirm_if("Charge ${value}?", lambda x: x > 50.0)
        def cmd(amount: float) -> None:
            click.echo(f"Charged ${amount}")

        result = cli_runner.invoke(cmd, ["--amount", "99.99"], input="yes\n")
        assert result.exit_code == 0
        assert "Charge $99.99?" in result.output


class TestConfirmIfPredicateExceptions:
    """Test confirm_if decorator when predicate raises exceptions."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_predicate_exception_propagates(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that exceptions in predicate function are propagated."""

        def bad_predicate(value: Any) -> bool:
            raise RuntimeError("Predicate failed")

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Proceed?", bad_predicate)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"])
        assert result.exit_code != 0
        assert "Predicate failed" in result.output


class TestConfirmIfEdgeCases:
    """Test confirm_if decorator edge cases."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore

    def test_empty_string_value(self, cli_runner: CliRunner) -> None:
        """Test confirm_if with empty string value."""

        @command()
        @option("text", default="")
        @confirm_if("Use empty value?", lambda x: len(x) == 0)
        def cmd(text: str) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", ""], input="y\n")
        assert result.exit_code == 0
        assert "Use empty value?" in result.output

    def test_none_value_handling(self, cli_runner: CliRunner) -> None:
        """Test confirm_if behavior with None values."""

        @command()
        @option("value", default=None)
        @confirm_if("Use None?", lambda x: x is None)
        def cmd(value: Any) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, input="yes\n")
        assert result.exit_code == 0

    def test_whitespace_in_response(self, cli_runner: CliRunner) -> None:
        """Test that whitespace is stripped from responses."""

        @command()
        @option("value", type=int, default=100)
        @confirm_if("Proceed?", lambda x: x > 50)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "100"], input="  yes  \n")
        assert result.exit_code == 0
        assert "Value: 100" in result.output
