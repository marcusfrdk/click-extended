"""Child decorator to check if a string has a minimum length."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class MinLength(ChildNode):
    """Child decorator to check if a string has a minimum length."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        if len(value) < kwargs["length"]:
            raise ValueError(
                "Value is too short, must be at "
                f"least '{kwargs['length']}' characters."
            )
        return value


def min_length(length: int) -> Decorator:
    """
    Check if a string has a minimum length.

    Type: `ChildNode`

    Supports: `str`

    Args:
        length (int):
            The minimum length to enforce.

    Returns:
        Decorator:
            The decorated function.
    """
    return MinLength.as_decorator(length=length)
