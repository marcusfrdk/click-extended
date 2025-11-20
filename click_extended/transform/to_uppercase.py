"""Transformation decorator to convert a string to uppercase."""

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.types import Decorator


class ToUppercase(ChildNode):
    """Transformation decorator to convert a string to uppercase."""

    def process(self, value: str, context: ProcessContext) -> str:
        return value.upper()


def to_uppercase() -> Decorator:
    """
    Convert a value to uppercase.

    Returns:
        Decorator:
            The decorated function.
    """
    return ToUppercase.as_decorator()
