"""Child validation decorator to check exclusiveness between nodes."""

from typing import Any

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.core.tag import Tag
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class Exclusive(ChildNode):
    """Child validation decorator to check exclusiveness between nodes."""

    def _normalize_list(self, value: str | list[str] | None) -> list[str]:
        """
        Normalize the `with_parents` or `with_tags`
        parameters to a list of strings.

        Args:
            value (str | list[str] | None):
                The input value.

        Returns:
            list[str]:
                The normalized parameter value.
        """
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value

    def _get_conflicting_parents(
        self,
        context: Context,
        with_parents: list[str],
        with_tags: list[str],
    ) -> set[str]:
        """
        Get the set of parent names that were provided and conflict.

        Args:
            context (Context):
                The current context.
            with_parents (list[str]):
                List of parent names to check.
            with_tags (list[str]):
                List of tag names to check.

        Returns:
            set[str]:
                Set of conflicting parent names that were provided.
        """
        conflicts: set[str] = set()

        for parent_name in with_parents:
            parent_node = context.get_parent(parent_name)
            if parent_node is not None and parent_node.was_provided:
                conflicts.add(parent_name)

        tagged_parents = context.get_tagged()
        for tag_name in with_tags:
            if tag_name in tagged_parents:
                for node in tagged_parents[tag_name]:
                    if node.was_provided:
                        conflicts.add(node.name)

        return conflicts

    def handle_all(
        self,
        value: Any,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        parent = context.parent
        if parent is None:
            raise EnvironmentError("Parent should be defined, but is not.")

        if isinstance(parent, Tag):
            raise TypeError("Parent is a tag, but should not be able to be.")

        if not parent.was_provided:
            return

        with_parents = self._normalize_list(kwargs.get("with_parents"))
        with_tags = self._normalize_list(kwargs.get("with_tags"))

        conflicts = self._get_conflicting_parents(
            context, with_parents, with_tags
        )

        if conflicts:
            humanized = humanize_iterable(conflicts, wrap="'")
            raise ValueError(
                f"{parent.__class__.__name__} '{parent.name}' is exclusive "
                f"with {humanized}"
            )

    def handle_tag(
        self,
        value: dict[str, Any],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        parent = context.parent
        if parent is None:
            raise EnvironmentError("Parent should be defined, but is not.")

        if not isinstance(parent, Tag):
            raise ValueError(
                f"Parent should be a tag, but got {type(parent).__name__}"
            )

        if not parent.get_provided_values():
            return

        provided = context.get_provided_values()
        provided_in_tag = {
            name: val for name, val in provided.items() if name in value
        }

        if len(provided_in_tag) > 1:
            parent_names = list(provided_in_tag.keys())
            humanized = humanize_iterable(parent_names, wrap="'")
            raise ValueError(
                f"Only one of {humanized} "
                f"can be provided, but got {len(provided_in_tag)}"
            )


def exclusive(
    with_parents: str | list[str] | None = None,
    with_tags: str | list[str] | None = None,
) -> Decorator:
    """
    Checks for exclusiveness between nodes in the tree.

    Args:
        with_parents (str | list[str] | None, optional):
            Check for exclusiveness between other parents in the tree.
        with_tags (str | list[str] | None, optional):
            Check for exclusiveness between other tags in the tree.

    Returns:
        Decorator:
            The decorated function.

    Raises:
        ValueError:
            If the exclusiveness validation fails.
    """
    return Exclusive.as_decorator(
        with_parents=with_parents,
        with_tags=with_tags,
    )
