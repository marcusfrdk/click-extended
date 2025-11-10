"""The node used as a root node."""

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from click_extended.core._node import Node
from click_extended.core._tree import tree
from click_extended.errors import NoRootError

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode

P = ParamSpec("P")
T = TypeVar("T")


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

    @classmethod
    def as_decorator(
        cls, name: str, /, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the root node.

        The root node is the top-level decorator that triggers tree building
        and collects values from all parent nodes. When the decorated function
        is called, it injects parent node values as keyword arguments.

        Args:
            name (str):
                The name of the root node (e.g., command or group name).
            *args (Any):
                Additional positional arguments for the specific root type.
            **kwargs (Any):
                Additional keyword arguments for the specific root type.

        Returns:
            Callable:
                A decorator function that registers the root node and
                builds the tree.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            instance = cls(name=name)
            tree.register_root(instance)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Wrapper that collects parent values and injects them."""
                parent_values: dict[str, Any] = {}

                if tree.root is None:
                    raise NoRootError

                for parent_name, parent_node in tree.root.children.items():
                    if isinstance(parent_name, str):
                        parent_values[parent_name] = parent_node.get_value()

                merged_kwargs: dict[str, Any] = {**call_kwargs, **parent_values}

                return func(*call_args, **merged_kwargs)

            return wrapper

        return decorator
