"""Tests for ChildNodes that support different types in different cases.

This tests the ability to have union type hints where the same types are available
across cases, but you can selectively handle different structures. The key insight:
- You CANNOT have completely different types per structure (e.g., int for single, str for tuple)
- You CAN have unions within structures that support multiple types
- The validation checks: does the parent_type appear in ANY union member that matches the structure?

Examples that WORK:
- str | int | tuple[str | int, ...] - both types supported in both cases
- str | tuple[str, ...] - str supported in both cases
- int | tuple[int | str, ...] - int for single, int OR str for tuple

Examples that DON'T work as you might expect:
- int | tuple[str, ...] - Python sees two union members, but int single won't match tuple[str]
"""

from typing import Any

import pytest

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.argument import Argument
from click_extended.core.option import Option
from click_extended.errors import TypeMismatchError


class TestTypeVariationAcrossCases:
    """Test that union types allow flexible type support across cases."""

    def test_same_types_all_structures(self) -> None:
        """Same types supported across all structures."""

        class UniformNode(ChildNode):
            """Accepts str or int for all cases."""

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

        validator = UniformNode("validator")

        # Single: both str and int work
        validator.validate_type(Option("--value", type=str))
        validator.validate_type(Option("--value", type=int))

        # Single: float fails
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--value", type=float))

        # Flat: both str and int work
        validator.validate_type(Option("--value", nargs=2, type=str))
        validator.validate_type(Option("--value", nargs=2, type=int))

        # Flat: float fails
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--value", nargs=2, type=float))

        # Nested: both str and int work
        validator.validate_type(
            Option("--value", nargs=2, multiple=True, type=str)
        )
        validator.validate_type(
            Option("--value", nargs=2, multiple=True, type=int)
        )

        # Nested: float fails
        with pytest.raises(TypeMismatchError):
            validator.validate_type(
                Option("--value", nargs=2, multiple=True, type=float)
            )


class TestComplexTypeVariations:
    """Test complex combinations of type variations."""

    def test_expanding_union_support(self) -> None:
        """Flat and nested cases can support more types than single."""

        class ExpandingNode(ChildNode):
            """Single has fewer types than tuple cases."""

            def process(
                self,
                value: (
                    str
                    | tuple[str | int | float, ...]
                    | tuple[tuple[str | int | float, ...], ...]
                ),
                context: ProcessContext,
            ) -> Any:
                return value

        validator = ExpandingNode("validator")

        # Single: only str
        validator.validate_type(Option("--v", type=str))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=int))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=float))

        # Flat: all three types
        validator.validate_type(Option("--v", nargs=2, type=str))
        validator.validate_type(Option("--v", nargs=2, type=int))
        validator.validate_type(Option("--v", nargs=2, type=float))

        # Nested: all three types
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=str))
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=int))
        validator.validate_type(
            Option("--v", nargs=2, multiple=True, type=float)
        )

    def test_argument_with_type_variations(self) -> None:
        """Arguments can also use type variations."""

        class ArgTypeNode(ChildNode):
            """Single and unlimited both support str and int."""

            def process(
                self,
                value: str | int | tuple[str | int, ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = ArgTypeNode("validator")

        # Single: str and int work
        validator.validate_type(Argument("value", type=str))
        validator.validate_type(Argument("value", type=int))

        # Unlimited: str and int work
        validator.validate_type(Argument("value", nargs=-1, type=str))
        validator.validate_type(Argument("value", nargs=-1, type=int))

        # Both fail with float
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Argument("value", type=float))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Argument("value", nargs=-1, type=float))

    def test_nested_has_extra_types(self) -> None:
        """Nested case can support additional types not in flat case."""

        class NestedExtraNode(ChildNode):
            """Nested supports more types."""

            def process(
                self,
                value: (
                    str | tuple[str, ...] | tuple[tuple[str | bool, ...], ...]
                ),
                context: ProcessContext,
            ) -> Any:
                return value

        validator = NestedExtraNode("validator")

        # Single and flat: only str
        validator.validate_type(Option("--v", type=str))
        validator.validate_type(Option("--v", nargs=2, type=str))

        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=bool))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", nargs=2, type=bool))

        # Nested: both str and bool
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=str))
        validator.validate_type(
            Option("--v", nargs=2, multiple=True, type=bool)
        )


class TestEdgeCasesWithTypeVariations:
    """Edge cases for type variations."""

    def test_single_type_all_cases(self) -> None:
        """Same single type supported across all cases."""

        class UniformNode(ChildNode):
            """str for all cases."""

            def process(
                self,
                value: str | tuple[str, ...] | tuple[tuple[str, ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = UniformNode("validator")

        # All cases with str should work
        validator.validate_type(Option("--v", type=str))
        validator.validate_type(Option("--v", nargs=2, type=str))
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=str))

        # All cases with int should fail
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=int))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", nargs=2, type=int))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(
                Option("--v", nargs=2, multiple=True, type=int)
            )

    def test_gradual_type_expansion(self) -> None:
        """Type support expands gradually through the cases."""

        class ExpandingNode(ChildNode):
            """Single=str, Flat=str|int, Nested=str|int|float."""

            def process(
                self,
                value: (
                    str
                    | tuple[str | int, ...]
                    | tuple[tuple[str | int | float, ...], ...]
                ),
                context: ProcessContext,
            ) -> Any:
                return value

        validator = ExpandingNode("validator")

        # Single: only str
        validator.validate_type(Option("--v", type=str))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=int))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=float))

        # Flat: str and int
        validator.validate_type(Option("--v", nargs=2, type=str))
        validator.validate_type(Option("--v", nargs=2, type=int))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", nargs=2, type=float))

        # Nested: all three
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=str))
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=int))
        validator.validate_type(
            Option("--v", nargs=2, multiple=True, type=float)
        )

    def test_flat_and_nested_only(self) -> None:
        """Support only tuple cases, not single value."""

        class TupleOnlyNode(ChildNode):
            """Only supports tuple structures."""

            def process(
                self,
                value: (
                    tuple[str | int, ...] | tuple[tuple[str | int, ...], ...]
                ),
                context: ProcessContext,
            ) -> Any:
                return value

        validator = TupleOnlyNode("validator")

        # Single should fail for both types
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=str))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=int))

        # Flat works for both types
        validator.validate_type(Option("--v", nargs=2, type=str))
        validator.validate_type(Option("--v", nargs=2, type=int))

        # Nested works for both types
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=str))
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=int))

    def test_single_and_nested_only(self) -> None:
        """Support single and nested, but not flat."""

        class SkipFlatNode(ChildNode):
            """Single and nested only."""

            def process(
                self,
                value: str | tuple[tuple[str, ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = SkipFlatNode("validator")

        # Single works
        validator.validate_type(Option("--v", type=str))

        # Flat fails (no flat tuple member in union)
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", nargs=2, type=str))

        # Nested works
        validator.validate_type(Option("--v", nargs=2, multiple=True, type=str))

    def test_custom_types_with_unions(self) -> None:
        """Custom types work with union support."""

        class CustomClass:
            pass

        class CustomNode(ChildNode):
            """Supports custom types across all cases."""

            def process(
                self,
                value: (
                    CustomClass
                    | tuple[CustomClass, ...]
                    | tuple[tuple[CustomClass, ...], ...]
                ),
                context: ProcessContext,
            ) -> Any:
                return value

        validator = CustomNode("validator")

        # All cases with CustomClass work
        validator.validate_type(Option("--v", type=CustomClass))
        validator.validate_type(Option("--v", nargs=2, type=CustomClass))
        validator.validate_type(
            Option("--v", nargs=2, multiple=True, type=CustomClass)
        )

        # All fail with str
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", type=str))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(Option("--v", nargs=2, type=str))
        with pytest.raises(TypeMismatchError):
            validator.validate_type(
                Option("--v", nargs=2, multiple=True, type=str)
            )
