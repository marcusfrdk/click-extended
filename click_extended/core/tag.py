"""Representation of a tag in the command line."""

from collections.abc import Callable
from typing import Any

from click_extended.core._main import Main
from click_extended.core._parent import Parent


class Tag(Parent):
    """Representation of a tag in the command line.

    Tags group multiple options/arguments/envs and apply operations on the group.
    """

    def __init__(self, name: str) -> None:
        """Initialize a new Tag instance."""
        super().__init__(name=name, tags=[])


def tag(name: str) -> Callable[[Any], Any]:
    """Tag decorator - must be called with parentheses."""
    if callable(name):
        raise TypeError(
            "tag() must be called with parentheses: use @tag('tag_name') "
            "instead of @tag"
        )

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Tag decorator."""
        tag_instance = Tag(name=name)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(tag_instance)
            return tag_instance

        return tag_instance(main_or_parent)

    return wrapper
