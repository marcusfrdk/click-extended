"""Child node to add a suffix to a string."""

from typing import Any

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.types import Decorator


class AddSuffix(ChildNode):
    """Child node to add a suffix to a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        return value + kwargs["suffix"]

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


def add_suffix(suffix: str) -> Decorator:
    """
    Add a suffix to a string.

    Type: `ChildNode`

    Supports: `str`, `flat tuple`, `nested tuple`

    Args:
        suffix (str):
            The suffix to add.

    Returns:
        Decorator:
            The decorated function.
    """
    return AddSuffix.as_decorator(suffix=suffix)
