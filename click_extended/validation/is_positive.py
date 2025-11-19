"""Validation child for checking if a value is positive."""

from typing import Any, Callable, ParamSpec, TypeVar

from click_extended.core._child_node import ChildNode, ProcessContext

ERROR_MESSAGE = "Value of '{}' must be positive, got {}"

P = ParamSpec("P")
T = TypeVar("T")


class IsPositive(ChildNode):
    """Validation child for checking if a value is positive."""

    types = [int, float]

    def process(
        self, value: int | float | None, context: ProcessContext
    ) -> None:
        if value is None:
            return

        if value <= 0:
            raise ValueError(ERROR_MESSAGE.format(context.parent.name, value))


def is_positive(
    *args: Any, **kwargs: Any
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Validation decorator to check if a value is positive."""
    return IsPositive.as_decorator(*args, **kwargs)
