"""Child decorator to convert an integer ot floating point number to a Decimal."""

from decimal import Decimal
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class ToDecimal(ChildNode):
    """Child decorator to convert an integer ot floating point number to a Decimal."""

    def handle_numeric(
        self, value: int | float, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        return Decimal(value)


def to_decimal() -> Decorator:
    """
    Convert an integer or floating point number to a Decimal.

    Type: `ChildNode`

    Supports: `int`, `float`
    :returns: The decorated function.
    :rtype: Decorator
    """
    return ToDecimal.as_decorator()
