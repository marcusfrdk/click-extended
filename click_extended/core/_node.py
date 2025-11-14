"""Base class for all node types."""

from abc import ABC
from typing import Mapping


class Node(ABC):
    """Base class for all node types."""

    _children: dict[str | int, "Node"] | None

    def __init__(
        self,
        name: str,
        parent: "Node | None" = None,
        children: dict[str | int, "Node"] | None = None,
    ):
        """
        Initialize a new `Node` instance.
        """
        self.name = name
        self.parent = parent
        self._children = children or {}

    @property
    def children(self) -> Mapping[str | int, "Node"] | None:
        """Get the children dictionary."""
        return self._children

    @children.setter
    def children(self, value: dict[str | int, "Node"] | None) -> None:
        """Set the children dictionary."""
        self._children = value

    def get(self, name: str) -> "Node | None":
        """
        Get an entry from the children.

        Args:
            name (str):
                The name of the child.
        """
        if self._children is None:
            return None
        return self._children.get(name, None)

    def __getitem__(self, name: str | int) -> "Node":
        if self._children is None:
            raise KeyError("Node has no children")
        return self._children[name]

    def __setitem__(self, name: str | int, node: "Node") -> None:
        if self._children is None:
            raise TypeError("Cannot set child on a node with no children")
        self._children[name] = node

    def __len__(self) -> int:
        if self._children is None:
            return 0
        return len(self._children)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"
