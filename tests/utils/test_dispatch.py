"""Tests for dispatch utilities."""

import asyncio
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import Mock
from uuid import UUID

import pytest

from click_extended.core.child_node import ChildNode
from click_extended.errors import (
    InvalidHandlerError,
    ProcessError,
    UnhandledTypeError,
)
from click_extended.utils.dispatch import (
    _classify_tuple,
    _determine_handler,
    _extract_inner_types,
    _get_implemented_handlers,
    _is_handler_implemented,
    _should_call_handler,
    _validate_handler_type,
    dispatch_to_child,
    dispatch_to_child_async,
    has_async_handlers,
)


class TestClassifyTuple:
    """Test _classify_tuple function."""

    def test_empty_tuple(self) -> None:
        """Test classifying empty tuple returns flat."""
        assert _classify_tuple(()) == "flat"

    def test_flat_tuple_primitives(self) -> None:
        """Test flat tuple with only primitives."""
        assert _classify_tuple((1, 2, "three", 4.5, True)) == "flat"

    def test_flat_tuple_simple_types(self) -> None:
        """Test flat tuple with simple non-primitive types."""
        assert (
            _classify_tuple(
                (Path("/tmp"), UUID("12345678-1234-5678-1234-567812345678"))
            )
            == "flat"
        )
        assert _classify_tuple((datetime.now(), Decimal("10.5"))) == "flat"

    def test_nested_tuple(self) -> None:
        """Test nested tuple with all iterables."""
        assert _classify_tuple(((1, 2), (3, 4), [5, 6])) == "nested"
        assert _classify_tuple(([1], {"a": 1})) == "nested"

    def test_mixed_tuple(self) -> None:
        """Test mixed tuple with both simple and iterable types."""
        assert _classify_tuple((1, (2, 3), "four")) == "mixed"
        assert _classify_tuple(("str", [1, 2], Path("/tmp"))) == "mixed"

    def test_tuple_with_non_categorized_object(self) -> None:
        """Test tuple with objects that aren't simple or iterable."""
        # Objects that aren't in SIMPLE_TYPES or ITERABLE_TYPES are treated as simple
        assert _classify_tuple((object(), object())) == "flat"


class TestExtractInnerTypes:
    """Test _extract_inner_types function."""

    def test_simple_type(self) -> None:
        """Test extracting from simple type."""
        assert _extract_inner_types(int) == {int}
        assert _extract_inner_types(str) == {str}

    def test_union_types(self) -> None:
        """Test extracting from Union types."""
        assert _extract_inner_types(int | str) == {int, str}
        assert _extract_inner_types(int | str | float) == {int, str, float}

    def test_union_with_none(self) -> None:
        """Test Union with None is filtered out."""
        assert _extract_inner_types(int | None) == {int}
        assert _extract_inner_types(str | int | None) == {str, int}

    def test_tuple_hint(self) -> None:
        """Test extracting from tuple[T, ...] hint."""
        # tuple[int, ...]
        hint = tuple[int, ...]
        assert _extract_inner_types(hint) == {int}

    def test_tuple_multiple_types(self) -> None:
        """Test extracting from tuple with multiple specific types."""
        # tuple[int, str, float] (not variadic)
        hint = tuple[int, str, float]
        assert _extract_inner_types(hint) == {int, str, float}

    def test_list_hint(self) -> None:
        """Test extracting from list[T] hint."""
        assert _extract_inner_types(list[str]) == {str}
        assert _extract_inner_types(list[int]) == {int}

    def test_set_hint(self) -> None:
        """Test extracting from set[T] hint."""
        assert _extract_inner_types(set[str]) == {str}

    def test_frozenset_hint(self) -> None:
        """Test extracting from frozenset[T] hint."""
        assert _extract_inner_types(frozenset[int]) == {int}

    def test_dict_hint(self) -> None:
        """Test extracting from dict[K, V] hint."""
        # Should extract value type (V)
        assert _extract_inner_types(dict[str, int]) == {int}

    def test_nested_tuple_hint(self) -> None:
        """Test extracting from nested tuple hint."""
        # tuple[tuple[int, ...], ...]
        inner = tuple[int, ...]
        outer = tuple[inner, ...]
        assert _extract_inner_types(outer) == {int}


class TestValidateHandlerType:
    """Test _validate_handler_type function."""

    def test_any_type_always_valid(self) -> None:
        """Test that Any type always validates."""
        from typing import Any

        is_valid, msg = _validate_handler_type("handle_all", 123, Any)
        assert is_valid
        assert msg == ""

    def test_handle_primitive_with_correct_type(self) -> None:
        """Test handle_primitive with correct primitive type."""
        is_valid, msg = _validate_handler_type("handle_primitive", 42, int)
        assert is_valid
        assert msg == ""

    def test_handle_primitive_with_wrong_type(self) -> None:
        """Test handle_primitive with wrong type."""
        is_valid, msg = _validate_handler_type("handle_primitive", "hello", int)
        assert not is_valid
        assert "Expected int, got str" in msg

    def test_handle_primitive_string_to_int_suggestion(self) -> None:
        """Test suggestion when string is provided but int expected."""
        is_valid, msg = _validate_handler_type("handle_primitive", "123", int)
        assert not is_valid
        assert "type=int" in msg

    def test_handle_primitive_int_to_string_suggestion(self) -> None:
        """Test suggestion when int is provided but str expected."""
        is_valid, msg = _validate_handler_type("handle_primitive", 123, str)
        assert not is_valid
        assert "type=str" in msg

    def test_handle_flat_tuple_not_tuple(self) -> None:
        """Test handle_flat_tuple with non-tuple value."""
        is_valid, msg = _validate_handler_type(
            "handle_flat_tuple", [1, 2], tuple[int, ...]
        )
        assert not is_valid
        assert "Expected tuple, got list" in msg

    def test_handle_flat_tuple_nested_error(self) -> None:
        """Test handle_flat_tuple with nested tuple."""
        is_valid, msg = _validate_handler_type(
            "handle_flat_tuple", ((1, 2), (3, 4)), tuple[int, ...]
        )
        assert not is_valid
        assert "nested tuple" in msg
        assert "handle_nested_tuple" in msg

    def test_handle_flat_tuple_mixed_error(self) -> None:
        """Test handle_flat_tuple with mixed tuple."""
        is_valid, msg = _validate_handler_type(
            "handle_flat_tuple", (1, (2, 3)), tuple[int, ...]
        )
        assert not is_valid
        assert "mixed tuple" in msg

    def test_handle_flat_tuple_wrong_inner_type(self) -> None:
        """Test handle_flat_tuple with wrong inner types."""
        is_valid, msg = _validate_handler_type(
            "handle_flat_tuple", ("a", "b", "c"), tuple[int, ...]
        )
        assert not is_valid
        assert "Expected tuple[int, ...]" in msg
        assert "type=int" in msg

    def test_handle_nested_tuple_flat_error(self) -> None:
        """Test handle_nested_tuple with flat tuple."""
        is_valid, msg = _validate_handler_type(
            "handle_nested_tuple", (1, 2, 3), tuple[tuple[int, ...], ...]
        )
        assert not is_valid
        assert "flat tuple" in msg
        assert "handle_flat_tuple" in msg

    def test_handle_nested_tuple_mixed_error(self) -> None:
        """Test handle_nested_tuple with mixed tuple."""
        is_valid, msg = _validate_handler_type(
            "handle_nested_tuple", ((1, 2), 3), tuple[tuple[int, ...], ...]
        )
        assert not is_valid
        assert "mixed tuple" in msg

    def test_handle_tuple_accepts_any_tuple(self) -> None:
        """Test handle_tuple accepts any tuple."""
        is_valid, msg = _validate_handler_type(
            "handle_tuple", (1, "a", [2]), tuple
        )
        assert is_valid
        assert msg == ""

    def test_handle_list_not_list(self) -> None:
        """Test handle_list with non-list value."""
        is_valid, msg = _validate_handler_type("handle_list", (1, 2), list[int])
        assert not is_valid
        assert "Expected list, got tuple" in msg

    def test_handle_list_wrong_inner_type(self) -> None:
        """Test handle_list with wrong inner types."""
        is_valid, msg = _validate_handler_type(
            "handle_list", ["a", "b"], list[int]
        )
        assert not is_valid
        assert "Expected list[int]" in msg

    def test_handle_dict_not_dict(self) -> None:
        """Test handle_dict with non-dict value."""
        is_valid, msg = _validate_handler_type("handle_dict", [1, 2], dict)
        assert not is_valid
        assert "Expected dict, got list" in msg


class MockChildNode(ChildNode):
    """Mock child node for testing."""

    def __init__(self, name: str = "test_child") -> None:
        """Initialize mock child node."""
        self.name = name
        self.process_args: tuple[Any, ...] = ()
        self.process_kwargs: dict[str, Any] = {}


class TestIsHandlerImplemented:
    """Test _is_handler_implemented function."""

    def test_not_implemented_returns_false(self) -> None:
        """Test that base ChildNode handlers return False."""
        child = MockChildNode()
        assert not _is_handler_implemented(child, "handle_primitive")

    def test_implemented_handler_returns_true(self) -> None:
        """Test that implemented handler returns True."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        assert _is_handler_implemented(child, "handle_primitive")

    def test_nonexistent_handler_returns_false(self) -> None:
        """Test that non-existent handler returns False."""
        child = MockChildNode()
        assert not _is_handler_implemented(child, "handle_nonexistent")


class TestGetImplementedHandlers:
    """Test _get_implemented_handlers function."""

    def test_no_handlers_implemented(self) -> None:
        """Test child with no handlers implemented."""
        child = MockChildNode()
        handlers = _get_implemented_handlers(child)
        assert handlers == []

    def test_single_handler_implemented(self) -> None:
        """Test child with one handler implemented."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        handlers = _get_implemented_handlers(child)
        assert "primitive" in handlers

    def test_multiple_handlers_implemented(self) -> None:
        """Test child with multiple handlers implemented."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

            def handle_list(self, value: list[int], context: Any) -> list[int]:
                return [x * 2 for x in value]

        child = CustomChild()
        handlers = _get_implemented_handlers(child)
        assert "primitive" in handlers
        assert "list" in handlers


class TestShouldCallHandler:
    """Test _should_call_handler function."""

    def test_non_none_value_always_true(self) -> None:
        """Test that non-None values always return True."""
        child = MockChildNode()
        assert _should_call_handler(child, "handle_all", 42)
        assert _should_call_handler(child, "handle_all", "string")

    def test_none_value_with_optional_type(self) -> None:
        """Test None value with Optional type hint."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int | None, context: Any) -> int:
                return value or 0

        child = CustomChild()
        assert _should_call_handler(child, "handle_primitive", None)

    def test_none_value_without_optional_type(self) -> None:
        """Test None value without Optional in type hint."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        assert not _should_call_handler(child, "handle_primitive", None)


class TestDetermineHandler:
    """Test _determine_handler function."""

    def test_tag_context_returns_handle_tag(self) -> None:
        """Test that tag context returns handle_tag."""

        class CustomChild(MockChildNode):
            def handle_tag(self, value: Any, context: Any) -> None:
                pass

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = True

        handler = _determine_handler(child, "value", context)
        assert handler == "handle_tag"

    def test_bytes_returns_handle_bytes(self) -> None:
        """Test that bytes value returns handle_bytes."""

        class CustomChild(MockChildNode):
            def handle_bytes(self, value: bytes, context: Any) -> bytes:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, b"hello", context)
        assert handler == "handle_bytes"

    def test_decimal_returns_handle_decimal(self) -> None:
        """Test that Decimal value returns handle_decimal."""

        class CustomChild(MockChildNode):
            def handle_decimal(self, value: Decimal, context: Any) -> Decimal:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, Decimal("10.5"), context)
        assert handler == "handle_decimal"

    def test_datetime_returns_handle_datetime(self) -> None:
        """Test that datetime/date/time returns handle_datetime."""

        class CustomChild(MockChildNode):
            def handle_datetime(
                self, value: datetime, context: Any
            ) -> datetime:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, datetime.now(), context)
        assert handler == "handle_datetime"

        handler = _determine_handler(child, date.today(), context)
        assert handler == "handle_datetime"

    def test_uuid_returns_handle_uuid(self) -> None:
        """Test that UUID returns handle_uuid."""

        class CustomChild(MockChildNode):
            def handle_uuid(self, value: UUID, context: Any) -> UUID:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(
            child, UUID("12345678-1234-5678-1234-567812345678"), context
        )
        assert handler == "handle_uuid"

    def test_path_returns_handle_path(self) -> None:
        """Test that Path returns handle_path."""

        class CustomChild(MockChildNode):
            def handle_path(self, value: Path, context: Any) -> Path:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, Path("/tmp"), context)
        assert handler == "handle_path"

    def test_dict_returns_handle_dict(self) -> None:
        """Test that dict returns handle_dict."""

        class CustomChild(MockChildNode):
            def handle_dict(
                self, value: dict[str, Any], context: Any
            ) -> dict[str, Any]:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, {"key": "value"}, context)
        assert handler == "handle_dict"

    def test_primitive_returns_handle_primitive(self) -> None:
        """Test that primitives return handle_primitive."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, 42, context)
        assert handler == "handle_primitive"

    def test_flat_tuple_returns_handle_flat_tuple(self) -> None:
        """Test that flat tuple returns handle_flat_tuple."""

        class CustomChild(MockChildNode):
            def handle_flat_tuple(
                self, value: tuple[int, ...], context: Any
            ) -> tuple[int, ...]:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, (1, 2, 3), context)
        assert handler == "handle_flat_tuple"

    def test_nested_tuple_returns_handle_nested_tuple(self) -> None:
        """Test that nested tuple returns handle_nested_tuple."""

        class CustomChild(MockChildNode):
            def handle_nested_tuple(
                self, value: tuple[tuple[int, ...], ...], context: Any
            ) -> Any:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, ((1, 2), (3, 4)), context)
        assert handler == "handle_nested_tuple"

    def test_mixed_tuple_falls_back_to_handle_tuple(self) -> None:
        """Test that mixed tuple uses handle_tuple if available."""

        class CustomChild(MockChildNode):
            def handle_tuple(
                self, value: tuple[Any, ...], context: Any
            ) -> tuple[Any, ...]:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, (1, (2, 3)), context)
        assert handler == "handle_tuple"

    def test_fallback_to_handle_all(self) -> None:
        """Test fallback to handle_all when no specific handler."""

        class CustomChild(MockChildNode):
            def handle_all(self, value: Any, context: Any) -> Any:
                return value

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False

        handler = _determine_handler(child, object(), context)
        assert handler == "handle_all"


class TestHasAsyncHandlers:
    """Test has_async_handlers function."""

    def test_no_async_handlers(self) -> None:
        """Test child with no async handlers."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        assert not has_async_handlers(child)

    def test_with_async_handler(self) -> None:
        """Test child with async handler."""

        class CustomChild(MockChildNode):
            async def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        assert has_async_handlers(child)

    def test_mixed_sync_and_async(self) -> None:
        """Test child with both sync and async handlers."""

        class CustomChild(MockChildNode):
            def handle_list(self, value: list[int], context: Any) -> list[int]:
                return value

            async def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        assert has_async_handlers(child)


class TestDispatchToChild:
    """Test dispatch_to_child function."""

    def test_dispatch_none_with_handle_none(self) -> None:
        """Test dispatching None with handle_none implemented."""

        class CustomChild(MockChildNode):
            def handle_none(self, context: Any) -> int:
                return 0

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {}

        result = dispatch_to_child(child, None, context)
        assert result == 0

    def test_dispatch_none_returns_none(self) -> None:
        """Test dispatching None returns None when no handler."""
        child = MockChildNode()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {}

        result = dispatch_to_child(child, None, context)
        assert result is None

    def test_dispatch_primitive(self) -> None:
        """Test dispatching primitive value."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = dispatch_to_child(child, 21, context)
        assert result == 42

    def test_dispatch_with_handle_all(self) -> None:
        """Test dispatching with handle_all fallback."""

        class CustomChild(MockChildNode):
            def handle_all(self, value: Any, context: Any) -> str:
                return f"processed: {value}"

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = dispatch_to_child(child, "test", context)
        assert result == "processed: test"

    def test_dispatch_raises_unhandled_type_error(self) -> None:
        """Test dispatch raises UnhandledTypeError when no handler."""
        child = MockChildNode()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {}

        with pytest.raises(UnhandledTypeError) as exc_info:
            dispatch_to_child(child, 42, context)

        assert "test_child" in str(exc_info.value)

    def test_dispatch_handler_returns_none_preserves_value(self) -> None:
        """Test that handler returning None preserves original value."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> None:
                # Return None to preserve original value
                return None

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = dispatch_to_child(child, 42, context)
        assert result == 42

    def test_dispatch_handle_none_returns_none_preserves_none(self) -> None:
        """Test handle_none returning None preserves None value."""

        class CustomChild(MockChildNode):
            def handle_none(self, context: Any) -> None:
                # Validation only, return None
                return None

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {}

        result = dispatch_to_child(child, None, context)
        assert result is None

    def test_dispatch_not_implemented_error_fallback(self) -> None:
        """Test that NotImplementedError causes fallback to next handler."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                raise NotImplementedError()

            def handle_all(self, value: Any, context: Any) -> str:
                return "handled by handle_all"

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = dispatch_to_child(child, 42, context)
        assert result == "handled by handle_all"

    def test_dispatch_handle_tag_validation_only(self) -> None:
        """Test handle_tag must not return values."""

        class CustomChild(MockChildNode):
            def handle_tag(self, value: Any, context: Any) -> Any:
                return "modified"  # This should raise error

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = True
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        with pytest.raises(InvalidHandlerError) as exc_info:
            dispatch_to_child(child, {"key": "value"}, context)

        assert "validation-only" in str(exc_info.value)

    def test_dispatch_type_mismatch_raises_process_error(self) -> None:
        """Test type mismatch raises ProcessError."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        with pytest.raises(ProcessError) as exc_info:
            dispatch_to_child(child, "not_an_int", context)

        assert "Type mismatch" in str(exc_info.value)


class TestDispatchToChildAsync:
    """Test dispatch_to_child_async function."""

    @pytest.mark.asyncio
    async def test_async_dispatch_none_with_async_handle_none(self) -> None:
        """Test async dispatching None with async handle_none."""

        class CustomChild(MockChildNode):
            async def handle_none(self, context: Any) -> int:
                await asyncio.sleep(0.001)
                return 0

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {}

        result = await dispatch_to_child_async(child, None, context)
        assert result == 0

    @pytest.mark.asyncio
    async def test_async_dispatch_primitive_with_async_handler(self) -> None:
        """Test async dispatching primitive with async handler."""

        class CustomChild(MockChildNode):
            async def handle_primitive(self, value: int, context: Any) -> int:
                await asyncio.sleep(0.001)
                return value * 2

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = await dispatch_to_child_async(child, 21, context)
        assert result == 42

    @pytest.mark.asyncio
    async def test_async_dispatch_primitive_with_sync_handler(self) -> None:
        """Test async dispatch can call sync handlers too."""

        class CustomChild(MockChildNode):
            def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = await dispatch_to_child_async(child, 21, context)
        assert result == 42

    @pytest.mark.asyncio
    async def test_async_dispatch_raises_unhandled_type_error(self) -> None:
        """Test async dispatch raises UnhandledTypeError when no handler."""
        child = MockChildNode()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {}

        with pytest.raises(UnhandledTypeError):
            await dispatch_to_child_async(child, 42, context)

    @pytest.mark.asyncio
    async def test_async_dispatch_handle_tag_validation_only(self) -> None:
        """Test async handle_tag must not return values."""

        class CustomChild(MockChildNode):
            async def handle_tag(self, value: Any, context: Any) -> Any:
                await asyncio.sleep(0.001)
                return "modified"  # This should raise error

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = True
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        with pytest.raises(InvalidHandlerError):
            await dispatch_to_child_async(child, {"key": "value"}, context)

    @pytest.mark.asyncio
    async def test_async_dispatch_not_implemented_fallback(self) -> None:
        """Test async dispatch NotImplementedError causes fallback."""

        class CustomChild(MockChildNode):
            async def handle_primitive(self, value: int, context: Any) -> int:
                raise NotImplementedError()

            async def handle_all(self, value: Any, context: Any) -> str:
                await asyncio.sleep(0.001)
                return "handled by handle_all"

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = await dispatch_to_child_async(child, 42, context)
        assert result == "handled by handle_all"

    @pytest.mark.asyncio
    async def test_async_dispatch_none_with_sync_handle_none(self) -> None:
        """Test async dispatch can call sync handle_none."""

        class CustomChild(MockChildNode):
            def handle_none(self, context: Any) -> int:
                return 0

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {}

        result = await dispatch_to_child_async(child, None, context)
        assert result == 0

    @pytest.mark.asyncio
    async def test_async_dispatch_with_sync_handle_all(self) -> None:
        """Test async dispatch with sync handle_all fallback."""

        class CustomChild(MockChildNode):
            def handle_all(self, value: Any, context: Any) -> str:
                return f"sync: {value}"

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        result = await dispatch_to_child_async(child, "test", context)
        assert result == "sync: test"

    @pytest.mark.asyncio
    async def test_async_dispatch_type_mismatch_raises_process_error(
        self,
    ) -> None:
        """Test async dispatch type mismatch raises ProcessError."""

        class CustomChild(MockChildNode):
            async def handle_primitive(self, value: int, context: Any) -> int:
                return value * 2

        child = CustomChild()
        context = Mock()
        context.is_tag.return_value = False
        context.click_context = Mock()
        context.click_context.meta = {"click_extended": {}}

        with pytest.raises(ProcessError) as exc_info:
            await dispatch_to_child_async(child, "not_an_int", context)

        assert "Type mismatch" in str(exc_info.value)
