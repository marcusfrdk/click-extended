"""A node used for managing child nodes."""

# pylint: disable=redefined-builtin
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import asyncio
from abc import ABC
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar, cast

from click_extended.core._node import Node
from click_extended.core._tree import queue_parent
from click_extended.utils.process import process_children

if TYPE_CHECKING:
    from click_extended.core._child_node import ChildNode
    from click_extended.core._root_node import RootNode

P = ParamSpec("P")
T = TypeVar("T")


class ParentNode(Node, ABC):
    """A node used for managing child nodes."""

    parent: "RootNode"

    def __init__(
        self,
        name: str,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
    ):
        """
        Initialize a new `ParentNode` instance.

        Args:
            name (str):
                The name of the node (parameter name for injection).
            help (str, optional):
                Help text for this parameter. If not provided,
                may use function's docstring.
            required (bool):
                Whether this parameter is required. Defaults to False.
            default (Any):
                Default value if not provided. Defaults to `None`.
            tags (str | list[str], optional):
                Tag(s) to associate with this parameter for grouping.
                Can be a single string or list of strings.
        """
        super().__init__(name=name)
        self.children = {}
        self.help = help
        self.required = required
        self.default = default

        if tags is None:
            self.tags: list[str] = []
        elif isinstance(tags, str):
            self.tags = [tags]
        else:
            self.tags = list(tags)

        self._raw_value: Any = None
        self._raw_value_set: bool = False
        self._cached_value: Any = None
        self._value_computed: bool = False
        self._was_provided: bool = False

    @property
    def children(
        self,
    ) -> dict[str | int, "ChildNode"]:
        """Get the children with proper ChildNode typing."""
        return cast(dict[str | int, "ChildNode"], self._children)

    @children.setter
    def children(self, value: dict[str | int, Node] | None) -> None:
        """Set the children storage."""
        self._children = value

    @classmethod
    def as_decorator(
        cls, **config: Any
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the parent node.

        All configuration parameters are passed through to the
        subclass's __init__ method.

        Args:
            **config (Any):
                Configuration parameters specific to the `ParentNode` subclass.

        Returns:
            Callable:
                A decorator function that registers the parent node.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            instance = cls(**config)
            queue_parent(instance)

            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapper(
                    *call_args: P.args, **call_kwargs: P.kwargs
                ) -> T:
                    """Async wrapper that preserves the original function."""
                    result = await func(*call_args, **call_kwargs)
                    return cast(T, result)

                return cast(Callable[P, T], async_wrapper)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Wrapper that preserves the original function."""
                return func(*call_args, **call_kwargs)

            return wrapper

        return decorator

    def set_raw_value(self, value: Any, was_provided: bool = False) -> None:
        """
        Set the raw value from the source.

        This method is called by RootNode to set the value retrieved
        from Click or other sources.

        Args:
            value (Any):
                The raw value from the source (Click context, env var, etc.).
            was_provided (bool):
                Whether the user explicitly provided this value
                (as opposed to using the default).
        """
        self._raw_value = value
        self._raw_value_set = True
        self._was_provided = was_provided
        self._value_computed = False
        self._cached_value = None

    def was_provided(self) -> bool:
        """
        Check if the user explicitly provided this value.

        Returns:
            bool:
                `True` if the value was explicitly provided by the user,
                `False` if it's using the default value.
        """
        return self._was_provided

    def get_raw_value(self) -> Any:
        """
        Get the raw value from the source (`click.Argument`, `click.Option`,
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
        Get the processed value of the `ParentNode`.

        Processes the raw value through the chain of children and returns
        the processed value. Results are cached after first computation.

        Returns:
            Any:
                The processed value of the chain of children.
        """
        if not self._value_computed:
            if self._raw_value_set:
                raw_value = self._raw_value
            else:
                raw_value = self.get_raw_value()

            assert self.children is not None
            self._cached_value = process_children(
                raw_value, self.children, self
            )
            self._value_computed = True
        return self._cached_value
