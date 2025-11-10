"""A node used for managing child nodes."""

from typing import TYPE_CHECKING, Any

from click_extended.core._child_node import ChildNode
from click_extended.core._node import Node

if TYPE_CHECKING:
    from click_extended.core._root_node import RootNode


class ParentNode(Node):
    """A node used for managing child nodes."""

    parent: "RootNode"
    children: dict[str | int, "ChildNode"]

    def __init__(self, name: str):
        """
        Initialize a new `ParentNode` instance.

        Args:
            name (str):
                The name of the node.
        """
        super().__init__(name=name, level=2)

    def get_value(self) -> Any:
        """
        Get the processed value of the chain of children.

        Returns:
            Any:
                The processed value of the chain of children.
        """
        # TODO: Retrieve the value from the option, argument, env, etc.
        value = ""

        for child in reversed(self.children.values()):
            value = child.process(value)

        return value
