"""Transformation decorator to add a prefix to a string."""

from typing import Any

from click_extended.core._child_node import ChildNode


class Prefix(ChildNode):
    """Decorator to add a prefix to a string."""

    def process(self, value: Any, *args: Any, **kwargs: Any):
        if not isinstance(value, str):
            raise TypeError("Value is not of type string.")

        return kwargs.get("prefix", "") + value


# TODO: Implement this decorator in a way that makes it simple and type-hinted.

# def prefix():
#   ...
