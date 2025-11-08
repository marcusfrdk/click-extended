"""Representation of a main node."""

from abc import ABC
from collections.abc import Callable
from typing import Any, TypeVar

from click_extended.core._context import Context
from click_extended.errors import ExecutionError

F = TypeVar("F", bound=Callable[..., Any])


class Main(ABC):  # noqa: B024
    """
    Representation of a main node (Command/Group).

    Main nodes create the context and orchestrate execution of the
    decorator chain. They do not execute logic themselves.
    """

    def __init__(self) -> None:
        """Initialize a new Main instance."""
        self.context = Context()
        self.parents: list[Any] = []
        self.func: Callable[..., Any] = lambda: None

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

        # Handle Env parents - inject environment variables into kwargs
        from click_extended.core.env import Env

        for parent in self.parents:
            if isinstance(parent, Env):
                env_value = parent.get_env_value()
                injection_key = parent.get_injection_key()
                # Only inject if not already present in kwargs
                if injection_key not in kwargs:
                    kwargs[injection_key] = env_value
                parent.value = env_value

        # Handle other parents - extract values from kwargs
        for parent in self.parents:
            if not isinstance(parent, Env) and parent.name:
                param_name = parent.name.lstrip("-").replace("-", "_")
                if param_name in kwargs:
                    parent.value = kwargs[param_name]
            parent.execute(self.context)

        if self.context.failures:
            raise ExecutionError(self.context.failures)

        result = self.func(*args, **kwargs)

        return result

    def add_parent(self, parent: Any) -> None:
        """Register a parent node with this main node."""
        self.parents.append(parent)
