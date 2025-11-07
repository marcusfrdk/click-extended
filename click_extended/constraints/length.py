"""Decorator for validating the length of a string."""

from collections.abc import Callable
from typing import Any

from click_extended.core._child import Child
from click_extended.core._context import Context


class Length(Child):
    """Decorator for validating the length of a string."""

    def __init__(self, min: int, max: int):
        """Initialize a new `Length` constraint decorator."""
        self.min = min
        self.max = max

    def after_single(self, value: Any, ctx: Context) -> Any:  # noqa: ARG002
        print("Running length", value)
        if not isinstance(value, str):
            raise TypeError("Value must be a string.")
        if not self.min <= len(value) <= self.max:
            raise ValueError(
                f"Value must be between {self.min} and {self.max} characters long."
            )
        return value


def length(min: int, max: int) -> Callable[[Any], Any]:
    """Create a Length constraint decorator."""
    return Length.decorator(min=min, max=max, cls=Length)  # type: ignore[return-value]
