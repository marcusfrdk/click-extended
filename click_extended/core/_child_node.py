"""The node used as a child node.."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

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

    def __init__(
        self,
        name: str,
        process_args: tuple[Any, ...] | None = None,
        process_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a new `ChildNode` instance.

        Args:
            name (str):
                The name of the node.
            process_args (tuple):
                Positional arguments to pass to the process method.
            process_kwargs (dict[str, Any]):
                Keyword arguments to pass to the process method.
        """
        super().__init__(name=name, children=None)
        self.children = None
        self.process_args = process_args or ()
        self.process_kwargs = process_kwargs or {}

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
    def as_decorator(
        cls, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Return a decorator representation of the child node.

        The provided args and kwargs are stored and later passed to the
        process method when called by the `ParentNode`.

        Args:
            *args (Any):
                Positional arguments to pass to the process method.
            **kwargs (Any):
                Keyword arguments to pass to the process method.

        Returns:
            Callable:
                A decorator function that registers the child node.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """The actual decorator that wraps the function."""
            name = Transform(cls.__name__).to_snake_case()
            instance = cls(name=name, process_args=args, process_kwargs=kwargs)
            queue_child(instance)
            return func

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
