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

    def handle_flat_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return tuple(
            self.handle_str(v, context, *args, **kwargs) for v in value
        )

    def handle_nested_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return tuple(
            tuple(self.handle_str(v, context, *args, **kwargs) for v in t)
            for t in value
        )


def add_prefix(prefix: str) -> Decorator:
    """
    Add a prefix to a string.

    Type: `ChildNode`

    Supports: `str`, `flat tuple`, `nested tuple`

    Args:
        prefix (str):
            The prefix to add.

    Returns:
        Decorator:
            The decorated function.
    """
    return AddPrefix.as_decorator(prefix=prefix)
