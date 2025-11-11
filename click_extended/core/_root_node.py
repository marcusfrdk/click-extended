"""The node used as a root node."""

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar, cast

from click_extended.core._node import Node
from click_extended.core._tree import Tree
from click_extended.errors import NoRootError

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode

P = ParamSpec("P")
T = TypeVar("T")
WrapperType = TypeVar("WrapperType")


class RootNodeWrapper:
    """
    Base wrapper class that provides visualize()
    method for all RootNode types.
    """

    def __init__(self, instance: "RootNode") -> None:
        """
        Initialize the wrapper.

        Args:
            instance: The RootNode instance to wrap.
        """
        self._root_instance = instance

    def visualize(self) -> None:
        """Visualize the tree structure."""
        self._root_instance.visualize()


class RootNode(Node):
    """The node used as a root node."""

    parent: None
    children: dict[str | int, "ParentNode"]
    tree: Tree

    def __init__(self, name: str) -> None:
        """
        Initialize a new `RootNode` instance.

        Args:
            name (str):
                The name of the node.
        """
        super().__init__(name=name, level=1)
        self.tree = Tree()

    @classmethod
    def as_decorator(
        cls, name: str | None = None, /, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Any]:
        """
        Return a decorator representation of the root node.

        The root node is the top-level decorator that triggers tree building
        and collects values from all parent nodes. When the decorated function
        is called, it injects parent node values as keyword arguments.

        Args:
            name (str, optional):
                The name of the root node. If None, uses the decorated
                function's name.
            **kwargs (Any):
                Additional keyword arguments for the specific root type.

        Returns:
            Callable:
                A decorator function that registers the root node
                and builds the tree.
        """

        def decorator(func: Callable[..., Any]) -> Any:
            """The actual decorator that wraps the function."""
            node_name = name if name is not None else func.__name__
            instance = cls(name=node_name, **kwargs)
            instance.tree.register_root(instance)

            @wraps(func)
            def wrapper(*call_args: Any, **call_kwargs: Any) -> Any:
                """Wrapper that collects parent values and injects them."""
                parent_values: dict[str, Any] = {}

                if instance.tree.root is None:
                    raise NoRootError

                for (
                    parent_name,
                    parent_node,
                ) in instance.tree.root.children.items():
                    if isinstance(parent_name, str):
                        parent_values[parent_name] = parent_node.get_value()

                merged_kwargs: dict[str, Any] = {**call_kwargs, **parent_values}

                return func(*call_args, **merged_kwargs)

            return cls.wrap(wrapper, node_name, instance, **kwargs)

        return decorator

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: "RootNode",
        **kwargs: Any,
    ) -> Any:
        """
        Hook for subclasses to apply additional wrapping after value injection.

        By default, returns the wrapped function unchanged. Subclasses can
        override this to add custom behavior (e.g., click.command wrapping).

        Args:
            wrapped_func (Callable):
                The function already wrapped with value injection.
            name (str):
                The name of the root node.
            instance (RootNode):
                The RootNode instance that owns this tree.
            **kwargs (Any):
                Additional keyword arguments passed to `as_decorator`.

        Returns:
            Any:
                The wrapped result. Subclasses determine the actual type.
        """
        func_with_visualize = cast(Any, wrapped_func)
        func_with_visualize.visualize = instance.visualize
        return func_with_visualize

    def visualize(self) -> None:
        """Visualize the tree structure."""
        if self.tree.root is None:
            raise NoRootError

        print(self.tree.root.name)
        for parent in self.tree.root.children.values():
            print(f"  {parent.name}")
            for child in parent.children.values():
                print(f"    {child.name}")
