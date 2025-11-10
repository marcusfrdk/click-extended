"""Base class for all node types."""

from abc import ABC
from typing import Literal


class Node(ABC):
    """Base class for all node types."""

    def __init__(
        self,
        name: str,
        level: Literal[1, 2, 3],
        parent: "Node | None" = None,
        children: dict[str | int, "Node"] | None = None,
    ):
        """
        Initialize a new `Node` instance.
        """
        self.name = name
        self.level = level
        self.parent = parent
        self.children = children or {}

    def get(self, name: str) -> "Node | None":
        """
        Get an entry from the children.

        Args:
            name (str):
                The name of the child.
        """
        return self.children.get(name, None)

    def __getitem__(self, name: str) -> "Node":
        return self.children[name]

    def __setitem__(self, name: str, node: "Node") -> None:
        self.children[name] = node

    def __len__(self) -> int:
        return len(self.children)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"
