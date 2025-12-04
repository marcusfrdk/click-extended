"""Child node to add a prefix to a string."""

from typing import Any

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.types import Decorator


class AddPrefix(ChildNode):
    """Child node to add a prefix to a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        return kwargs["prefix"] + value


def add_prefix(prefix: str) -> Decorator:
    """
    Add a prefix to a string.

    Type: `ChildNode`

    Supports: `str`

    Args:
        prefix (str):
            The prefix to add.

    Returns:
        Decorator:
            The decorated function.
    """
    return AddPrefix.as_decorator(prefix=prefix)
