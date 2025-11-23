"""GlobalNode class for tree-level observation and injection."""

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Literal, ParamSpec, TypeVar

from click_extended.core._tree import Tree
from click_extended.core.context import Context
from click_extended.core.node import Node

P = ParamSpec("P")
T = TypeVar("T")


class GlobalNode(Node, ABC):
    """
    A node that executes at the tree level either pre- or post initialization.
    for observation or value injection but cannot have attached children.

    To inject values into the function, the node must have a set name
    (`name="my_name"`), and will be directly passed to the function as the
    keyword argument as that name. If name is not set, only observation will be
    performed.

    All nodes have access to an internal data store under `context.data`, which
    is a plain dictionary, allowing you to share data between nodes.
    """

    def __init__(
        self,
        name: str | None = None,
        run: Literal["first", "last"] = "first",
    ) -> None:
        """
        Initialize a new `GlobalNode` instance.

        Args:
          name (str | None, optional):
            The parameter name to inject the return value into.
            If `None`, runs in observer mode (no injection).
          run (Literal["first", "last"]):
            When to execute this global node:
            - `"first"`: Before all parent/child processing (default)
            - `"last"`: After all parent/child processing, before function call
        """
        internal_name = name if name is not None else f"_global_{id(self)}"
        super().__init__(name=internal_name, children=None)

        self.inject_name = name
        self.run = run

    @abstractmethod
    def handle(self, context: "Context") -> Any:
        """
        Execute the global node logic.

        This method is called at the appropriate point in the tree lifecycle
        based on the `phase` setting.

        Args:
            context (Context):
                The processing context containing access to all nodes,
                data store, and debug settings.

        Returns:
            Any:
                If `name` is set, this value will be injected into the function
                (including `None`). If `name` is `None`, the return value
                is ignored.
        """
        raise NotImplementedError

    @classmethod
    def as_decorator(
        cls,
        name: str | None = None,
        run: Literal["first", "last"] = "first",
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the global node.

        Args:
            name (str | None, optional):
                The parameter name to inject the return value into.
                If `None`, runs in observer mode.
            run (Literal["first", "last"], required):
                When to execute this global node.
                - `"first"`: Before all parent/child processing
                - `"last"`: After all parent/child processing

        Returns:
            Decorator:
                A decorator function that registers the global node.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            instance = cls(name=name, run=run)
            Tree.queue_global(instance)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Wrapper that preserves the original function."""
                return func(*call_args, **call_kwargs)

            return wrapper

        return decorator


__all__ = ["GlobalNode"]
