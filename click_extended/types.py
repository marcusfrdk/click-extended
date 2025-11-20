"""Types used in `click_extended` which can be useful for users."""

# pylint: disable=invalid-name

from typing import Any, Callable

from click_extended.core._child_node import ProcessContext
from click_extended.core.argument import Argument
from click_extended.core.command import Command
from click_extended.core.env import Env
from click_extended.core.group import Group
from click_extended.core.option import Option
from click_extended.core.tag import Tag

Tags = dict[str, Tag]
Siblings = list[str]
Parent = "ParentNode | Tag"
Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]

__all__ = [
    "ProcessContext",
    "Decorator",
    "Parent",
    "Argument",
    "Command",
    "Env",
    "Group",
    "Option",
    "Siblings",
    "Tag",
    "Tags",
]
