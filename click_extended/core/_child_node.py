"""The node used as a child node.."""

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from click_extended.core._node import Node

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode


class ChildNode(Node):
    """The node used as a child node."""

    parent: "ParentNode"
    children: None

    def __init__(self, name: str) -> None:
        """
        Initialize a new `ChildNode` instance.

        Args:
            name (str):
                The name of the node.
        """
        super().__init__(name=name, level=3)

    def get(self, name: str) -> None:
        """
        The `ChildNode` has no children, thus this method
        returns `None`.

        Args:
            name (str):
                The name of the child.

        Returns:
            None:
                Always returns `None` as the `ChildNode` has no children.
        """
        return None

    def __getitem__(self, name: str) -> Node:
        raise KeyError(f"A ChildNode instance has no children.")

    @abstractmethod
    def process(self, value: Any) -> Any:
        """
        Process the value of the chain and returns the processed value.

        Args:
            value (Any):
                The input value.

        Returns:
            Any:
                The processed value.
        """
        raise NotImplementedError
