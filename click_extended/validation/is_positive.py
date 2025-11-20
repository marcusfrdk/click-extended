"""Validation child for checking if a value is positive."""

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.errors import UnhandledValueError, ValidationError
from click_extended.types import Decorator
from click_extended.utils import (
    is_nested_tuple_value,
    is_single_value,
    is_tuple_value,
)


class IsPositive(ChildNode):
    """Validation child for checking if a value is positive."""

    def process(
        self,
        value: (
            int
            | float
            | tuple[int | float, ...]
            | tuple[tuple[int | float, ...], ...]
        ),
        context: ProcessContext,
    ) -> None:
        def check(v: int | float) -> None:
            if v <= 0:
                raise ValidationError(f"{v} is not positive")

        if is_single_value(value, (int, float)):
            check(value)
        elif is_tuple_value(value, (int, float)):
            for v in value:
                check(v)
        elif is_nested_tuple_value(value, (int, float)):
            for t in value:
                for v in t:
                    check(v)
        else:
            raise UnhandledValueError(value)


def is_positive() -> Decorator:
    """
    Validation decorator to check if a value is positive.

    Supports: `int | float`, `tuple[int | float]`, `tuple[tuple[int | float]].

    Returns:
        Decorator:
            The decorated function.
    """
    return IsPositive.as_decorator()
