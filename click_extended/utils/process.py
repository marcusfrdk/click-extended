"""Utility functions for processing child nodes."""

# pylint: disable=broad-exception-caught

from typing import TYPE_CHECKING, Any, Mapping, cast

from click_extended.core._child_node import ProcessContext

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode
    from click_extended.core._parent_node import ParentNode
    from click_extended.core.tag import Tag


def process_children(
    value: Any,
    children: Mapping[Any, Any],
    parent: "ParentNode | Tag",
    tags: dict[str, "Tag"] | None = None,
) -> Any:
    """
    Process a value through a chain of child nodes.

    Args:
        value (Any):
            The initial value to process.
        children (Mapping[Any, Any]):
            Mapping of child nodes to process the value through.
        parent (ParentNode | Tag):
            The parent node that owns these children.
        tags (dict[str, Tag], optional):
            Dictionary mapping tag names to Tag instances.
            Passed to each child's process method.

    Returns:
        Any:
            The processed value after passing through all children.

    Raises:
        TypeMismatchError:
            If a child node doesn't support the parent's type.
    """
    all_children = [cast("ChildNode", child) for child in children.values()]

    if tags is None:
        tags = {}

    if parent.__class__.__name__ not in ("Tag",):
        for child in all_children:
            child.validate_type(cast("ParentNode", parent))

    for child in all_children:
        siblings = list(
            {c.__class__.__name__ for c in all_children if id(c) != id(child)}
        )

        context = ProcessContext(
            parent=parent,
            siblings=siblings,
            tags=tags,
            args=child.process_args,
            kwargs=child.process_kwargs,
        )

        if value is None and child.should_skip_none():
            continue

        result = child.process(value, context)

        if result is not None:
            value = result

    return value
