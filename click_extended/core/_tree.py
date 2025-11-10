"""Singleton class for storing the nodes of the current context."""

from threading import Lock
from typing import TYPE_CHECKING, Any, Literal, cast

from click_extended.errors.no_parent_error import NoParentError
from click_extended.errors.no_root_error import NoRootError
from click_extended.errors.parent_node_exists_error import ParentNodeExistsError
from click_extended.errors.root_node_exists_error import RootNodeExistsError

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode
    from click_extended.core._parent_node import ParentNode
    from click_extended.core._root_node import RootNode


class Tree:
    """
    Singleton class for storing the nodes of the current context.

    This tree is designed to work with decorators, which are applied
    bottom-to-top. Registrations are queued and then built in reverse
    order to maintain the hierarchy.
    """

    _instance: "Tree | None" = None
    _lock = Lock()

    root: "RootNode | None"
    recent: "ParentNode | None"
    queue: list[
        tuple[
            Literal["root", "parent", "child"],
            "RootNode | ParentNode | ChildNode",
        ]
    ]

    def __new__(cls, *args: Any, **kwargs: Any) -> "Tree":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.root = None
                    cls._instance.recent = None
                    cls._instance.queue = []
        return cls._instance

    def __init__(self) -> None:
        """Initialize a new `Tree` instance."""

    def __copy__(self) -> "Tree":
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> "Tree":
        return self

    def __reduce__(self) -> tuple[type["Tree"], tuple[()]]:
        return (self.__class__, ())

    def register_root(self, node: "RootNode") -> None:
        """
        Queue the root node for registration and build the tree.

        In decorator systems, the root is called last, so we can
        build the tree when it's registered.

        Args:
            node (RootNode):
                The node to register as the root node for the tree.
        """
        self.queue.append(("root", node))

        for node_type, node_ins in reversed(self.queue):
            if node_type == "root":
                if self.root is not None:
                    raise RootNodeExistsError

                self.root = cast("RootNode", node_ins)
            elif node_type == "parent":
                if self.root is None:
                    raise NoRootError

                if self.root.get(node_ins.name) is not None:
                    raise ParentNodeExistsError(node_ins.name)

                self.recent = cast("ParentNode", node_ins)
                self.root[node_ins.name] = node_ins
            elif node_type == "child":
                if self.root is None:
                    raise NoRootError

                if self.recent is None:
                    raise NoParentError

                name = self.recent.name
                index = len(self.root[name])
                self.root[name].children[index] = cast("ChildNode", node_ins)

        self.queue.clear()

    def register_parent(self, node: "ParentNode") -> None:
        """
        Queue a parent node for registration.

        In decorator systems, parents are called before their root but
        need to be built after the root exists.

        Args:
            node (ParentNode):
                The parent node to register to the tree.
        """
        self.queue.append(("parent", node))

    def register_child(self, node: "ChildNode") -> None:
        """
        Queue a child node for registration.

        In decorator systems, children are called before their parent but
        need to be built after the parent exists.

        Args:
            node (ChildNode):
                The `ChildNode` to add to the `ParentNode` instance.
        """
        self.queue.append(("child", node))

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
