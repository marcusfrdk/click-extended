"""Child decorator to apply an arbitrary function to any input."""

from typing import Any, Callable

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.types import Decorator


class Apply(ChildNode):
    """Child decorator to apply an arbitrary function to any input."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        return kwargs["fn"](value)


def apply(fn: Callable[[Any], Any]) -> Decorator:
    """
    A `ChildNode` decorator to apply an arbitrary function to all input.

    Args:
        fn (Callable[[Any], Any]):
            The function to apply.

    Returns:
        Decorator:
            The decorated function.
    """
    return Apply.as_decorator(fn=fn)
