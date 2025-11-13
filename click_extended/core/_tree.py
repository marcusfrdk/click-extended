"""Class for storing the nodes of the current context."""

# pylint: disable=global-variable-not-assigned
# pylint: disable=import-outside-toplevel

from typing import TYPE_CHECKING, Literal, cast

from click_extended.errors import (
    NoParentError,
    NoRootError,
    ParentNodeExistsError,
    RootNodeExistsError,
)
from click_extended.utils.visualize import visualize_tree

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode
    from click_extended.core._parent_node import ParentNode
    from click_extended.core._root_node import RootNode


_pending_nodes: list[
    tuple[
        Literal["parent", "child"],
        "ParentNode | ChildNode",
    ]
] = []


def get_pending_nodes() -> (
    list[tuple[Literal["parent", "child"], "ParentNode | ChildNode"]]
):
    """Get and clear the pending nodes queue."""
    global _pending_nodes
    nodes = _pending_nodes.copy()
    _pending_nodes.clear()
    return nodes


def queue_parent(node: "ParentNode") -> None:
    """Queue a parent node for the next root registration."""
    _pending_nodes.append(("parent", node))


def queue_child(node: "ChildNode") -> None:
    """Queue a child node for the next root registration."""
    _pending_nodes.append(("child", node))


class Tree:
    """
    Class for storing the nodes of the current context.

    This tree is designed to work with decorators, which are applied
    bottom-to-top. Registrations are queued and then built in reverse
    order to maintain the hierarchy.
    """

    def __init__(self) -> None:
        """Initialize a new `Tree` instance."""
        self.root: "RootNode | None" = None
        self.recent: "ParentNode | None" = None

    def register_root(self, node: "RootNode") -> None:
        """
        Register the root node and build the tree from pending nodes.

        In decorator systems, the root is called last, so we can
        build the tree when it's registered by processing all
        pending nodes that were queued during decoration.

        Args:
            node (RootNode):
                The node to register as the root node for the tree.
        """
        if self.root is not None:
            raise RootNodeExistsError
        self.root = node

        pending = list(reversed(get_pending_nodes()))

        for node_type, node_inst in pending:
            if node_type == "parent":
                if self.root.get(node_inst.name) is not None:
                    raise ParentNodeExistsError(node_inst.name)

                self.recent = cast("ParentNode", node_inst)
                self.root[node_inst.name] = node_inst
            elif node_type == "child":
                if self.recent is None:
                    raise NoParentError(node_inst.name)

                name = self.recent.name
                parent_node = cast("ParentNode", self.root[name])
                index = len(parent_node)
                assert parent_node.children is not None
                parent_node.children[index] = cast("ChildNode", node_inst)

    def register_parent(self, node: "ParentNode") -> None:
        """
        Register a parent node directly to this tree.

        Args:
            node (ParentNode):
                The parent node to register to the tree.
        """
        if self.root is None:
            raise NoRootError

        if self.root.get(node.name) is not None:
            raise ParentNodeExistsError(node.name)

        self.recent = node
        self.root[node.name] = node

    def register_child(self, node: "ChildNode") -> None:
        """
        Register a child node directly to this tree.

        This method is for runtime registration, not decorator-time.

        Args:
            node (ChildNode):
                The `ChildNode` to add to the `ParentNode` instance.
        """
        if self.root is None:
            raise NoRootError

        if self.recent is None:
            raise NoParentError(node.name)

        name = self.recent.name
        parent_node = cast("ParentNode", self.root[name])
        index = len(parent_node)
        assert parent_node.children is not None
        parent_node.children[index] = node

    def visualize(self) -> None:
        """Visualize the tree."""
        visualize_tree(self.root)
