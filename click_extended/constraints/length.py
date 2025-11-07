"""Decorator for validating the length of a string."""

# pylint: disable=redefined-builtin

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

    def after_single(self, value: Any, ctx: Context) -> Any:
        """Validate the length of a string value."""
        if not isinstance(value, str):
            ctx.add_failure(value, "Value must be a string")
            return value

        if not self.min <= len(value) <= self.max:
            ctx.add_failure(
                value,
                f"Must be between {self.min} and {self.max} characters long",
            )
            return value

        return value


def length(min: int, max: int) -> Callable[[Any], Any]:
    """Create a Length constraint decorator."""
    return Length.decorator(min=min, max=max, cls=Length)  # type: ignore[return-value]
