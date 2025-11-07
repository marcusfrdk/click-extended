"""Decorator used for debugging functions, decorators and contexts."""

from collections.abc import Callable
from typing import Any, TypeVar

from click_extended.core._child import Child
from click_extended.core._context import Context

F = TypeVar("F", bound=Callable[..., Any])


class Debug(Child):
    """Decorator used for debugging functions, decorators and contexts."""

    def after_single(self, value: Any, ctx: Context) -> Any:
        print(ctx)
        return value


def debug(fn: F | None = None) -> Callable[[F], F] | F:
    """Debugging decorator."""
    return Child.decorator(fn, cls=Debug)
