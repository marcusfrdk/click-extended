"""Decorator used for debugging functions, decorators and contexts."""

from typing import Any, Callable, TypeVar

from click_extended.core._child import Child
from click_extended.core._context import Context

F = TypeVar("F", bound=Callable[..., Any])


class Debug(Child):
    """Decorator used for debugging functions, decorators and contexts."""

    def before_single(self, value: Any, ctx: Context) -> None:
        print("Before:")
        print(f"Value: {value}")
        print(f"Context: {ctx}")

    def after_single(self, value: Any, ctx: Context) -> Any:
        print("After:")
        print(f"Value: {value}")
        print(f"Context: {ctx}")
        return value


def debug(fn: F | None = None) -> Callable[[F], F] | F:
    """Debugging decorator."""
    return Child.decorator(fn, cls=Debug)
