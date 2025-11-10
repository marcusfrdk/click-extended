"""The node used as a child node.."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar, overload

from click_extended.core._node import Node
from click_extended.core._tree import queue_child
from click_extended.utils.transform import Transform

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode

P = ParamSpec("P")
T = TypeVar("T")


class ChildNode(Node, ABC):
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

    @classmethod
    @overload
    def as_decorator(cls, func: Callable[P, T], /) -> Callable[P, Any]:
        """Overload for @decorator syntax (without parentheses)."""
        ...

    @classmethod
    @overload
    def as_decorator(
        cls, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Overload for @decorator() or @decorator(*args, **kwargs) syntax."""
        ...

    @classmethod
    def as_decorator(
        cls, *args: Any, **kwargs: Any
    ) -> (
        Callable[..., Any] | Callable[[Callable[..., Any]], Callable[..., Any]]
    ):
        """
        Return a decorator representation of the child node.

        This creates a decorator that supports being called either as
        `@decorator`, `@decorator()`, and `@decorator(*args, **kwargs)`.

        The provided args and kwargs are stored and later passed to the
        process method when called by the `ParentNode`.

        Args:
            *args (Any):
                Positional arguments to pass to the process method.
            **kwargs (Any):
                Keyword arguments to pass to the process method.

        Returns:
            Callable:
                A decorator function or the decorated function
                depending on usage.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """The actual decorator that wraps the function."""
            name = Transform(cls.__name__).to_snake_case()
            instance = cls(name=name)
            queue_child(instance)
            return func

        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return decorator(args[0])

        return decorator

    @abstractmethod
    def process(
        self, value: Any, *args: Any, siblings: list[str], **kwargs: Any
    ) -> Any:
        """
        Process the value of the chain and returns the processed value.

        This method should only be called by the `ParentNode` class.

        Args:
            value (Any):
                The previous value from the chain or directly from the
                `ParentNode`.
            *args (Any):
                Additional positional arguments passed from as_decorator.
            siblings (list[str]):
                A list of unique class names of all sibling child nodes
                in the parent. This is always provided by the ParentNode.
            **kwargs (Any):
                Additional keyword arguments passed from as_decorator.

        Returns:
            Any:
                The processed value.
        """
        raise NotImplementedError
