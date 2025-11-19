"""The node used as a child node.."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-few-public-methods

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from click_extended.core._node import Node
from click_extended.core._tree import queue_child
from click_extended.errors import TypeMismatchError
from click_extended.utils.transform import Transform

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode
    from click_extended.core.tag import Tag

P = ParamSpec("P")
T = TypeVar("T")


class ProcessContext:
    """
    Context provided to `ChildNode.process()` containing
    all processing information.
    """

    def __init__(
        self,
        parent: "ParentNode | Tag",
        siblings: list[str],
        tags: dict[str, "Tag"],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """
        Initialize a new ProcessContext instance.

        Args:
            parent (ParentNode | Tag):
                The parent node (ParentNode or Tag) this child is attached to.
            siblings (list[str]):
                List of unique class names of all sibling child nodes.
            tags (dict[str, Tag]):
                Dictionary mapping tag names to Tag instances.
            args (tuple[Any, ...]):
                Additional positional arguments from `as_decorator`.
            kwargs (dict[str, Any]):
                Additional keyword arguments from `as_decorator`.
        """
        self.parent = parent
        self.siblings = siblings
        self.tags = tags
        self.args = args
        self.kwargs = kwargs


class ChildNode(Node, ABC):
    """The node used as a child node."""

    parent: "ParentNode"
    types: list[type] = []

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

    def validate_type(self, parent: "ParentNode") -> None:
        """
        Validate that the parent's type is supported by this child node.

        An empty types list means all types are supported.
        If types list is not empty, the parent's type must be in the list.

        Args:
            parent (ParentNode):
                The parent node to validate against.

        Raises:
            TypeMismatchError:
                If the parent's type is not supported by this child node.
        """

        if not self.types:
            return

        parent_type = getattr(parent, "type", None)

        if parent_type is None:
            return

        if parent_type not in self.types:
            raise TypeMismatchError(
                child_name=self.__class__.__name__,
                parent_name=parent.name,
                parent_type=parent_type,
                supported_types=self.types,
            )

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

    def __getitem__(self, name: str | int) -> Node:
        raise KeyError("A ChildNode instance has no children.")

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
    def process(self, value: Any, context: ProcessContext) -> Any:
        """
        Process the value and return the processed result.

        Args:
            value (Any):
                The value to process (from previous child or parent).
                Subclasses can override the type annotation for value.
            context (ProcessContext):
                Context containing parent, siblings, tags, and decorator args.

        Returns:
            Any:
                The processed value, or None to leave the value unchanged.
        """
        raise NotImplementedError
