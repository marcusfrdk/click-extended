"""Transformation decorator to convert a string to lowercase."""

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.errors import UnhandledValueError
from click_extended.types import Decorator
from click_extended.utils import (
    is_nested_tuple_value,
    is_single_value,
    is_tuple_value,
)


class ToLowercase(ChildNode):
    """Transformation decorator to convert a string to lowercase."""

    def process(
        self,
        value: str | tuple[str, ...] | tuple[tuple[str, ...], ...],
        context: ProcessContext,
    ) -> str | tuple[str, ...] | tuple[tuple[str, ...], ...]:
        if is_single_value(value, str):
            return value.lower()
        if is_tuple_value(value, str):
            return tuple(v.lower() for v in value)
        if is_nested_tuple_value(value, str):
            return tuple(tuple(v.lower() for v in t) for t in value)
        raise UnhandledValueError(value)


def to_lowercase() -> Decorator:
    """
    Convert a value to lowercase.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return ToLowercase.as_decorator()
