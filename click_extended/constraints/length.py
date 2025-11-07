"""Decorator for validating the length of a string."""

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
        if not isinstance(value, str):
            raise TypeError("Value must be a string.")
        if not (self.min <= len(value) <= self.max):
            raise ValueError(
                f"Value must be between {self.min} and {self.max} characters long."
            )
        return value


def length(min: int, max: int) -> Length:
    """Create a Length constraint decorator."""
    return Length.decorator(min=min, max=max, cls=Length)
