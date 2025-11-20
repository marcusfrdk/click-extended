"""Tests for flexible union type validation allowing multi-case ChildNodes."""

from typing import Any, Union

import pytest

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.argument import Argument
from click_extended.core.option import Option
from click_extended.errors import TypeMismatchError, ValidationError


class FlexibleChildNode(ChildNode):
    """A ChildNode that handles single values, flat tuples, and nested tuples."""

    def process(
        self,
        value: (
            str
            | int
            | tuple[str | int, ...]
            | tuple[tuple[str | int, ...], ...]
        ),
        context: ProcessContext,
    ) -> Any:
        return value


class TestFlexibleUnionValidation:
    """Test that union types can handle multiple value structures."""

    # === Valid Cases ===

    def test_union_accepts_single_value_str(self) -> None:
        """Union should accept single value option with str."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", type=str)
        validator.validate_type(option)  # Should not raise

    def test_union_accepts_single_value_int(self) -> None:
        """Union should accept single value option with int."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", type=int)
        validator.validate_type(option)  # Should not raise

    def test_union_accepts_flat_tuple_nargs2(self) -> None:
        """Union should accept flat tuple with nargs=2."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", nargs=2, type=str)
        validator.validate_type(option)  # Should not raise

    def test_union_accepts_flat_tuple_nargs3(self) -> None:
        """Union should accept flat tuple with nargs=3."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", nargs=3, type=int)
        validator.validate_type(option)  # Should not raise

    def test_union_accepts_nested_tuple_multiple(self) -> None:
        """Union should accept nested tuple with multiple=True."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", nargs=2, multiple=True, type=str)
        validator.validate_type(option)  # Should not raise

    def test_union_accepts_nested_tuple_nargs1_multiple(self) -> None:
        """Union should accept nested tuple with nargs=1, multiple=True."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", nargs=1, multiple=True, type=int)
        validator.validate_type(option)  # Should not raise

    def test_union_accepts_argument_single(self) -> None:
        """Union should accept single value argument."""
        validator = FlexibleChildNode("validator")
        arg = Argument("value", type=str)
        validator.validate_type(arg)  # Should not raise

    def test_union_accepts_argument_nargs_unlimited(self) -> None:
        """Union should accept argument with nargs=-1 (flat tuple)."""
        validator = FlexibleChildNode("validator")
        arg = Argument("value", nargs=-1, type=str)
        validator.validate_type(arg)  # Should not raise

    # === Invalid Cases - Unsupported Parent Type ===

    def test_union_rejects_unsupported_type_float(self) -> None:
        """Union should reject parent with unsupported type (float)."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", type=float)

        with pytest.raises(TypeMismatchError) as exc_info:
            validator.validate_type(option)

        assert "validator" in str(exc_info.value)

    def test_union_rejects_unsupported_type_bool(self) -> None:
        """Union should reject parent with unsupported type (bool)."""
        validator = FlexibleChildNode("validator")
        option = Option("--value", type=bool)

        with pytest.raises(TypeMismatchError) as exc_info:
            validator.validate_type(option)

        assert "validator" in str(exc_info.value)

    # === Edge Cases ===

    def test_union_with_typing_union_syntax(self) -> None:
        """Union validation should work with typing.Union syntax."""

        class TypingUnionNode(ChildNode):
            """Node using typing.Union."""

            def process(
                self,
                value: Union[
                    str, int, tuple[str, ...], tuple[tuple[str, ...], ...]
                ],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = TypingUnionNode("validator")
        option_single = Option("--value", type=str)
        option_flat = Option("--value", nargs=2, type=str)
        option_nested = Option("--value", nargs=2, multiple=True, type=str)

        # All should pass
        validator.validate_type(option_single)
        validator.validate_type(option_flat)
        validator.validate_type(option_nested)

    def test_union_with_mixed_types_single_and_flat(self) -> None:
        """Union can mix different inner types for single and flat cases."""

        class MixedTypeNode(ChildNode):
            """Node with str for single, int for tuples."""

            def process(
                self,
                value: str | tuple[int, ...] | tuple[tuple[int, ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = MixedTypeNode("validator")

        # Single str should work
        option_str = Option("--value", type=str)
        validator.validate_type(option_str)

        # Flat tuple of int should work
        option_int_flat = Option("--value", nargs=2, type=int)
        validator.validate_type(option_int_flat)

        # Nested tuple of int should work
        option_int_nested = Option("--value", nargs=2, multiple=True, type=int)
        validator.validate_type(option_int_nested)

        # Single int should fail (not in union)
        option_int_single = Option("--value", type=int)
        with pytest.raises(TypeMismatchError):
            validator.validate_type(option_int_single)

    def test_union_with_partial_support(self) -> None:
        """Union can support only some cases, not all three."""

        class PartialNode(ChildNode):
            """Node supporting only flat and nested, not single."""

            def process(
                self,
                value: tuple[str, ...] | tuple[tuple[str, ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = PartialNode("validator")

        # Flat should work
        option_flat = Option("--value", nargs=2, type=str)
        validator.validate_type(option_flat)

        # Nested should work
        option_nested = Option("--value", nargs=2, multiple=True, type=str)
        validator.validate_type(option_nested)

        # Single should fail
        option_single = Option("--value", type=str)
        with pytest.raises(TypeMismatchError):
            validator.validate_type(option_single)

    def test_union_empty_tuple_edge_case(self) -> None:
        """Union should handle options that might produce empty tuples."""
        validator = FlexibleChildNode("validator")

        # nargs=0 is not valid in Click, but let's test multiple=True with default
        option = Option("--value", nargs=2, multiple=True, type=str, default=())
        validator.validate_type(option)  # Should not raise

    def test_union_with_none_in_union(self) -> None:
        """Union with None should still validate correctly."""

        class OptionalNode(ChildNode):
            """Node with optional value."""

            def process(
                self,
                value: (
                    str | None | tuple[str, ...] | tuple[tuple[str, ...], ...]
                ),
                context: ProcessContext,
            ) -> Any:
                return value

        validator = OptionalNode("validator")

        # Single value should work
        option_single = Option("--value", type=str)
        validator.validate_type(option_single)

        # Flat tuple should work
        option_flat = Option("--value", nargs=2, type=str)
        validator.validate_type(option_flat)

        # Nested should work
        option_nested = Option("--value", nargs=2, multiple=True, type=str)
        validator.validate_type(option_nested)

    def test_union_complex_nested_structure(self) -> None:
        """Union validation with complex nested union types."""

        class ComplexNode(ChildNode):
            """Node with complex nested unions."""

            def process(
                self,
                value: (
                    str
                    | int
                    | tuple[str | int, ...]
                    | tuple[tuple[str | int, ...], ...]
                ),
                context: ProcessContext,
            ) -> Any:
                return value

        validator = ComplexNode("validator")

        # Test all combinations of str and int
        test_cases = [
            Option("--v", type=str),  # single str
            Option("--v", type=int),  # single int
            Option("--v", nargs=2, type=str),  # flat str
            Option("--v", nargs=2, type=int),  # flat int
            Option("--v", nargs=2, multiple=True, type=str),  # nested str
            Option("--v", nargs=2, multiple=True, type=int),  # nested int
        ]

        for option in test_cases:
            validator.validate_type(option)  # All should pass

    # === Inheritance Cases ===

    def test_union_with_inherited_childnode(self) -> None:
        """Union validation should work with inherited ChildNodes."""

        class BaseNode(ChildNode):
            """Base node."""

            def process(
                self,
                value: str | tuple[str, ...] | tuple[tuple[str, ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        class DerivedNode(BaseNode):
            """Derived node with same signature."""

            pass

        validator = DerivedNode("validator")
        option_single = Option("--value", type=str)
        option_flat = Option("--value", nargs=2, type=str)
        option_nested = Option("--value", nargs=2, multiple=True, type=str)

        # All should work
        validator.validate_type(option_single)
        validator.validate_type(option_flat)
        validator.validate_type(option_nested)

    def test_union_overridden_process_method(self) -> None:
        """Union validation uses the actual process() signature."""

        class BaseNode(ChildNode):
            """Base with broad union."""

            def process(
                self,
                value: str | tuple[str, ...] | tuple[tuple[str, ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        class NarrowNode(BaseNode):
            """Override with narrower type."""

            def process(  # type: ignore[override]
                self, value: str, context: ProcessContext
            ) -> Any:
                return value

        validator = NarrowNode("validator")

        option_single = Option("--value", type=str)
        validator.validate_type(option_single)

        option_flat = Option("--value", nargs=2, type=str)
        with pytest.raises(ValidationError):
            validator.validate_type(option_flat)

    # === No Type Hint Cases ===

    def test_union_no_type_hint_allows_all(self) -> None:
        """ChildNode without type hint should allow any parent."""

        class NoHintNode(ChildNode):
            """Node without type hints."""

            def process(self, value, context: ProcessContext) -> Any:  # type: ignore
                return value

        validator = NoHintNode("validator")

        # All should pass (no validation when no hints)
        validator.validate_type(Option("--value", type=str))
        validator.validate_type(Option("--value", nargs=2, type=float))
        validator.validate_type(
            Option("--value", nargs=2, multiple=True, type=bool)
        )

    def test_union_missing_value_parameter(self) -> None:
        """ChildNode without 'value' parameter should not raise."""

        class NoValueNode(ChildNode):
            """Node with different parameter name."""

            def process(  # type: ignore[override]
                self,
                data: str,
                context: ProcessContext,
            ) -> Any:
                return data

        validator = NoValueNode("validator")
        option = Option("--value", type=str)

        # Should not raise (validation skipped when 'value' param not found)
        validator.validate_type(option)


class TestFlexibleUnionEdgeCases:
    """Additional edge cases for union validation."""

    def test_union_with_ellipsis_only(self) -> None:
        """Handle tuple[...] edge case."""

        class EllipsisNode(ChildNode):
            """Node with ambiguous ellipsis."""

            def process(
                self, value: str | tuple[str, ...], context: ProcessContext
            ) -> Any:
                return value

        validator = EllipsisNode("validator")
        option = Option("--value", nargs=2, type=str)
        validator.validate_type(option)  # Should not raise

    def test_union_deeply_nested_invalid(self) -> None:
        """Triple-nested tuples should not match any case."""

        class TripleNestedNode(ChildNode):
            """Invalid triple-nested structure."""

            def process(
                self,
                value: tuple[tuple[tuple[str, ...], ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = TripleNestedNode("validator")
        option = Option("--value", nargs=2, multiple=True, type=str)

        # Should fail - triple nesting doesn't match expected double nesting
        with pytest.raises(TypeMismatchError):
            validator.validate_type(option)

    def test_union_all_non_matching_members(self) -> None:
        """Union where no member matches should fail."""

        class NoMatchNode(ChildNode):
            """Union with no matching members."""

            def process(
                self, value: float | bool | list[str], context: ProcessContext
            ) -> Any:
                return value

        validator = NoMatchNode("validator")
        option = Option("--value", type=str)

        # Should fail - str not in union
        with pytest.raises(TypeMismatchError):
            validator.validate_type(option)

    def test_union_with_generic_types(self) -> None:
        """Union with generic types like list should not match tuple."""

        class GenericNode(ChildNode):
            """Node with list instead of tuple."""

            def process(
                self, value: str | list[str], context: ProcessContext
            ) -> Any:
                return value

        validator = GenericNode("validator")

        # Single should work
        option_single = Option("--value", type=str)
        validator.validate_type(option_single)

        # Flat tuple should fail (list != tuple)
        option_flat = Option("--value", nargs=2, type=str)
        with pytest.raises(TypeMismatchError):
            validator.validate_type(option_flat)
