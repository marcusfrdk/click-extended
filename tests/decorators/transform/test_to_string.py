"""Tests for to_string decorator."""

from typing import Any
from unittest.mock import Mock

from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.other.context import Context
from click_extended.decorators.transform.to_string import ToString, to_string


class TestToStringUnit:
    """Unit tests for ToString node."""

    def test_to_string_int(self) -> None:
        node = ToString(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_all(42, ctx) == "42"
        assert isinstance(node.handle_all(42, ctx), str)

    def test_to_string_float(self) -> None:
        node = ToString(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_all(3.14, ctx) == "3.14"
        assert isinstance(node.handle_all(3.14, ctx), str)

    def test_to_string_bool(self) -> None:
        node = ToString(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_all(True, ctx) == "True"
        assert node.handle_all(False, ctx) == "False"

    def test_to_string_list(self) -> None:
        node = ToString(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_all([1, 2, 3], ctx) == "[1, 2, 3]"

    def test_to_string_none(self) -> None:
        node = ToString(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_all(None, ctx) == "None"

    def test_to_string_already_str(self) -> None:
        node = ToString(name="test")
        ctx = Mock(spec=Context)
        assert node.handle_all("hello", ctx) == "hello"


class TestToStringCLI:
    """CLI-level tests for to_string decorator."""

    def test_to_string_int_option(self, cli_runner: CliRunner) -> None:
        """Test that to_string converts an int to string in CLI."""

        @command()
        @option("value", type=int, default=None)
        @to_string()
        def cmd(value: Any) -> None:
            assert isinstance(value, str)
            assert value == "42"

        result = cli_runner.invoke(cmd, ["--value", "42"])
        assert result.exit_code == 0

    def test_to_string_string_option(self, cli_runner: CliRunner) -> None:
        """Test that to_string passes through string values unchanged."""

        @command()
        @option("value", default=None)
        @to_string()
        def cmd(value: Any) -> None:
            assert value == "hello"

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
