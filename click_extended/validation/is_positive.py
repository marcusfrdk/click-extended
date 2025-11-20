"""Validation child for checking if a value is positive."""

from typing import Any, Callable, ParamSpec, TypeVar

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.errors import ValidationError

P = ParamSpec("P")
T = TypeVar("T")


class IsPositive(ChildNode):
    """Validation child for checking if a value is positive."""

    def process(self, value: int | float, context: ProcessContext) -> None:
        if value <= 0:
            raise ValidationError(f"{value} is not positive")


def is_positive(
    *args: Any, **kwargs: Any
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Validation decorator to check if a value is positive."""
    return IsPositive.as_decorator(*args, **kwargs)
