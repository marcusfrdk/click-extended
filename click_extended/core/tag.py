"""Tag implementation for the `click_extended` library."""

from functools import wraps
from typing import TYPE_CHECKING, Callable, Mapping, ParamSpec, TypeVar, cast

from click_extended.core._node import Node
from click_extended.core._tree import queue_tag

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode
    from click_extended.core._parent_node import ParentNode

P = ParamSpec("P")
T = TypeVar("T")


class Tag(Node):
    """Tag class for grouping multiple ParentNodes together."""

    def __init__(self, name: str):
        """
        Initialize a new `Tag` instance.

        Args:
            name (str):
                The name of the tag for grouping ParentNodes.
        """
        super().__init__(name=name, children={})
        self.parent_nodes: list["ParentNode"] = []

    @property
    def children(self) -> Mapping[str | int, "ChildNode"]:
        return cast(Mapping[str | int, "ChildNode"], self._children)

    @children.setter
    def children(self, value: dict[str | int, "Node"] | None) -> None:
        self._children = value

    def get_provided_values(self) -> list[str]:
        """
        Get the names of all ParentNodes in this tag
        that were provided by the user.

        Returns:
            list[str]:
                List of parameter names that were provided.
        """
        return [node.name for node in self.parent_nodes if node.was_provided()]

    @classmethod
    def as_decorator(
        cls, name: str
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the tag.

        Args:
            name (str):
                The name of the tag.

        Returns:
            Callable:
                A decorator function that registers the tag.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            instance = cls(name=name)
            queue_tag(instance)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Wrapper that preserves the original function."""
                return func(*call_args, **call_kwargs)

            return wrapper

        return decorator


def tag(name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to create a tag for grouping ParentNodes.

    Tags allow you to apply ChildNodes to multiple ParentNodes at once
    and perform cross-node validation.

    Args:
        name (str):
            The name of the tag.

    Returns:
        Callable:
            A decorator function that registers the tag.

    Examples:

        ```python
        @command()
        @option("--api-key", tags="api-config")
        @option("--api-url", tags="api-config")
        @tag("api-config")
        @requires_one()
        def my_func(api_key, api_url):
            print(f"API Key: {api_key}, URL: {api_url}")
        ```
    """
    return Tag.as_decorator(name=name)
