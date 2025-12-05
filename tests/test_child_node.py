"""Comprehensive tests for ChildNode functionality."""

import asyncio
import ipaddress
import json
import os
import re
import tempfile
from datetime import datetime
from typing import Any, cast
from urllib.parse import urlparse, urlunparse

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.core.decorators.env import env
from click_extended.core.decorators.option import option
from click_extended.core.decorators.tag import tag
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context


class TestSyncHandlerDispatch:
    """Test that sync handlers are correctly dispatched based on value type."""

    def test_handle_string_with_string(self, cli_runner: CliRunner) -> None:
        """Test handle_str receives and processes string values."""

        class StringHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("--text", type=str, default="hello")
        @StringHandler.as_decorator()
        def cmd(text: str) -> None:
            click.echo(text)

        result = cli_runner.invoke(cmd, ["--text", "world"])
        assert result.exit_code == 0
        assert "WORLD" in result.output

    def test_handle_int_with_int(self, cli_runner: CliRunner) -> None:
        """Test handle_int receives and processes int values."""

        class IntHandler(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

        @command()
        @option("--num", type=int, default=5)
        @IntHandler.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "10"])
        assert result.exit_code == 0
        assert "Result: 20" in result.output

    def test_handle_float_with_float(self, cli_runner: CliRunner) -> None:
        """Test handle_float receives and processes float values."""

        class FloatHandler(ChildNode):
            def handle_float(self, value: float, context: Context) -> float:
                return round(value * 1.5, 2)

        @command()
        @option("--price", type=float, default=10.0)
        @FloatHandler.as_decorator()
        def cmd(price: float) -> None:
            click.echo(f"Price: {price}")

        result = cli_runner.invoke(cmd, ["--price", "20.5"])
        assert result.exit_code == 0
        assert "Price: 30.75" in result.output

    def test_handle_bool_with_bool(self, cli_runner: CliRunner) -> None:
        """Test handle_bool receives and processes bool values."""

        class BoolHandler(ChildNode):
            def handle_bool(self, value: bool, context: Context) -> bool:
                return not value

        @command()
        @option("--flag", is_flag=True)
        @BoolHandler.as_decorator()
        def cmd(flag: bool) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd, ["--flag"])
        assert result.exit_code == 0
        assert "Flag: False" in result.output

    def test_handle_string_then_dict_parsing(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str on JSON string - dict parsing happens in command function."""

        class JSONValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                try:
                    json.loads(value)
                    return value
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON: {e}")

        @command()
        @option("--data", type=str, default='{"name": "test"}')
        @JSONValidator.as_decorator()
        def cmd(data: str) -> None:
            data_dict = json.loads(data)
            data_dict = {
                k: v.upper() if isinstance(v, str) else v
                for k, v in data_dict.items()
            }
            click.echo(f"Data: {data_dict}")

        result = cli_runner.invoke(cmd, ["--data", '{"name": "hello"}'])
        assert result.exit_code == 0
        assert "Data: {'name': 'HELLO'}" in result.output

    def test_handle_string_with_path_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str on path string - Path objects are 'flat' types."""

        class PathValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                from pathlib import Path

                p = Path(value)
                if not p.exists():
                    raise ValueError(f"Path does not exist: {value}")
                return str(p.resolve())

        @command()
        @option("--path", type=str, default=".")
        @PathValidator.as_decorator()
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "."])
        assert result.exit_code == 0
        assert "Path:" in result.output

    def test_handle_string_with_date_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test handle_str on date string - datetime objects are 'flat' types."""

        class DateParser(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                try:
                    date_obj = datetime.strptime(value, "%Y-%m-%d")
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError as e:
                    raise ValueError(f"Invalid date format: {e}")

        @command()
        @option("--date", type=str, default="2025-01-01")
        @DateParser.as_decorator()
        def cmd(date: str) -> None:
            click.echo(f"Date: {date}")

        result = cli_runner.invoke(cmd, ["--date", "2025-11-23"])
        assert result.exit_code == 0
        assert "Date: 2025-11-23" in result.output

    def test_handle_tuple_with_mixed_types(self, cli_runner: CliRunner) -> None:
        """Test handle_tuple as fallback for mixed (1, (2, 3)) type tuples."""

        class StringParser(ChildNode):
            """First handler: parse string to tuple."""

            def handle_str(
                self, value: str, context: Context
            ) -> tuple[Any, ...]:
                return cast(tuple[Any, ...], eval(value))

        class MixedTupleHandler(ChildNode):
            """Second handler: transform mixed tuple."""

            def handle_tuple(
                self, value: tuple[Any, ...], context: Context
            ) -> tuple[Any, ...]:
                result: list[tuple[int]] = []
                for item in value:
                    if isinstance(item, tuple):
                        result.append(tuple(x * 2 for x in item))  # type: ignore
                    else:
                        result.append(item * 2)
                return tuple(result)

        @command()
        @option("--data", type=str, default="(1,(2,3))")
        @StringParser.as_decorator()
        @MixedTupleHandler.as_decorator()
        def cmd(data: tuple[Any, ...]) -> None:
            click.echo(f"Data: {data}")

        result = cli_runner.invoke(cmd, ["--data", "(1,(2,3))"])
        assert result.exit_code == 0
        assert "Data: (2, (4, 6))" in result.output

    def test_handle_none_explicitly(self, cli_runner: CliRunner) -> None:
        """Test handle_none is called when value is None."""

        class NoneHandler(ChildNode):
            def handle_none(self, context: Context) -> str:
                return "DEFAULT_VALUE"

        @command()
        @option("--value", type=str, default=None)
        @NoneHandler.as_decorator()
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: DEFAULT_VALUE" in result.output

    def test_handle_none_skips_by_default(self, cli_runner: CliRunner) -> None:
        """Test None passes through when handle_none not implemented."""

        class NoNoneHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("--value", type=str, default=None)
        @NoNoneHandler.as_decorator()
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: None" in result.output

    def test_handle_all_catches_everything(self, cli_runner: CliRunner) -> None:
        """Test handle_all intercepts all value types."""

        class AllHandler(ChildNode):
            def handle_all(self, value: Any, context: Context) -> str:
                return f"PROCESSED_{value}"

        @command()
        @option("--value", type=str, default="test")
        @AllHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: PROCESSED_hello" in result.output


class TestSyncTypeValidation:
    """Test type hint validation for sync handlers."""

    def test_type_hint_validation_matches(self, cli_runner: CliRunner) -> None:
        """Handler with value: int accepts int."""

        class IntOnlyHandler(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

        @command()
        @option("--num", type=int, default=5)
        @IntOnlyHandler.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Num: {num}")

        result = cli_runner.invoke(cmd, ["--num", "10"])
        assert result.exit_code == 0
        assert "Num: 20" in result.output

    def test_type_hint_validation_rejects_mismatch(
        self, cli_runner: CliRunner
    ) -> None:
        """Handler with value: int rejects str - raises UnhandledTypeError."""

        class IntOnlyHandler(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

        @command()
        @option("--value", type=str, default="test")
        @IntOnlyHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 1
        assert "unhandledtypeerror" in result.output.lower()
        assert "does not handle values of type 'str'" in result.output.lower()

    def test_union_type_support(self, cli_runner: CliRunner) -> None:
        """Handler with value: str | int accepts both."""

        class UnionHandler(ChildNode):
            def handle_str(
                self, value: str | int, context: Context
            ) -> str | int:
                if isinstance(value, str):
                    return value.upper()
                return value * 2

        @command()
        @option("--value", type=str, default="test")
        @UnionHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: HELLO" in result.output

    def test_union_type_with_tuples(self, cli_runner: CliRunner) -> None:
        """Handler with value: str | tuple[str, ...] handles both."""

        class FlexibleHandler(ChildNode):
            def handle_str(
                self, value: str | tuple[str, ...], context: Context
            ) -> str:
                if isinstance(value, tuple):
                    return " ".join(value).upper()
                return value.upper()

        @command()
        @option("--value", type=str, default="test")
        @FlexibleHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: HELLO" in result.output

    def test_optional_type_handling(self, cli_runner: CliRunner) -> None:
        """Handler with value: str | None handles None."""

        class OptionalHandler(ChildNode):
            def handle_str(self, value: str | None, context: Context) -> str:
                return value.upper() if value else "EMPTY"

        @command()
        @option("--value", type=str, default=None)
        @OptionalHandler.as_decorator()
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: EMPTY" in result.output


class TestSyncHandlerPriority:
    """Test that handlers are called in correct priority order."""

    def test_handle_none_priority_over_others(
        self, cli_runner: CliRunner
    ) -> None:
        """handle_none called first for None values."""

        class PriorityHandler(ChildNode):
            def handle_none(self, context: Context) -> str:
                return "FROM_NONE"

            def handle_all(self, value: Any, context: Context) -> str:
                return "FROM_ALL"

        @command()
        @option("--value", type=str, default=None)
        @PriorityHandler.as_decorator()
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: FROM_NONE" in result.output

    def test_specific_handler_priority_over_handle_all(
        self, cli_runner: CliRunner
    ) -> None:
        """Specific handlers like handle_str are called before handle_all fallback."""

        class SpecificPriorityHandler(ChildNode):
            def handle_all(self, value: Any, context: Context) -> str:
                return "FROM_ALL"

            def handle_str(self, value: str, context: Context) -> str:
                return "FROM_PRIMITIVE"

        @command()
        @option("--value", type=str, default="test")
        @SpecificPriorityHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: FROM_PRIMITIVE" in result.output

    def test_specific_handler_priority(self, cli_runner: CliRunner) -> None:
        """handle_str chosen over handle_complex for strings."""

        class SpecificHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return "FROM_PRIMITIVE"

            def handle_all(self, value: Any, context: Context) -> str:
                return "FROM_ALL"

        @command()
        @option("--value", type=str, default="test")
        @SpecificHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: FROM_PRIMITIVE" in result.output


class TestSyncErrorHandling:
    """Test error handling in sync child nodes."""

    def test_value_error_wrapped(self, cli_runner: CliRunner) -> None:
        """ValueError from handler wrapped in ProcessError."""

        class ErrorHandler(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value < 0:
                    raise ValueError("Value must be positive")
                return value

        @command()
        @option("--num", type=int, default=5)
        @ErrorHandler.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Num: {num}")

        result = cli_runner.invoke(cmd, ["--num", "-5"])
        assert result.exit_code == 1
        assert "must be positive" in result.output.lower()

    def test_error_includes_context(self, cli_runner: CliRunner) -> None:
        """Error messages include parent/child context."""

        class ContextErrorHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                raise ValueError("Custom error message")

        @command()
        @option("--value", type=str, default="test")
        @ContextErrorHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "test"])
        assert result.exit_code == 1
        assert "custom error message" in result.output.lower()


class TestAsyncHandlerDispatch:
    """Test that async handlers are correctly dispatched based on value type."""

    def test_async_handle_string_string(self, cli_runner: CliRunner) -> None:
        """Test async handle_str receives and processes string values."""

        class AsyncStringHandler(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)  # Simulate async work
                return value.upper()

        @command()
        @option("--text", type=str, default="hello")
        @AsyncStringHandler.as_decorator()
        def cmd(text: str) -> None:
            click.echo(text)

        result = cli_runner.invoke(cmd, ["--text", "async"])
        assert result.exit_code == 0
        assert "ASYNC" in result.output

    def test_async_handle_int_int(self, cli_runner: CliRunner) -> None:
        """Test async handle_int receives and processes int values."""

        class AsyncIntHandler(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 3

        @command()
        @option("--num", type=int, default=5)
        @AsyncIntHandler.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "7"])
        assert result.exit_code == 0
        assert "Result: 21" in result.output

    def test_async_handle_float_float(self, cli_runner: CliRunner) -> None:
        """Test async handle_float receives and processes float values."""

        class AsyncFloatHandler(ChildNode):
            async def handle_float(
                self, value: float, context: Context
            ) -> float:
                await asyncio.sleep(0.001)
                return round(value * 2.5, 2)

        @command()
        @option("--price", type=float, default=10.0)
        @AsyncFloatHandler.as_decorator()
        def cmd(price: float) -> None:
            click.echo(f"Price: {price}")

        result = cli_runner.invoke(cmd, ["--price", "8.4"])
        assert result.exit_code == 0
        assert "Price: 21.0" in result.output

    def test_async_handle_bool_bool(self, cli_runner: CliRunner) -> None:
        """Test async handle_bool receives and processes bool values."""

        class AsyncBoolHandler(ChildNode):
            async def handle_bool(self, value: bool, context: Context) -> bool:
                await asyncio.sleep(0.001)
                return not value

        @command()
        @option("--flag", is_flag=True)
        @AsyncBoolHandler.as_decorator()
        def cmd(flag: bool) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd, ["--flag"])
        assert result.exit_code == 0
        assert "Flag: False" in result.output

    def test_async_handle_string_json_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test async handle_str on JSON string."""

        class AsyncJSONValidator(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                try:
                    json.loads(value)
                    return value
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON: {e}")

        @command()
        @option("--data", type=str, default='{"name": "TEST"}')
        @AsyncJSONValidator.as_decorator()
        def cmd(data: str) -> None:
            data_dict = json.loads(data)
            data_dict = {
                k: v.lower() if isinstance(v, str) else v
                for k, v in data_dict.items()
            }
            click.echo(f"Data: {data_dict}")

        result = cli_runner.invoke(cmd, ["--data", '{"name": "HELLO"}'])
        assert result.exit_code == 0
        assert "Data: {'name': 'hello'}" in result.output

    def test_async_handle_string_path_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test async handle_str on path string."""

        class AsyncPathValidator(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                from pathlib import Path

                p = Path(value)
                if not p.exists():
                    raise ValueError(f"Path does not exist: {value}")
                return str(p.absolute())

        @command()
        @option("--path", type=str, default=".")
        @AsyncPathValidator.as_decorator()
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "."])
        assert result.exit_code == 0
        assert "Path:" in result.output

    def test_async_handle_string_date_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test async handle_str on date string."""

        class AsyncDateParser(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                try:
                    date_obj = datetime.strptime(value, "%Y-%m-%d")
                    return date_obj.strftime("%Y/%m/%d")
                except ValueError as e:
                    raise ValueError(f"Invalid date format: {e}")

        @command()
        @option("--date", type=str, default="2025-01-01")
        @AsyncDateParser.as_decorator()
        def cmd(date: str) -> None:
            click.echo(f"Date: {date}")

        result = cli_runner.invoke(cmd, ["--date", "2025-12-25"])
        assert result.exit_code == 0
        assert "Date: 2025/12/25" in result.output

    def test_async_handle_tuple_with_mixed_types(
        self, cli_runner: CliRunner
    ) -> None:
        """Test async handle_tuple as fallback for mixed (1, (2, 3)) type tuples."""

        class AsyncStringParser(ChildNode):
            """First handler: parse string to tuple."""

            async def handle_str(
                self, value: str, context: Context
            ) -> tuple[Any, ...]:
                await asyncio.sleep(0.001)
                return cast(tuple[Any, ...], eval(value))

        class AsyncMixedTupleHandler(ChildNode):
            """Second handler: transform mixed tuple."""

            async def handle_tuple(
                self, value: tuple[Any, ...], context: Context
            ) -> tuple[Any, ...]:
                await asyncio.sleep(0.001)
                result: list[tuple[int]] = []
                for item in value:
                    if isinstance(item, tuple):
                        result.append(tuple(x * 3 for x in item))  # type: ignore
                    else:
                        result.append(item * 3)
                return tuple(result)

        @command()
        @option("--data", type=str, default="(2,(3,4))")
        @AsyncStringParser.as_decorator()
        @AsyncMixedTupleHandler.as_decorator()
        def cmd(data: tuple[Any, ...]) -> None:
            click.echo(f"Data: {data}")

        result = cli_runner.invoke(cmd, ["--data", "(2,(3,4))"])
        assert result.exit_code == 0
        assert "Data: (6, (9, 12))" in result.output

    def test_async_handle_none(self, cli_runner: CliRunner) -> None:
        """Test async handle_none is called when value is None."""

        class AsyncNoneHandler(ChildNode):
            async def handle_none(self, context: Context) -> str:
                await asyncio.sleep(0.001)
                return "ASYNC_DEFAULT"

        @command()
        @option("--value", type=str, default=None)
        @AsyncNoneHandler.as_decorator()
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: ASYNC_DEFAULT" in result.output

    def test_async_handle_all(self, cli_runner: CliRunner) -> None:
        """Test async handle_all intercepts all value types."""

        class AsyncAllHandler(ChildNode):
            async def handle_all(self, value: Any, context: Context) -> str:
                await asyncio.sleep(0.001)
                return f"ASYNC_{value}"

        @command()
        @option("--value", type=str, default="test")
        @AsyncAllHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: ASYNC_hello" in result.output


class TestAsyncMultipleHandlers:
    """Test chains of async handlers."""

    def test_async_multiple_handlers_in_chain(
        self, cli_runner: CliRunner
    ) -> None:
        """All async handlers in chain."""

        class AsyncValidator(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                if value < 0:
                    raise ValueError("Must be positive")
                return value

        class AsyncTransformer(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 10

        @command()
        @option("--num", type=int, default=5)
        @AsyncValidator.as_decorator()
        @AsyncTransformer.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "7"])
        assert result.exit_code == 0
        assert "Result: 70" in result.output


class TestAsyncTypeValidation:
    """Test type validation for async handlers."""

    def test_async_handler_type_validation(self, cli_runner: CliRunner) -> None:
        """Async handler with type hints validates correctly."""

        class AsyncTypedHandler(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 2

        @command()
        @option("--num", type=int, default=5)
        @AsyncTypedHandler.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Num: {num}")

        result = cli_runner.invoke(cmd, ["--num", "15"])
        assert result.exit_code == 0
        assert "Num: 30" in result.output

    def test_async_handler_union_types(self, cli_runner: CliRunner) -> None:
        """Async handler with union types."""

        class AsyncUnionHandler(ChildNode):
            async def handle_str(
                self, value: str | int, context: Context
            ) -> str:
                await asyncio.sleep(0.001)
                if isinstance(value, int):
                    return f"INT:{value * 2}"
                return f"STR:{value.upper()}"

        @command()
        @option("--value", type=str, default="test")
        @AsyncUnionHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: STR:HELLO" in result.output

    def test_async_handler_optional_types(self, cli_runner: CliRunner) -> None:
        """Async handler with optional types."""

        class AsyncOptionalHandler(ChildNode):
            async def handle_str(
                self, value: str | None, context: Context
            ) -> str:
                await asyncio.sleep(0.001)
                return value.upper() if value else "ASYNC_EMPTY"

        @command()
        @option("--value", type=str, default=None)
        @AsyncOptionalHandler.as_decorator()
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: ASYNC_EMPTY" in result.output


class TestAsyncHandlerPriority:
    """Test async handler priority."""

    def test_async_handle_string_called_before_complex(
        self, cli_runner: CliRunner
    ) -> None:
        """Async handle_str called before handle_complex for primitives."""

        class AsyncPriorityHandler(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                return "FROM_PRIMITIVE"

            async def handle_all(self, value: Any, context: Context) -> str:
                await asyncio.sleep(0.001)
                return "FROM_ALL"

        @command()
        @option("--value", type=str, default="test")
        @AsyncPriorityHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: FROM_PRIMITIVE" in result.output

    def test_async_specific_handler_priority_over_handle_all(
        self, cli_runner: CliRunner
    ) -> None:
        """Async specific handlers like handle_str are called before handle_all fallback."""

        class AsyncSpecificPriorityHandler(ChildNode):
            async def handle_all(self, value: Any, context: Context) -> str:
                await asyncio.sleep(0.001)
                return "FROM_ALL"

            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                return "FROM_PRIMITIVE"

        @command()
        @option("--value", type=str, default="test")
        @AsyncSpecificPriorityHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: FROM_PRIMITIVE" in result.output

    def test_async_handle_none_called_first(
        self, cli_runner: CliRunner
    ) -> None:
        """Async handle_none called first for None values."""

        class AsyncNonePriorityHandler(ChildNode):
            async def handle_none(self, context: Context) -> str:
                await asyncio.sleep(0.001)
                return "FROM_NONE"

            async def handle_all(self, value: Any, context: Context) -> str:
                await asyncio.sleep(0.001)
                return "FROM_ALL"

        @command()
        @option("--value", type=str, default=None)
        @AsyncNonePriorityHandler.as_decorator()
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: FROM_NONE" in result.output


class TestAsyncErrorHandling:
    """Test error handling in async handlers."""

    def test_async_handler_with_validation_error(
        self, cli_runner: CliRunner
    ) -> None:
        """Async handler with validation error."""

        class AsyncValidationHandler(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                if value < 10:
                    raise ValueError("Value must be at least 10")
                return value

        @command()
        @option("--num", type=int, default=15)
        @AsyncValidationHandler.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Num: {num}")

        result = cli_runner.invoke(cmd, ["--num", "5"])
        assert result.exit_code == 1
        assert "must be at least 10" in result.output.lower()

    def test_async_handler_with_transform_error(
        self, cli_runner: CliRunner
    ) -> None:
        """Async handler with transformation error."""

        class AsyncTransformHandler(ChildNode):
            async def handle_str(self, value: str, context: Context) -> int:
                await asyncio.sleep(0.001)
                try:
                    return int(value)
                except ValueError:
                    raise ValueError(f"Cannot convert '{value}' to integer")

        @command()
        @option("--value", type=str, default="123")
        @AsyncTransformHandler.as_decorator()
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "abc"])
        assert result.exit_code == 1
        assert "cannot convert" in result.output.lower()

    def test_async_handler_with_value_error(
        self, cli_runner: CliRunner
    ) -> None:
        """Async handler raises ValueError."""

        class AsyncErrorHandler(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                if "error" in value.lower():
                    raise ValueError("Value contains 'error'")
                return value.upper()

        @command()
        @option("--text", type=str, default="test")
        @AsyncErrorHandler.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "error_value"])
        assert result.exit_code == 1
        assert "contains 'error'" in result.output.lower()


class TestMixedSyncAsync:
    """Test mixing sync and async handlers in chains."""

    def test_mixed_sync_validator_async_transformer(
        self, cli_runner: CliRunner
    ) -> None:
        """Sync validation → async transformation."""

        class SyncValidator(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value <= 0:
                    raise ValueError("Must be positive")
                return value

        class AsyncTransformer(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 100

        @command()
        @option("--num", type=int, default=5)
        @SyncValidator.as_decorator()
        @AsyncTransformer.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "3"])
        assert result.exit_code == 0
        assert "Result: 300" in result.output

    def test_mixed_async_validator_sync_transformer(
        self, cli_runner: CliRunner
    ) -> None:
        """Async validation → sync transformation."""

        class AsyncValidator(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                if len(value) < 3:
                    raise ValueError("Too short")
                return value

        class SyncTransformer(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("--text", type=str, default="test")
        @AsyncValidator.as_decorator()
        @SyncTransformer.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: HELLO" in result.output

    def test_mixed_three_handlers_alternating(
        self, cli_runner: CliRunner
    ) -> None:
        """Sync → async → sync chain."""

        class SyncValidator(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value < 0:
                    raise ValueError("Must be non-negative")
                return value

        class AsyncMultiplier(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 5

        class SyncAdder(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value + 100

        @command()
        @option("--num", type=int, default=10)
        @SyncValidator.as_decorator()
        @AsyncMultiplier.as_decorator()
        @SyncAdder.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "4"])
        assert result.exit_code == 0
        assert "Result: 120" in result.output  # (4 * 5) + 100

    def test_mixed_all_sync_except_one_async(
        self, cli_runner: CliRunner
    ) -> None:
        """Mostly sync with one async in middle."""

        class SyncHandler1(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value + 1

        class AsyncHandler(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 2

        class SyncHandler2(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value + 10

        @command()
        @option("--num", type=int, default=5)
        @SyncHandler1.as_decorator()
        @AsyncHandler.as_decorator()
        @SyncHandler2.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "5"])
        assert result.exit_code == 0
        assert "Result: 22" in result.output  # ((5 + 1) * 2) + 10

    def test_mixed_all_async_except_one_sync(
        self, cli_runner: CliRunner
    ) -> None:
        """Mostly async with one sync in middle."""

        class AsyncHandler1(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 2

        class SyncHandler(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value + 5

        class AsyncHandler2(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 3

        @command()
        @option("--num", type=int, default=2)
        @AsyncHandler1.as_decorator()
        @SyncHandler.as_decorator()
        @AsyncHandler2.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "2"])
        assert result.exit_code == 0
        assert "Result: 27" in result.output  # ((2 * 2) + 5) * 3

    def test_mixed_async_error_in_sync_chain(
        self, cli_runner: CliRunner
    ) -> None:
        """Async handler throws error in sync chain."""

        class SyncHandler1(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value + 1

        class AsyncValidator(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                if value > 10:
                    raise ValueError("Too large")
                return value

        class SyncHandler2(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

        @command()
        @option("--num", type=int, default=5)
        @SyncHandler1.as_decorator()
        @AsyncValidator.as_decorator()
        @SyncHandler2.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "15"])
        assert result.exit_code == 1
        assert "too large" in result.output.lower()

    def test_mixed_sync_error_in_async_chain(
        self, cli_runner: CliRunner
    ) -> None:
        """Sync handler throws error in async chain."""

        class AsyncHandler1(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 2

        class SyncValidator(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value < 5:
                    raise ValueError("Too small")
                return value

        class AsyncHandler2(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value + 10

        @command()
        @option("--num", type=int, default=5)
        @AsyncHandler1.as_decorator()
        @SyncValidator.as_decorator()
        @AsyncHandler2.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "2"])
        assert result.exit_code == 1
        assert "too small" in result.output.lower()


class TestParentNodeIntegration:
    """Test child nodes with different parent types."""

    def test_child_with_option_parent(self, cli_runner: CliRunner) -> None:
        """Child node processes @option value."""

        class UppercaseHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("--name", type=str, default="test")
        @UppercaseHandler.as_decorator()
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "alice"])
        assert result.exit_code == 0
        assert "Name: ALICE" in result.output

    def test_child_with_argument_parent(self, cli_runner: CliRunner) -> None:
        """Child node processes @argument value."""

        class DoubleHandler(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

        @command()
        @argument("count", type=int)
        @DoubleHandler.as_decorator()
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["5"])
        assert result.exit_code == 0
        assert "Count: 10" in result.output

    def test_child_with_env_parent(self, cli_runner: CliRunner) -> None:
        """Child node processes @env value."""

        class PrefixHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return f"PREFIX_{value}"

        @command()
        @env("TEST_VAR", param="test_var")
        @PrefixHandler.as_decorator()
        def cmd(test_var: str | None) -> None:
            click.echo(f"Var: {test_var}")

        result = cli_runner.invoke(cmd, env={"TEST_VAR": "VALUE"})
        assert result.exit_code == 0
        assert "Var: PREFIX_VALUE" in result.output

    def test_multiple_children_chain_sync(self, cli_runner: CliRunner) -> None:
        """Multiple sync child nodes process in sequence."""

        class Validator(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value < 0:
                    raise ValueError("Must be non-negative")
                return value

        class Multiplier(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 10

        class Adder(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value + 5

        @command()
        @option("--num", type=int, default=3)
        @Validator.as_decorator()
        @Multiplier.as_decorator()
        @Adder.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "7"])
        assert result.exit_code == 0
        assert "Result: 75" in result.output  # (7 * 10) + 5

    def test_multiple_children_chain_async(self, cli_runner: CliRunner) -> None:
        """Multiple async child nodes process in sequence."""

        class AsyncValidator(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                if value < 0:
                    raise ValueError("Must be non-negative")
                return value

        class AsyncMultiplier(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 10

        class AsyncAdder(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value + 5

        @command()
        @option("--num", type=int, default=3)
        @AsyncValidator.as_decorator()
        @AsyncMultiplier.as_decorator()
        @AsyncAdder.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "7"])
        assert result.exit_code == 0
        assert "Result: 75" in result.output  # (7 * 10) + 5

    def test_multiple_children_chain_mixed(self, cli_runner: CliRunner) -> None:
        """Multiple mixed sync/async child nodes process in sequence."""

        class SyncValidator(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value < 0:
                    raise ValueError("Must be non-negative")
                return value

        class AsyncMultiplier(ChildNode):
            async def handle_int(self, value: int, context: Context) -> int:
                await asyncio.sleep(0.001)
                return value * 10

        class SyncAdder(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value + 5

        @command()
        @option("--num", type=int, default=3)
        @SyncValidator.as_decorator()
        @AsyncMultiplier.as_decorator()
        @SyncAdder.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "7"])
        assert result.exit_code == 0
        assert "Result: 75" in result.output  # (7 * 10) + 5

    def test_env_with_async_transformer(self, cli_runner: CliRunner) -> None:
        """Env value transformed by async handler."""

        class AsyncEnvHandler(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                return f"TRANSFORMED_{value}"

        @command()
        @env("MY_VAR", param="my_var")
        @AsyncEnvHandler.as_decorator()
        def cmd(my_var: str | None) -> None:
            click.echo(f"Var: {my_var}")

        result = cli_runner.invoke(cmd, env={"MY_VAR": "test"})
        assert result.exit_code == 0
        assert "Var: TRANSFORMED_test" in result.output


class TestTagValidation:
    """Test tag-based validation across multiple parameters."""

    def test_tag_validation_single_parent(self, cli_runner: CliRunner) -> None:
        """@tag with one parent node."""

        class SingleTagValidator(ChildNode):
            def handle_tag(
                self, value: dict[str, Any], context: Context
            ) -> None:
                if "name" in value and value["name"]:
                    if len(value["name"]) < 3:
                        raise ValueError("Name too short")

        @command()
        @option("--name", type=str, default="test", tags="validation")
        @tag("validation")
        @SingleTagValidator.as_decorator()
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "alice"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--name", "ab"])
        assert result.exit_code == 1
        assert "name too short" in result.output.lower()

    def test_tag_validation_multiple_parents(
        self, cli_runner: CliRunner
    ) -> None:
        """@tag validates across multiple parameters."""

        class MultiTagValidator(ChildNode):
            def handle_tag(
                self, value: dict[str, Any], context: Context
            ) -> None:
                username = value.get("username")
                email = value.get("email")

                if username and email:
                    if username.lower() not in email.lower():
                        raise ValueError("Username must be part of email")

        @command()
        @option("--username", type=str, default="user", tags="user_info")
        @option(
            "--email", type=str, default="user@example.com", tags="user_info"
        )
        @tag("user_info")
        @MultiTagValidator.as_decorator()
        def cmd(username: str, email: str) -> None:
            click.echo(f"User: {username}, Email: {email}")

        result = cli_runner.invoke(
            cmd, ["--username", "john", "--email", "john@example.com"]
        )
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cmd, ["--username", "bob", "--email", "alice@example.com"]
        )
        assert result.exit_code == 1
        assert "username must be part of email" in result.output.lower()

    def test_tag_receives_all_parent_values(
        self, cli_runner: CliRunner
    ) -> None:
        """handle_tag gets dict with all tagged params."""

        received_values: dict[str, Any] = {}

        class ValueCapture(ChildNode):
            def handle_tag(
                self, value: dict[str, Any], context: Context
            ) -> None:
                received_values.update(value)

        @command()
        @option("--name", type=str, default="alice", tags="capture")
        @option("--age", type=int, default=30, tags="capture")
        @option("--city", type=str, default="NYC", tags="capture")
        @tag("capture")
        @ValueCapture.as_decorator()
        def cmd(name: str, age: int, city: str) -> None:
            click.echo("OK")

        result = cli_runner.invoke(
            cmd, ["--name", "bob", "--age", "25", "--city", "LA"]
        )
        assert result.exit_code == 0
        assert received_values["name"] == "bob"
        assert received_values["age"] == 25
        assert received_values["city"] == "LA"

    def test_tag_validation_only_no_transform(
        self, cli_runner: CliRunner
    ) -> None:
        """@tag handlers cannot transform values."""

        class InvalidTransformTag(ChildNode):
            def handle_tag(
                self, value: dict[str, Any], context: Context
            ) -> dict[str, Any]:
                return {"transformed": True}

        @command()
        @option("--value", type=str, default="test", tags="transform")
        @tag("transform")
        @InvalidTransformTag.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1

    def test_tag_async_validation_multiple_parents(
        self, cli_runner: CliRunner
    ) -> None:
        """Async @tag validation across multiple parameters."""

        class AsyncMultiTagValidator(ChildNode):
            async def handle_tag(
                self, value: dict[str, Any], context: Context
            ) -> None:
                await asyncio.sleep(0.001)
                min_val = value.get("min_val")
                max_val = value.get("max_val")

                if min_val is not None and max_val is not None:
                    if min_val >= max_val:
                        raise ValueError("Min must be less than max")

        @command()
        @option("--min-val", type=int, default=0, tags="range")
        @option("--max-val", type=int, default=100, tags="range")
        @tag("range")
        @AsyncMultiTagValidator.as_decorator()
        def cmd(min_val: int, max_val: int) -> None:
            click.echo(f"Range: {min_val} to {max_val}")

        result = cli_runner.invoke(cmd, ["--min-val", "10", "--max-val", "20"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--min-val", "50", "--max-val", "30"])
        assert result.exit_code == 1
        assert "min must be less than max" in result.output.lower()


class TestRealWorldValidators:
    """Test real-world validation scenarios."""

    def test_email_validator_sync(self, cli_runner: CliRunner) -> None:
        """Email format validation with regex (sync)."""

        class EmailValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, value):
                    raise ValueError(f"Invalid email format: {value}")
                return value

        @command()
        @option("--email", type=str, default="test@example.com")
        @EmailValidator.as_decorator()
        def cmd(email: str) -> None:
            click.echo(f"Email: {email}")

        result = cli_runner.invoke(cmd, ["--email", "user@domain.com"])
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cmd, ["--email", "test.user+tag@sub.domain.co.uk"]
        )
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--email", "invalid.email"])
        assert result.exit_code == 1
        assert "invalid email format" in result.output.lower()

        result = cli_runner.invoke(cmd, ["--email", "@domain.com"])
        assert result.exit_code == 1

    def test_email_validator_async(self, cli_runner: CliRunner) -> None:
        """Email format validation with regex (async)."""

        class AsyncEmailValidator(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, value):
                    raise ValueError(f"Invalid email format: {value}")
                return value

        @command()
        @option("--email", type=str, default="test@example.com")
        @AsyncEmailValidator.as_decorator()
        def cmd(email: str) -> None:
            click.echo(f"Email: {email}")

        result = cli_runner.invoke(cmd, ["--email", "async@test.com"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--email", "bad@"])
        assert result.exit_code == 1

    def test_url_validator(self, cli_runner: CliRunner) -> None:
        """URL format validation."""

        class URLValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                try:
                    result = urlparse(value)
                    if not all([result.scheme, result.netloc]):
                        raise ValueError(f"Invalid URL: {value}")
                    return value
                except Exception as e:
                    raise ValueError(f"Invalid URL: {value}") from e

        @command()
        @option("--url", type=str, default="https://example.com")
        @URLValidator.as_decorator()
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(
            cmd, ["--url", "https://github.com/user/repo"]
        )
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--url", "http://localhost:8000/path"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--url", "not-a-url"])
        assert result.exit_code == 1

        result = cli_runner.invoke(cmd, ["--url", "ftp://"])
        assert result.exit_code == 1

    def test_phone_number_validator(self, cli_runner: CliRunner) -> None:
        """Phone number format validation."""

        class PhoneValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                cleaned = re.sub(r"[-.\s()]", "", value)
                if not re.match(r"^\+?1?\d{10}$", cleaned):
                    raise ValueError(f"Invalid phone number: {value}")
                return value

        @command()
        @option("--phone", type=str, default="5551234567")
        @PhoneValidator.as_decorator()
        def cmd(phone: str) -> None:
            click.echo(f"Phone: {phone}")

        result = cli_runner.invoke(cmd, ["--phone", "5551234567"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--phone", "(555) 123-4567"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--phone", "+15551234567"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--phone", "123"])
        assert result.exit_code == 1

    def test_positive_integer_validator(self, cli_runner: CliRunner) -> None:
        """Number must be > 0 validation."""

        class PositiveValidator(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value <= 0:
                    raise ValueError(f"Value must be positive, got {value}")
                return value

        @command()
        @option("--count", type=int, default=1)
        @PositiveValidator.as_decorator()
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["--count", "10"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--count", "0"])
        assert result.exit_code == 1

        result = cli_runner.invoke(cmd, ["--count", "-5"])
        assert result.exit_code == 1

    def test_range_validator(self, cli_runner: CliRunner) -> None:
        """Value within range validation using handler kwargs."""

        class RangeValidator(ChildNode):
            def handle_int(
                self,
                value: int,
                context: Context,
                *args: Any,
                min: int = 0,
                max: int = 100,
                **kwargs: Any,
            ) -> int:
                if not (min <= value <= max):
                    raise ValueError(
                        f"Value {value} not in range [{min}, {max}]"
                    )
                return value

        @command()
        @option("--score", type=int, default=50)
        @RangeValidator.as_decorator(min=0, max=100)
        def cmd(score: int) -> None:
            click.echo(f"Score: {score}")

        result = cli_runner.invoke(cmd, ["--score", "75"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--score", "0"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--score", "100"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--score", "101"])
        assert result.exit_code == 1

        result = cli_runner.invoke(cmd, ["--score", "-1"])
        assert result.exit_code == 1

    def test_file_exists_validator_sync(self, cli_runner: CliRunner) -> None:
        """Path must exist validation (sync)."""

        class FileExistsValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                if not os.path.exists(value):
                    raise ValueError(f"File not found: {value}")
                return value

        @command()
        @option("--file", type=str, default="test.txt")
        @FileExistsValidator.as_decorator()
        def cmd(file: str) -> None:
            click.echo(f"File: {file}")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = cli_runner.invoke(cmd, ["--file", tmp_path])
            assert result.exit_code == 0

            result = cli_runner.invoke(cmd, ["--file", "/nonexistent/file.txt"])
            assert result.exit_code == 1
            assert "file not found" in result.output.lower()
        finally:
            os.unlink(tmp_path)

    def test_file_exists_validator_async(self, cli_runner: CliRunner) -> None:
        """Path must exist validation (async)."""

        class AsyncFileExistsValidator(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                if not os.path.exists(value):
                    raise ValueError(f"File not found: {value}")
                return value

        @command()
        @option("--file", type=str, default="test.txt")
        @AsyncFileExistsValidator.as_decorator()
        def cmd(file: str) -> None:
            click.echo(f"File: {file}")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = cli_runner.invoke(cmd, ["--file", tmp_path])
            assert result.exit_code == 0
        finally:
            os.unlink(tmp_path)

    def test_directory_exists_validator(self, cli_runner: CliRunner) -> None:
        """Directory must exist validation."""

        class DirExistsValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                if not os.path.isdir(value):
                    raise ValueError(f"Directory not found: {value}")
                return value

        @command()
        @option("--dir", type=str, default=".")
        @DirExistsValidator.as_decorator()
        def cmd(dir: str) -> None:
            click.echo(f"Dir: {dir}")

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = cli_runner.invoke(cmd, ["--dir", tmp_dir])
            assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--dir", "/nonexistent/directory"])
        assert result.exit_code == 1

    def test_file_extension_validator(self, cli_runner: CliRunner) -> None:
        """File has correct extension validation using handler kwargs."""

        class ExtensionValidator(ChildNode):
            def handle_str(
                self,
                value: str,
                context: Context,
                *args: Any,
                extensions: list[str] | None = None,
                **kwargs: Any,
            ) -> str:
                if extensions is None:
                    extensions = []
                if not any(value.endswith(ext) for ext in extensions):
                    raise ValueError(
                        f"File must have one of these extensions: {', '.join(extensions)}"
                    )
                return value

        @command()
        @option("--file", type=str, default="test.txt")
        @ExtensionValidator.as_decorator(extensions=[".txt", ".md", ".rst"])
        def cmd(file: str) -> None:
            click.echo(f"File: {file}")

        result = cli_runner.invoke(cmd, ["--file", "document.txt"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--file", "README.md"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--file", "script.py"])
        assert result.exit_code == 1
        assert "must have one of these extensions" in result.output.lower()


class TestRealWorldTransformers:
    """Test real-world transformation scenarios."""

    def test_json_string_parser_sync(self, cli_runner: CliRunner) -> None:
        """Parse JSON string to dict (sync)."""

        class JSONParser(ChildNode):
            def handle_str(
                self, value: str, context: Context
            ) -> dict[str, Any]:
                try:
                    return cast(dict[str, Any], json.loads(value))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON: {e}")

        @command()
        @option("--data", type=str, default='{"key": "value"}')
        @JSONParser.as_decorator()
        def cmd(data: dict[str, Any]) -> None:
            click.echo(f"Parsed: {data}")

        result = cli_runner.invoke(
            cmd, ["--data", '{"name": "test", "count": 42}']
        )
        assert result.exit_code == 0
        assert "Parsed: {'name': 'test', 'count': 42}" in result.output

        result = cli_runner.invoke(cmd, ["--data", "not json"])
        assert result.exit_code == 1
        assert "invalid json" in result.output.lower()

    def test_json_string_parser_async(self, cli_runner: CliRunner) -> None:
        """Parse JSON string to dict (async)."""

        class AsyncJSONParser(ChildNode):
            async def handle_str(
                self, value: str, context: Context
            ) -> dict[str, Any]:
                await asyncio.sleep(0.001)
                try:
                    return cast(dict[str, Any], json.loads(value))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON: {e}")

        @command()
        @option("--data", type=str, default='{"key": "value"}')
        @AsyncJSONParser.as_decorator()
        def cmd(data: dict[str, Any]) -> None:
            click.echo(f"Parsed: {data}")

        result = cli_runner.invoke(cmd, ["--data", '{"async": true}'])
        assert result.exit_code == 0

    def test_csv_string_parser(self, cli_runner: CliRunner) -> None:
        """Parse CSV string to list."""

        class CSVParser(ChildNode):
            def handle_str(self, value: str, context: Context) -> list[str]:
                return [item.strip() for item in value.split(",")]

        @command()
        @option("--items", type=str, default="a,b,c")
        @CSVParser.as_decorator()
        def cmd(items: list[str]) -> None:
            click.echo(f"Items: {items}")

        result = cli_runner.invoke(cmd, ["--items", "apple,banana,cherry"])
        assert result.exit_code == 0
        assert "Items: ['apple', 'banana', 'cherry']" in result.output

    def test_uppercase_transformer(self, cli_runner: CliRunner) -> None:
        """String to uppercase transformation."""

        class UppercaseTransformer(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("--text", type=str, default="hello")
        @UppercaseTransformer.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0
        assert "Text: HELLO WORLD" in result.output

    def test_lowercase_transformer(self, cli_runner: CliRunner) -> None:
        """String to lowercase transformation."""

        class LowercaseTransformer(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.lower()

        @command()
        @option("--text", type=str, default="TEST")
        @LowercaseTransformer.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "HELLO WORLD"])
        assert result.exit_code == 0
        assert "Text: hello world" in result.output

    def test_strip_whitespace_transformer(self, cli_runner: CliRunner) -> None:
        """Remove leading/trailing spaces transformation."""

        class StripTransformer(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.strip()

        @command()
        @option("--text", type=str, default="  test  ")
        @StripTransformer.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: [{text}]")

        result = cli_runner.invoke(cmd, ["--text", "  hello world  "])
        assert result.exit_code == 0
        assert "Text: [hello world]" in result.output

    def test_slug_transformer(self, cli_runner: CliRunner) -> None:
        """Convert to URL slug transformation."""

        class SlugTransformer(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                value = value.lower().strip()
                value = re.sub(r"[^\w\s-]", "", value)
                value = re.sub(r"[-\s]+", "-", value)
                return value

        @command()
        @option("--title", type=str, default="Hello World")
        @SlugTransformer.as_decorator()
        def cmd(title: str) -> None:
            click.echo(f"Slug: {title}")

        result = cli_runner.invoke(
            cmd, ["--title", "Hello World! This is a Test."]
        )
        assert result.exit_code == 0
        assert "Slug: hello-world-this-is-a-test" in result.output

    def test_date_parser_transformer_sync(self, cli_runner: CliRunner) -> None:
        """Parse date string to datetime (sync)."""

        class DateParser(ChildNode):
            def handle_str(self, value: str, context: Context) -> datetime:
                try:
                    return datetime.strptime(value, "%Y-%m-%d")
                except ValueError as e:
                    raise ValueError(f"Invalid date format: {e}")

        @command()
        @option("--date", type=str, default="2025-01-01")
        @DateParser.as_decorator()
        def cmd(date: datetime) -> None:
            click.echo(f"Date: {date.strftime('%B %d, %Y')}")

        result = cli_runner.invoke(cmd, ["--date", "2025-11-23"])
        assert result.exit_code == 0
        assert "Date: November 23, 2025" in result.output

    def test_date_parser_transformer_async(self, cli_runner: CliRunner) -> None:
        """Parse date string to datetime (async)."""

        class AsyncDateParser(ChildNode):
            async def handle_str(
                self, value: str, context: Context
            ) -> datetime:
                await asyncio.sleep(0.001)
                try:
                    return datetime.strptime(value, "%Y-%m-%d")
                except ValueError as e:
                    raise ValueError(f"Invalid date format: {e}")

        @command()
        @option("--date", type=str, default="2025-01-01")
        @AsyncDateParser.as_decorator()
        def cmd(date: datetime) -> None:
            click.echo(f"Date: {date.year}")

        result = cli_runner.invoke(cmd, ["--date", "2025-12-25"])
        assert result.exit_code == 0
        assert "Date: 2025" in result.output

    def test_currency_parser(self, cli_runner: CliRunner) -> None:
        """Parse '$1,234.56' to float."""

        class CurrencyParser(ChildNode):
            def handle_str(self, value: str, context: Context) -> float:
                cleaned = re.sub(r"[$,]", "", value)
                try:
                    return float(cleaned)
                except ValueError:
                    raise ValueError(f"Invalid currency format: {value}")

        @command()
        @option("--price", type=str, default="$100.00")
        @CurrencyParser.as_decorator()
        def cmd(price: float) -> None:
            click.echo(f"Price: {price}")

        result = cli_runner.invoke(cmd, ["--price", "$1,234.56"])
        assert result.exit_code == 0
        assert "Price: 1234.56" in result.output


class TestRealWorldChained:
    """Test chained validation and transformation."""

    def test_chained_email_validation_and_lowercase(
        self, cli_runner: CliRunner
    ) -> None:
        """Validate email then lowercase (mixed sync/async)."""

        class EmailValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, value):
                    raise ValueError(f"Invalid email: {value}")
                return value

        class AsyncLowercase(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                await asyncio.sleep(0.001)
                return value.lower()

        @command()
        @option("--email", type=str, default="Test@Example.COM")
        @EmailValidator.as_decorator()
        @AsyncLowercase.as_decorator()
        def cmd(email: str) -> None:
            click.echo(f"Email: {email}")

        result = cli_runner.invoke(cmd, ["--email", "User@Domain.COM"])
        assert result.exit_code == 0
        assert "Email: user@domain.com" in result.output

    def test_chained_url_validation_and_normalization(
        self, cli_runner: CliRunner
    ) -> None:
        """Validate URL then normalize."""

        class URLValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                result = urlparse(value)
                if not all([result.scheme, result.netloc]):
                    raise ValueError(f"Invalid URL: {value}")
                return value

        class URLNormalizer(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                parsed = urlparse(value)
                path = parsed.path.rstrip("/")
                return urlunparse(
                    (
                        parsed.scheme,
                        parsed.netloc.lower(),
                        path,
                        parsed.params,
                        parsed.query,
                        "",  # Remove fragment
                    )
                )

        @command()
        @option("--url", type=str, default="https://Example.com/")
        @URLValidator.as_decorator()
        @URLNormalizer.as_decorator()
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(
            cmd, ["--url", "HTTPS://Example.COM/Path/#fragment"]
        )
        assert result.exit_code == 0
        assert "URL: https://example.com/Path" in result.output

    def test_conditional_validator_based_on_context(
        self, cli_runner: CliRunner
    ) -> None:
        """Validation depends on context data."""

        class ConditionalValidator(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                strict_mode = context.data.get("strict", False)
                if strict_mode and value < 10:
                    raise ValueError("Value must be >= 10 in strict mode")
                elif not strict_mode and value < 0:
                    raise ValueError("Value must be non-negative")
                return value

        @command()
        @option("--value", type=int, default=5)
        @ConditionalValidator.as_decorator()
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "5"])
        assert result.exit_code == 0

    def test_password_strength_validator_complex(
        self, cli_runner: CliRunner
    ) -> None:
        """Complex multi-rule validation."""

        class PasswordValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                errors: list[str] = []

                if len(value) < 8:
                    errors.append("at least 8 characters")
                if not re.search(r"[A-Z]", value):
                    errors.append("one uppercase letter")
                if not re.search(r"[a-z]", value):
                    errors.append("one lowercase letter")
                if not re.search(r"\d", value):
                    errors.append("one digit")
                if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
                    errors.append("one special character")

                if errors:
                    raise ValueError(
                        f"Password must contain: {', '.join(errors)}"
                    )
                return value

        @command()
        @option("--password", type=str, default="Test123!")
        @PasswordValidator.as_decorator()
        def cmd(password: str) -> None:
            click.echo("Password accepted")

        result = cli_runner.invoke(cmd, ["--password", "SecurePass123!"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--password", "Short1!"])
        assert result.exit_code == 1
        assert "at least 8 characters" in result.output.lower()

        result = cli_runner.invoke(cmd, ["--password", "password123!"])
        assert result.exit_code == 1

    def test_ip_address_validator(self, cli_runner: CliRunner) -> None:
        """IPv4/IPv6 validation."""

        class IPValidator(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                try:
                    ipaddress.ip_address(value)
                    return value
                except ValueError:
                    raise ValueError(f"Invalid IP address: {value}")

        @command()
        @option("--ip", type=str, default="127.0.0.1")
        @IPValidator.as_decorator()
        def cmd(ip: str) -> None:
            click.echo(f"IP: {ip}")

        result = cli_runner.invoke(cmd, ["--ip", "192.168.1.1"])
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cmd, ["--ip", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"]
        )
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--ip", "256.1.1.1"])
        assert result.exit_code == 1


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_string_handling(self, cli_runner: CliRunner) -> None:
        """Empty string '' passes through correctly."""

        class EmptyHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                if value == "":
                    return "EMPTY"
                return value.upper()

        @command()
        @option("--text", type=str, default="")
        @EmptyHandler.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0
        assert "Text: EMPTY" in result.output

    def test_zero_value_handling(self, cli_runner: CliRunner) -> None:
        """Zero (0, 0.0) handled correctly."""

        class ZeroHandler(ChildNode):
            def handle_int(self, value: int | float, context: Context) -> str:
                if value == 0:
                    return "ZERO"
                return f"NOT_ZERO:{value}"

        @command()
        @option("--num", type=int, default=0)
        @ZeroHandler.as_decorator()
        def cmd(num: str) -> None:
            click.echo(f"Num: {num}")

        result = cli_runner.invoke(cmd, ["--num", "0"])
        assert result.exit_code == 0
        assert "Num: ZERO" in result.output

    def test_none_with_optional_type_hint(self, cli_runner: CliRunner) -> None:
        """None value with Optional type hint."""

        class OptionalNoneHandler(ChildNode):
            def handle_none(self, context: Context) -> str:
                return "GOT_NONE"

            def handle_str(self, value: str | None, context: Context) -> str:
                return value.upper() if value else "DEFAULT"

        @command()
        @option("--value", type=str, default=None)
        @OptionalNoneHandler.as_decorator()
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: GOT_NONE" in result.output

    def test_default_value_skipped_when_not_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Child processing based on was_provided."""

        processed: list[str] = []

        class TrackingHandler(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                processed.append(value)
                return value.upper()

        @command()
        @option("--text", type=str, default="default")
        @TrackingHandler.as_decorator()
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        processed.clear()
        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert len(processed) > 0
        assert "Text: HELLO" in result.output

        processed.clear()
        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0


class TestChildNodeStructure:
    """Test ChildNode's structural properties."""

    def test_child_node_has_no_children(self) -> None:
        """Test that ChildNode.get() always returns None."""

        class TestChild(ChildNode):
            pass

        child = TestChild(name="test")
        assert child.get("any_key") is None  # type: ignore[func-returns-value]

    def test_child_node_getitem_raises_key_error(self) -> None:
        """Test that accessing children via __getitem__ raises KeyError."""

        class TestChild(ChildNode):
            pass

        child = TestChild(name="test")

        with pytest.raises(
            KeyError, match="A ChildNode instance has no children"
        ):
            _ = child["some_key"]

    def test_child_node_getitem_with_int_raises_key_error(self) -> None:
        """Test that accessing children with int key raises KeyError."""

        class TestChild(ChildNode):
            pass

        child = TestChild(name="test")

        with pytest.raises(
            KeyError, match="A ChildNode instance has no children"
        ):
            _ = child[0]
