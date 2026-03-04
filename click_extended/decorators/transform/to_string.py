"""Child decorator to convert a value to a string."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class ToString(ChildNode):
    """Child decorator to convert a value to a string."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        return str(value)


def to_string() -> Decorator:
    """
    Convert a value to its string representation.

    Type: `ChildNode`

    Supports: all types

    :returns: The decorated function.
    :rtype: Decorator
    """
    return ToString.as_decorator()
