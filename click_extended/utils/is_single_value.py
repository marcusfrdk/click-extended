"""Check if the value passed to the `process()` method is a single value."""

from datetime import datetime
from pathlib import Path
from typing import TypeGuard, TypeVar, overload

T = TypeVar("T", str, int, float, bool)


@overload
def is_single_value(  # type: ignore
    value: object,
    expected_type: type[str],
) -> TypeGuard[str]: ...


@overload
def is_single_value(  # type: ignore
    value: object,
    expected_type: type[int],
) -> TypeGuard[int]: ...


@overload
def is_single_value(  # type: ignore
    value: object, expected_type: type[float]
) -> TypeGuard[float]: ...


@overload
def is_single_value(  # type: ignore
    value: object, expected_type: type[bool]
) -> TypeGuard[bool]: ...


@overload
def is_single_value(  # type: ignore
    value: object, expected_type: tuple[type[int], type[float]]
) -> TypeGuard[int | float]: ...


@overload
def is_single_value(  # type: ignore
    value: object, expected_type: tuple[type[str], type[Path]]
) -> TypeGuard[str | Path]: ...


@overload
def is_single_value(  # type: ignore
    value: object, expected_type: tuple[type[str], type[datetime]]
) -> TypeGuard[str | datetime]: ...


def is_single_value(  # type: ignore
    value: object,
    expected_type: type[T] | tuple[type[T], ...],
) -> bool:
    """
    Check if the value passed to the `process()` method is a single value.

    Args:
        value (object):
            The value to check.
        expected_type (type[T] | tuple[type[T], ...]):
            Specific type or tuple of types to check for
            (str, int, float, or bool).

    Returns:
        bool:
            Whether the value is a single value or not.
    """
    return isinstance(value, expected_type)
