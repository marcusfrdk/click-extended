"""Check if the value is a nested tuple (tuple of tuples)."""

from datetime import datetime
from pathlib import Path
from typing import TypeGuard, TypeVar, cast, overload

T = TypeVar("T", str, int, float, bool)


@overload
def is_nested_tuple_value(  # type: ignore
    value: object, expected_type: type[str]
) -> TypeGuard[tuple[tuple[str, ...], ...]]: ...


@overload
def is_nested_tuple_value(  # type: ignore
    value: object, expected_type: type[int]
) -> TypeGuard[tuple[tuple[int, ...], ...]]: ...


@overload
def is_nested_tuple_value(  # type: ignore
    value: object, expected_type: type[float]
) -> TypeGuard[tuple[tuple[float, ...], ...]]: ...


@overload
def is_nested_tuple_value(  # type: ignore
    value: object, expected_type: type[bool]
) -> TypeGuard[tuple[tuple[bool, ...], ...]]: ...


@overload
def is_nested_tuple_value(  # type: ignore
    value: object, expected_type: tuple[type[int], type[float]]
) -> TypeGuard[tuple[tuple[int | float, ...], ...]]: ...


@overload
def is_nested_tuple_value(  # type: ignore
    value: object, expected_type: tuple[type[str], type[Path]]
) -> TypeGuard[tuple[tuple[str | Path, ...], ...]]: ...


@overload
def is_nested_tuple_value(  # type: ignore
    value: object, expected_type: tuple[type[str], type[datetime]]
) -> TypeGuard[tuple[tuple[str | datetime, ...], ...]]: ...


def is_nested_tuple_value(  # type: ignore
    value: object,
    expected_type: type[T] | tuple[type[T], ...],
) -> bool:
    """
    Check if the value is a nested tuple (tuple of tuples).

    Args:
        value (object):
            The value to check.
        expected_type (type[T] | tuple[type[T], ...]):
            Specific type or tuple of types to check for elements
            (str, int, float, or bool).

    Returns:
        bool:
            Whether the value is a nested tuple or not.
    """
    if not isinstance(value, tuple):
        return False

    tuple_value = cast("tuple[object, ...]", value)

    if len(tuple_value) == 0:
        return False

    for item in tuple_value:
        if not isinstance(item, tuple):
            return False

    for inner_tuple in tuple_value:
        if isinstance(inner_tuple, tuple):
            inner = cast("tuple[object, ...]", inner_tuple)
            for element in inner:
                if not isinstance(element, expected_type):
                    return False

    return True
