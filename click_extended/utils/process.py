"""Utility functions for processing child nodes."""

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode


def process_children(value: Any, children: dict[Any, Any]) -> Any:
    """
    Process a value through a chain of child nodes.

    Args:
        value (Any):
            The initial value to process.
        children (dict[Any, Any]):
            Dictionary of child nodes to process the value through.

    Returns:
        Any:
            The processed value after passing through all children.
    """
    all_children = [cast("ChildNode", child) for child in children.values()]

    for child in all_children:
        siblings = list(
            {c.__class__.__name__ for c in all_children if id(c) != id(child)}
        )

        value = child.process(
            value,
            *child.process_args,
            siblings=siblings,
            **child.process_kwargs,
        )

    return value
