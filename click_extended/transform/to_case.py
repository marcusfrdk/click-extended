"""A decorator for transforming a string into multiple formats."""

from typing import cast

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.errors import UnhandledValueError
from click_extended.types import Decorator
from click_extended.utils import (
    Transform,
    is_nested_tuple_value,
    is_single_value,
    is_tuple_value,
)


class Factory(ChildNode):
    """Base class for constructing transformation decorators."""

    def process(
        self,
        value: str | tuple[str, ...] | tuple[tuple[str, ...], ...],
        context: ProcessContext,
    ) -> str | tuple[str, ...] | tuple[tuple[str, ...], ...]:
        def transform(v: str) -> str:
            return cast(str, getattr(Transform(v), context.kwargs["method"])())

        if is_single_value(value, str):
            return transform(value)
        if is_tuple_value(value, str):
            return tuple(transform(v) for v in value)
        if is_nested_tuple_value(value, str):
            return tuple(tuple(transform(v) for v in t) for t in value)

        raise UnhandledValueError(value)


def to_upper_case() -> Decorator:
    """
    Convert a value to UPPER CASE.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_upper_case")


def to_lower_case() -> Decorator:
    """
    Convert a value to lower case.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_lower_case")


def to_meme_case() -> Decorator:
    """
    Convert a value to mEmE cAsE.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_meme_case")


def to_snake_case() -> Decorator:
    """
    Convert a value to snake_case.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_snake_case")


def to_screaming_snake_case() -> Decorator:
    """
    Convert a value to SCREAMING_SNAKE_CASE.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_screaming_snake_case")


def to_camel_case() -> Decorator:
    """
    Convert a value to camelCase.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_camel_case")


def to_pascal_case() -> Decorator:
    """
    Convert a value to PascalCase.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_pascal_case")


def to_kebab_case() -> Decorator:
    """
    Convert a value to kebab-case.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_kebab_case")


def to_train_case() -> Decorator:
    """
    Convert a value to Train-Case.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_train_case")


def to_flat_case() -> Decorator:
    """
    Convert a value to flatcase.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_flat_case")


def to_dot_case() -> Decorator:
    """
    Convert a value to dot.case.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_dot_case")


def to_title_case() -> Decorator:
    """
    Convert a value to Title Case.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_title_case")


def to_path_case() -> Decorator:
    """
    Convert a value to path/case.

    Supports `str`, `tuple[str]` and `tuple[tuple[str]]`.

    Returns:
        Decorator:
            The decorated function.
    """
    return Factory.as_decorator(method="to_path_case")
