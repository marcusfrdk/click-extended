"""Transformation decorator to convert a string to lowercase."""

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.types import Decorator


class ToLowercase(ChildNode):
    """Transformation decorator to convert a string to lowercase."""

    def process(self, value: str, context: ProcessContext) -> str:
        return value.lower()


def to_lowercase() -> Decorator:
    """
    Convert a value to lowercase.

    Returns:
        Decorator:
            The decorated function.
    """
    return ToLowercase.as_decorator()
