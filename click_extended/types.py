"""Types used in `click_extended` which can be useful for users."""

from click_extended.core._child_node import ChildNode
from click_extended.core._node import Node
from click_extended.core._parent_node import ParentNode
from click_extended.core._root_node import RootNode
from click_extended.core._tree import Tree
from click_extended.core.argument import Argument
from click_extended.core.command import Command
from click_extended.core.env import Env
from click_extended.core.group import Group
from click_extended.core.option import Option
from click_extended.core.tag import Tag

Tags = dict[str, Tag]
Siblings = list[str]
Parent = ParentNode | Tag

__all__ = [
    "ChildNode",
    "Node",
    "Parent",
    "ParentNode",
    "RootNode",
    "Tree",
    "Argument",
    "Command",
    "Env",
    "Group",
    "Option",
    "Siblings",
    "Tag",
    "Tags",
]
