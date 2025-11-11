"""A node used for managing child nodes."""

from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from click_extended.core._child_node import ChildNode
from click_extended.core._node import Node
from click_extended.core._tree import queue_parent

if TYPE_CHECKING:
    from click_extended.core._root_node import RootNode

P = ParamSpec("P")
T = TypeVar("T")


class ParentNode(Node, ABC):
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

    @classmethod
    def as_decorator(
        cls, name: str, /, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the parent node.

        Unlike `ChildNode`, `ParentNode` requires a name to be specified,
        which identifies the argument/option/environment variable.

        Args:
            name (str):
                The name of the parent node (e.g., "username",
                "port", "API_KEY").

        Returns:
            Callable:
                A decorator function that registers the parent node.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            instance = cls(name=name)
            queue_parent(instance)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Wrapper that preserves the original function."""
                return func(*call_args, **call_kwargs)

            return wrapper

        return decorator

    @abstractmethod
    def get_raw_value(self) -> Any:
        """
        Get the raw value from the source (click.Argument, click.Option,
        env, etc.).

        This method must be implemented by subclasses to retrieve the value
        from their specific source (e.g. command-line arguments, options,
        environment variables, etc.).

        Returns:
            Any:
                The raw value from the source before processing.
        """
        raise NotImplementedError

    def get_value(self) -> Any:
        """
        Get the raw value of the `ParentNode` and process it through the
        chain of children and return the processed value.

        Returns:
            Any:
                The processed value of the chain of children.
        """
        value = self.get_raw_value()
        all_children = list(self.children.values())

        for child in all_children:
            siblings = list(
                {
                    c.__class__.__name__
                    for c in all_children
                    if id(c) != id(child)
                }
            )

            value = child.process(
                value,
                *child.process_args,
                siblings=siblings,
                **child.process_kwargs,
            )

        return value
