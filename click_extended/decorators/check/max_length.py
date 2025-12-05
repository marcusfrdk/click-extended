"""Child decorator to check if a string is less than a set length."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class MaxLength(ChildNode):
    """Child decorator to check if a string is less than a set length."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        if kwargs["length"] < len(value):
            raise ValueError(
                "Value is too long, must be at most "
                f"'{kwargs['length']}' characters."
            )
        return value


def max_length(length: int) -> Decorator:
    """
    Check if a string is less than a set length.

    Type: `ChildNode`

    Supports: `str`

    Args:
        length (int):
            The maximum length to enforce.

    Returns:
        Decorator:
            The decorated function.
    """
    return MaxLength.as_decorator(length=length)
