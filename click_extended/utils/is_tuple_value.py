"""Check if the value passed to the `process()` method is a flat tuple."""

from datetime import datetime
from pathlib import Path
from typing import TypeGuard, TypeVar, cast, overload

T = TypeVar("T", str, int, float, bool)


@overload
def is_tuple_value(  # type: ignore
    value: object, expected_type: type[str]
) -> TypeGuard[tuple[str, ...]]: ...


@overload
def is_tuple_value(  # type: ignore
    value: object, expected_type: type[int]
) -> TypeGuard[tuple[int, ...]]: ...


@overload
def is_tuple_value(  # type: ignore
    value: object, expected_type: type[float]
) -> TypeGuard[tuple[float, ...]]: ...


@overload
def is_tuple_value(  # type: ignore
    value: object, expected_type: type[bool]
) -> TypeGuard[tuple[bool, ...]]: ...


@overload
def is_tuple_value(  # type: ignore
    value: object, expected_type: tuple[type[int], type[float]]
) -> TypeGuard[tuple[int | float, ...]]: ...


@overload
def is_tuple_value(  # type: ignore
    value: object, expected_type: tuple[type[str], type[Path]]
) -> TypeGuard[tuple[str | Path, ...]]: ...


@overload
def is_tuple_value(  # type: ignore
    value: object, expected_type: tuple[type[str], type[datetime]]
) -> TypeGuard[tuple[str | datetime, ...]]: ...


def is_tuple_value(  # type: ignore
    value: object,
    expected_type: type[T] | tuple[type[T], ...],
) -> bool:
    """
    Check if the value passed to the `process()` method is a flat tuple.

    Args:
        value (object):
            The value to check.
        expected_type (type[T] | tuple[type[T], ...]):
            Specific type or tuple of types to check for elements
            (str, int, float, or bool).

    Returns:
        bool:
            Whether the value is a flat tuple or not.
    """
    if not isinstance(value, tuple):
        return False

    tuple_value = cast("tuple[object, ...]", value)

    if len(tuple_value) == 0:
        return False

    for item in tuple_value:
        if not isinstance(item, expected_type):
            return False
    return True
