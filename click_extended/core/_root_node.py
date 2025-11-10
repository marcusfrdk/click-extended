"""The node used as a root node."""

from typing import TYPE_CHECKING

from click_extended.core._node import Node

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode


class RootNode(Node):
    """The node used as a root node."""

    parent: None
    children: dict[str | int, "ParentNode"]

    def __init__(self, name: str) -> None:
        """
        Initialize a new `RootNode` instance.

        Args:
            name (str):
                The name of the node.
        """
        super().__init__(name=name, level=1)
