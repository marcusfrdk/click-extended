"""Child node to convert a string to one of many formats."""

from typing import Any, cast

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.types import Decorator
from click_extended.utils.casing import Casing


class ToCase(ChildNode):
    """Child node to convert a string to one of many formats."""

    def handle_primitive(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return cast(str, getattr(Casing, kwargs["method"])(value))


def to_lower_case() -> Decorator:
    """
    Child node that converts a string to lowercase.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_lower_case")


def to_upper_case() -> Decorator:
    """
    Child node that converts a string to UPPERCASE.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_upper_case")


def to_meme_case() -> Decorator:
    """
    Child node that converts a string to mEmEcAsE.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_meme_case")


def to_snake_case() -> Decorator:
    """
    Child node that converts a string to snake_case.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_snake_case")


def to_screaming_snake_case() -> Decorator:
    """
    Child node that converts a string to SCREAMING_SNAKE_CASE.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_screaming_snake_case")


def to_camel_case() -> Decorator:
    """
    Child node that converts a string to camelCase.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_camel_case")


def to_pascal_case() -> Decorator:
    """
    Child node that converts a string to PascalCase.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_pascal_case")


def to_kebab_case() -> Decorator:
    """
    Child node that converts a string to kebab-case.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_kebab_case")


def to_train_case() -> Decorator:
    """
    Child node that converts a string to Train-Case.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_train_case")


def to_flat_case() -> Decorator:
    """
    Child node that converts a string to flatcase.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_flat_case")


def to_dot_case() -> Decorator:
    """
    Child node that converts a string to dot.case.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_dot_case")


def to_title_case() -> Decorator:
    """
    Child node that converts a string to Title Case.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_title_case")


def to_path_case() -> Decorator:
    """
    Child node that converts a string to path/case.

    Returns:
        Decorator:
            The decorator function.
    """
    return ToCase.as_decorator(method="to_path_case")
