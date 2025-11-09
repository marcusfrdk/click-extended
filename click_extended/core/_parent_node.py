"""Parent node."""

from abc import ABC
from typing import Any

from click_extended.core._child_node import ChildNode


class ParentNode(ABC):
    """Node that tags a decorator as a parameter (option, argument, env, tag)"""

    def __init__(self, name: str) -> None:
        """
        Initialize a new `ParentNode` instance.
        """
        self.name = name
        self.children: list[ChildNode] = []
        self.short: str | None = None
        self.long: str | None = None

    def add_child(self, child: ChildNode) -> None:
        self.children.append(child)

    def get_value(self) -> Any:
        pass
