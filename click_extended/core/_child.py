"""Abstract class representing a child node."""

# pylint: disable=unused-argument

from abc import ABC
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from click_extended.core._context import Context

F = TypeVar("F", bound=Callable[..., Any])


class Child(ABC):
    """Abstract class representing a child node.

    Children process values through a context-aware pipeline with optional
    before/after hooks for transformations and side effects.
    """

    def before(self, value: Any, ctx: Context) -> None:
        """Hook called before the decorated function executes."""

    def after(self, value: Any, ctx: Context) -> Any:
        """Hook called after the decorated function executes."""
        return value

    def __call__(self, fn: F) -> F:
        """Apply the decorator to a function."""

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrap the function with before/after hooks."""
            ctx = Context()  # Currently just a placeholder
            self.before(args, ctx)
            result = fn(*args, **kwargs)
            return self.after(result, ctx)

        return cast(F, wrapper)

    @staticmethod
    def decorator(
        fn: Optional[F] = None,
        *,
        cls: type,
        **default_kwargs: Any,
    ) -> Callable[[F], F] | F:
        """Create a decorator for the class."""

        def wrapper(func: F) -> F:
            """Wrap the function with the decorator class."""
            instance = cls(**default_kwargs)
            return instance(func)

        if fn is None:
            return wrapper
        return wrapper(fn)
