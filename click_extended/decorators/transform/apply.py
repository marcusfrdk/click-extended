"""Child decorator to apply an arbitrary function to any input."""

from typing import Any, Callable

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Apply(ChildNode):
    """Child decorator to apply an arbitrary function to any input."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        return kwargs["fn"](value)


def apply(fn: Callable[[Any], Any]) -> Decorator:
    """
    A decorator to apply an arbitrary function to all input.

    Type: `ChildNode`

    Supports: `Any`

    :param fn: The function to apply.
    :returns: The decorated function.
    :rtype: Decorator
    """
    return Apply.as_decorator(fn=fn)
