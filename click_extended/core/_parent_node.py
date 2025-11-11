"""A node used for managing child nodes."""

import asyncio
from abc import ABC
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar, cast

from click_extended.core._node import Node
from click_extended.core._tree import queue_parent

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
                Default value if not provided. Defaults to None.
        """
        super().__init__(name=name)
        self.children = {}
        self.help = help
        self.required = required
        self.default = default

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
                Configuration parameters specific to the ParentNode subclass.

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

            else:

                @wraps(func)
                def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                    """Wrapper that preserves the original function."""
                    return func(*call_args, **call_kwargs)

                return wrapper

        return decorator

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
        assert self.children is not None
        all_children = [
            cast("ChildNode", child) for child in self.children.values()
        ]

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
