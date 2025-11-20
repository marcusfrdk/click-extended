"""Utility functions for processing child nodes."""

# pylint: disable=broad-exception-caught

from typing import TYPE_CHECKING, Any, Mapping, cast

import click

from click_extended.core._child_node import ProcessContext
from click_extended.errors import CatchableError, ParameterError

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode
    from click_extended.core._parent_node import ParentNode
    from click_extended.core.tag import Tag


def process_children(
    value: Any,
    children: Mapping[Any, Any],
    parent: "ParentNode | Tag",
    tags: dict[str, "Tag"] | None = None,
    ctx: click.Context | None = None,
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
        ctx (click.Context, optional):
            The Click context for error reporting.

    Returns:
        Any:
            The processed value after passing through all children.

    Raises:
        TypeMismatchError:
            If a child node doesn't support the parent's type.
        ParameterError:
            If validation or transformation fails in a child node.
    """
    all_children = [cast("ChildNode", child) for child in children.values()]

    if tags is None:
        tags = {}

    if parent.__class__.__name__ not in ("Tag",):
        for child in all_children:
            child.validate_type(cast("ParentNode", parent))

    try:
        for child in all_children:
            siblings = list(
                {
                    c.__class__.__name__
                    for c in all_children
                    if id(c) != id(child)
                }
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

    except CatchableError as e:
        param_hint = _get_param_hint(parent)

        raise ParameterError(
            message=str(e),
            param_hint=param_hint,
            ctx=ctx,
        ) from e

    return value


def _get_param_hint(parent: "ParentNode | Tag") -> str | None:
    """
    Extract parameter name for error messages.

    Args:
        parent: The parent node (Option, Argument, or Tag).

    Returns:
        str | None: The parameter hint (e.g., '--config', 'PATH'), or None.
    """
    if hasattr(parent, "long") and getattr(parent, "long", None):
        return str(getattr(parent, "long"))

    if hasattr(parent, "opts") and getattr(parent, "opts", None):
        opts = getattr(parent, "opts")
        return str(next((opt for opt in opts if opt.startswith("--")), opts[0]))

    if hasattr(parent, "name") and getattr(parent, "name", None):
        return str(getattr(parent, "name")).upper()

    return None
