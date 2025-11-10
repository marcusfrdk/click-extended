"""Class for storing the nodes of the current context."""

from click_extended.core._child_node import ChildNode
from click_extended.core._parent_node import ParentNode
from click_extended.core._root_node import RootNode
from click_extended.errors.no_parent_error import NoParentError
from click_extended.errors.no_root_error import NoRootError
from click_extended.errors.parent_node_exists_error import ParentNodeExistsError
from click_extended.errors.root_node_exists_error import RootNodeExistsError


class Tree:
    """Class for storing the nodes of the current context."""

    def __init__(self):
        """
        Initialize a new `Tree` instance.
        """
        self.root: RootNode | None = None
        self.recent: ParentNode | None = None

    def register_root(self, node: RootNode) -> None:
        """
        Register the root node.

        Args:
            node (RootNode):
                The node to register as the root node for the tree.

        Raises:
            RootNodeExistsError:
                If a root node already exists.
        """
        if isinstance(self.root, RootNode):
            raise RootNodeExistsError

        self.root = node

    def register_parent(self, node: ParentNode) -> None:
        """
        Register a new parent to the tree.

        Args:
            node (ParentNode):
                The parent node to register to the tree.

        Raises:
            ParentNodeExistsError:
                If a parent already exists with the name.
        """
        if self.root is None:
            raise NoRootError

        if self.root.get(node.name) is not None:
            raise ParentNodeExistsError(node.name)

        self.recent = node
        self.root[node.name] = node

    def register_child(self, node: ChildNode) -> None:
        """
        Register a new child to the most recently added parent.

        Args:
            node (ChildNode):
                The `ChildNode` to add to the `ParentNode` instance.

        Raises:
            ParentNotFoundError:
                If the parent with the name `name` does not exist.
        """
        if self.root is None:
            raise NoRootError

        if self.recent is None:
            raise NoParentError

        name = self.recent.name
        index = len(self.root[name])
        self.root[name].children[index] = node

    def visualize(self) -> None:
        """Visualize the tree."""
        if self.root is None:
            print("No root defined.")
            return

        print(self.root.name)
        for parent in self.root.children.values():
            print(f"  {parent.name}")
            for child in parent.children.values():
                print(f"    {child.name}")
