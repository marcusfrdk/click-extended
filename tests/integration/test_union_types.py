"""Tests for union type support in validators/transformers."""

from typing import Any

import pytest

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.option import Option
from click_extended.errors import TypeMismatchError


class TestUnionTypeSupport:
    """Test that union types (str | int) are properly supported."""

    def test_union_type_with_matching_parent(self) -> None:
        """Union type should accept parent with matching type."""

        class UnionValidator(ChildNode):
            """Validator accepting str or int."""

            def process(
                self, value: tuple[str | int, ...], context: ProcessContext
            ) -> Any:
                return value

        validator = UnionValidator("validator")
        option_str = Option("--value", nargs=2, type=str)
        option_int = Option("--value", nargs=2, type=int)

        # Both should pass
        validator.validate_type(option_str)
        validator.validate_type(option_int)

    def test_union_type_rejects_non_matching_parent(self) -> None:
        """Union type should reject parent with non-matching type."""

        class UnionValidator(ChildNode):
            """Validator accepting str or int."""

            def process(
                self, value: tuple[str | int, ...], context: ProcessContext
            ) -> Any:
                return value

        validator = UnionValidator("validator")
        option = Option("--value", nargs=2, type=float)

        with pytest.raises(TypeMismatchError) as exc_info:
            validator.validate_type(option)

        error = exc_info.value
        assert "validator" in str(error)
        assert "value" in str(error)

    def test_single_value_with_union_type(self) -> None:
        """Single value with union type should work."""

        class SingleUnionValidator(ChildNode):
            """Validator accepting single str or int."""

            def process(self, value: str | int, context: ProcessContext) -> Any:
                return value

        validator = SingleUnionValidator("validator")
        option_str = Option("--value", type=str)
        option_int = Option("--value", type=int)

        # Both should pass
        validator.validate_type(option_str)
        validator.validate_type(option_int)

    def test_nested_tuple_with_union_type(self) -> None:
        """Nested tuple with union type should work when multiple=True."""

        class NestedUnionValidator(ChildNode):
            """Validator accepting nested tuples with str or int."""

            def process(
                self,
                value: tuple[tuple[str | int, ...], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = NestedUnionValidator("validator")
        option_str = Option("--value", nargs=2, multiple=True, type=str)
        option_int = Option("--value", nargs=2, multiple=True, type=int)

        # Both should pass
        validator.validate_type(option_str)
        validator.validate_type(option_int)

    def test_typing_union_syntax(self) -> None:
        """Test that typing.Union syntax also works."""
        from typing import Union

        class TypingUnionValidator(ChildNode):
            """Validator using typing.Union."""

            def process(
                self,
                value: tuple[Union[str, int], ...],
                context: ProcessContext,
            ) -> Any:
                return value

        validator = TypingUnionValidator("validator")
        option_str = Option("--value", nargs=2, type=str)
        option_int = Option("--value", nargs=2, type=int)

        # Both should pass
        validator.validate_type(option_str)
        validator.validate_type(option_int)
