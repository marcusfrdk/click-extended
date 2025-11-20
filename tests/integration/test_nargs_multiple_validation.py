"""
Tests for strict type validation across nargs and multiple configurations.

This module tests the distinct cases that Click produces based on
nargs and multiple parameter combinations:
- Case 1a: nargs=1, multiple=False → Single value (T)
- Case 1b: nargs>1, multiple=False → Flat tuple (tuple[T, ...])
- Case 2: multiple=True → ALWAYS Nested tuple (tuple[tuple[T, ...], ...])

When multiple=True, values are ALWAYS injected as tuple[tuple[T, ...], ...]
regardless of nargs, to maintain consistent type semantics.
"""

from typing import Any

import pytest

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.option import Option
from click_extended.errors import ValidationError


class SingleValueProcessor(ChildNode):
    """Processor that expects a single value: value: str"""

    def process(self, value: str, context: ProcessContext) -> Any:
        return value.upper()


class FlatTupleProcessor(ChildNode):
    """Processor that expects a flat tuple: value: tuple[str, ...]"""

    def process(self, value: tuple[str, ...], context: ProcessContext) -> Any:
        return tuple(v.upper() for v in value)


class NestedTupleProcessor(ChildNode):
    """Processor that expects a nested tuple: value: tuple[tuple[str, ...], ...]"""

    def process(
        self, value: tuple[tuple[str, ...], ...], context: ProcessContext
    ) -> Any:
        return tuple(tuple(v.upper() for v in inner) for inner in value)


class TestCase1aSingleValue:
    """Test Case 1a: nargs=1, multiple=False → Single value (T)"""

    def test_single_value_with_correct_processor(self) -> None:
        """Single value option with single value processor should pass."""
        option = Option("--name", nargs=1, multiple=False)
        processor = SingleValueProcessor("processor")

        # Should not raise
        processor.validate_type(option)

    def test_single_value_with_flat_tuple_processor_fails(self) -> None:
        """Single value option with flat tuple processor should fail."""
        option = Option("--name", nargs=1, multiple=False)
        processor = FlatTupleProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "nargs=1 and multiple=False" in error_msg
        assert "produces a single value" in error_msg
        assert "expects tuple type" in error_msg

    def test_single_value_with_nested_tuple_processor_fails(self) -> None:
        """Single value option with nested tuple processor should fail."""
        option = Option("--name", nargs=1, multiple=False)
        processor = NestedTupleProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "nargs=1 and multiple=False" in error_msg
        assert "produces a single value" in error_msg
        assert "expects tuple type" in error_msg


class TestCase1bFlatTuple:
    """Test Case 1b: nargs>1, multiple=False → Flat tuple (tuple[T, ...])"""

    def test_nargs_gt_1_with_flat_tuple_processor(self) -> None:
        """Option with nargs>1 and flat tuple processor should pass."""
        option = Option("--coords", nargs=2, multiple=False)
        processor = FlatTupleProcessor("processor")

        # Should not raise
        processor.validate_type(option)

    def test_nargs_gt_1_with_single_value_processor_fails(self) -> None:
        """Option with nargs>1 and single value processor should fail."""
        option = Option("--coords", nargs=2, multiple=False)
        processor = SingleValueProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "nargs=2 and multiple=False" in error_msg
        assert "produces a flat tuple" in error_msg
        assert "expects non-tuple type" in error_msg

    def test_nargs_gt_1_with_nested_tuple_processor_fails(self) -> None:
        """Option with nargs>1 (multiple=False) and nested tuple processor should fail."""
        option = Option("--coords", nargs=2, multiple=False)
        processor = NestedTupleProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "nargs=2 and multiple=False" in error_msg
        assert "produces a flat tuple" in error_msg
        assert "expects nested tuple type" in error_msg


class TestCase2NestedTuple:
    """Test Case 2: multiple=True → ALWAYS Nested tuple (tuple[tuple[T, ...], ...])"""

    def test_multiple_true_nargs_1_with_nested_tuple_processor(self) -> None:
        """Option with nargs=1, multiple=True and nested tuple processor should pass."""
        option = Option("--tags", nargs=1, multiple=True)
        processor = NestedTupleProcessor("processor")

        # Should not raise
        processor.validate_type(option)

    def test_multiple_true_nargs_gt_1_with_nested_tuple_processor(
        self,
    ) -> None:
        """Option with nargs>1 and multiple=True with nested tuple processor should pass."""
        option = Option("--points", nargs=2, multiple=True)
        processor = NestedTupleProcessor("processor")

        # Should not raise
        processor.validate_type(option)

    def test_multiple_true_with_single_value_processor_fails(self) -> None:
        """Option with multiple=True and single value processor should fail."""
        option = Option("--tags", nargs=1, multiple=True)
        processor = SingleValueProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "multiple=True" in error_msg
        assert "ALWAYS produces a nested tuple" in error_msg
        assert "expects non-tuple type" in error_msg

    def test_multiple_true_with_flat_tuple_processor_fails(self) -> None:
        """Option with multiple=True and flat tuple processor should fail."""
        option = Option("--tags", nargs=1, multiple=True)
        processor = FlatTupleProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "multiple=True" in error_msg
        assert "ALWAYS produces a nested tuple" in error_msg
        assert "expects flat tuple type" in error_msg


class TestErrorMessages:
    """Test that error messages provide clear guidance."""

    def test_error_message_suggests_correct_type_for_case_1a(self) -> None:
        """Error message for Case 1a suggests correct type."""
        option = Option("--name", nargs=1, multiple=False, type=str)
        processor = FlatTupleProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "value: str" in error_msg

    def test_error_message_suggests_correct_type_for_case_2(self) -> None:
        """Error message for Case 2 suggests correct nested tuple type."""
        option = Option("--tags", nargs=1, multiple=True, type=str)
        processor = SingleValueProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        # Accept either tuple[tuple[str]] or tuple[tuple[str, ...], ...]
        assert "tuple[tuple[str" in error_msg and "]]" in error_msg


class TestDefaultBehavior:
    """Test default values for nargs and multiple parameters."""

    def test_option_defaults_to_case_1a(self) -> None:
        """Option without nargs/multiple should default to Case 1a."""
        option = Option("--name")
        processor = SingleValueProcessor("processor")

        # Should not raise - defaults to nargs=1, multiple=False
        processor.validate_type(option)

    def test_option_defaults_fail_with_wrong_processor(self) -> None:
        """Option defaults with wrong processor should fail."""
        option = Option("--name")
        processor = FlatTupleProcessor("processor")

        with pytest.raises(ValidationError) as exc_info:
            processor.validate_type(option)

        error_msg = str(exc_info.value)
        assert "nargs=1 and multiple=False" in error_msg
