"""Class for storing the nodes of the current context."""

# pylint: disable=global-variable-not-assigned
# pylint: disable=import-outside-toplevel
# pylint: disable=broad-exception-caught

from typing import TYPE_CHECKING, Literal, cast

from click_extended.errors import (
    InvalidChildOnTagError,
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
    from click_extended.core.tag import Tag


_pending_nodes: list[
    tuple[
        Literal["parent", "child", "tag"],
        "ParentNode | ChildNode | Tag",
    ]
] = []


def get_pending_nodes() -> (
    list[
        tuple[Literal["parent", "child", "tag"], "ParentNode | ChildNode | Tag"]
    ]
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


def queue_tag(node: "Tag") -> None:
    """Queue a tag node for the next root registration."""
    _pending_nodes.append(("tag", node))


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
        self.recent_tag: "Tag | None" = None
        self.tags: dict[str, "Tag"] = {}

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
                if self.recent_tag is not None:
                    tag = self.recent_tag
                    child_inst = cast("ChildNode", node_inst)

                    sentinel = object()
                    is_validation_only = False

                    try:
                        result = child_inst.process(
                            sentinel,
                            *child_inst.process_args,
                            siblings=[],
                            tags={},
                            parent=tag,
                            **child_inst.process_kwargs,
                        )
                        is_validation_only = (
                            result is sentinel or result is None
                        )
                    except Exception:
                        is_validation_only = True

                    if not is_validation_only:
                        raise InvalidChildOnTagError(
                            child_name=child_inst.__class__.__name__,
                            tag_name=tag.name,
                        )

                    index = len(tag)
                    tag[index] = child_inst
                elif self.recent is not None:
                    name = self.recent.name
                    parent_node = cast("ParentNode", self.root[name])
                    index = len(parent_node)
                    parent_node[index] = cast("ChildNode", node_inst)
                else:
                    raise NoParentError(node_inst.name)
            elif node_type == "tag":
                tag_inst = cast("Tag", node_inst)
                self.tags[tag_inst.name] = tag_inst
                self.recent_tag = tag_inst

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
        parent_node[index] = node

    def visualize(self) -> None:
        """Visualize the tree."""
        visualize_tree(self.root)
