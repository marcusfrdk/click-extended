"""Subtract a value from the input."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Subtract(ChildNode):
    """Subtract a value from the input."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return value - kwargs["n"]


def subtract(n: int | float) -> Decorator:
    """
    Subtract a value from the input.

    Type: `ChildNode`

    Supports: `int`, `float`

    :param n: The value to subtract.
    :returns: The decorated function.
    :rtype: Decorator
    """
    return Subtract.as_decorator(n=n)
