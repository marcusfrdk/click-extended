"""Singleton class for storing the nodes of the current context."""

from threading import Lock
from typing import TYPE_CHECKING, Any

from click_extended.errors.no_parent_error import NoParentError
from click_extended.errors.no_root_error import NoRootError
from click_extended.errors.parent_node_exists_error import ParentNodeExistsError
from click_extended.errors.root_node_exists_error import RootNodeExistsError

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode
    from click_extended.core._parent_node import ParentNode
    from click_extended.core._root_node import RootNode


class Tree:
    """Singleton class for storing the nodes of the current context."""

    _instance: "Tree | None" = None
    _lock = Lock()

    root: "RootNode | None"
    recent: "ParentNode | None"

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.root = None
                    cls._instance.recent = None
        return cls._instance

    def __init__(self) -> None:
        """Initialize a new `Tree` instance."""

    def __copy__(self) -> "Tree":
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> "Tree":
        return self

    def __reduce__(self) -> tuple[type["Tree"], tuple[()]]:
        return (self.__class__, ())

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


tree = Tree()
