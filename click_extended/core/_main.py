"""Representation of a main node."""

from abc import ABC
from typing import Any, Callable, TypeVar

from click_extended.core._context import Context

F = TypeVar("F", bound=Callable[..., Any])


class Main(ABC):
    """
    Representation of a main node (Command/Group).

    Main nodes create the context and orchestrate execution of the decorator chain.
    They do not execute logic themselves.
    """

    def __init__(self) -> None:
        """Initialize a new Main instance."""
        self.context = Context()
        self.parents: list[Any] = []
        self.func: Callable[..., Any] | None = None

    def add_parent(self, parent: Any) -> None:
        """Register a parent node with this main node."""
        self.parents.append(parent)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the decorated function with the decorator chain."""
        if self.func is None:
            raise RuntimeError("No function registered with this main node")

        self.context.main.update(
            {
                "function": self.func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
        )

        for parent in self.parents:
            parent.execute(self.context)

        result = self.func(*args, **kwargs)

        return result
