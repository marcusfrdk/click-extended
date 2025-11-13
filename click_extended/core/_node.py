"""Base class for all node types."""

from abc import ABC


class Node(ABC):
    """Base class for all node types."""

    children: dict[str | int, "Node"] | None

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
        self.children = children or {}

    def get(self, name: str) -> "Node | None":
        """
        Get an entry from the children.

        Args:
            name (str):
                The name of the child.
        """
        if self.children is None:
            return None
        return self.children.get(name, None)

    def __getitem__(self, name: str) -> "Node":
        if self.children is None:
            raise KeyError("Node has no children")
        return self.children[name]

    def __setitem__(self, name: str, node: "Node") -> None:
        if self.children is None:
            raise TypeError("Cannot set child on a node with no children")
        self.children[name] = node

    def __len__(self) -> int:
        if self.children is None:
            return 0
        return len(self.children)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"
