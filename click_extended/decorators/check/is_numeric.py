"""Check if a value is numeric."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsNumeric(ChildNode):
    """Check if a value is numeric."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        try:
            float(value)
        except ValueError as e:
            raise ValueError(f"Value '{value}' is not numeric.") from e
        return value


def is_numeric() -> Decorator:
    """
    Check if a value is numeric (i.e. can be interpreted as an int or float).

    Type: `ChildNode`

    Supports: `str`

    :returns: The decorated function.
    :rtype: Decorator
    """
    return IsNumeric.as_decorator()
