"""Hook called on errors."""

# pylint: disable=keyword-arg-before-vararg

from __future__ import annotations

from typing import Callable, TypeGuard, overload

from click_extended.hooks.exception_types import ExceptionFilter, ExceptionType
from click_extended.hooks.hook_handler import HookHandler
from click_extended.hooks.hook_node import HookNode
from click_extended.hooks.hook_phase import HookPhase
from click_extended.hooks.hook_registry import get_registry


@overload
def on_error(
    handler: HookHandler,
    *exc: ExceptionType,
    include: ExceptionFilter = None,
    exclude: ExceptionFilter = None,
) -> HookNode: ...


@overload
def on_error(  # type: ignore
    *exc: ExceptionType,
    include: ExceptionFilter = None,
    exclude: ExceptionFilter = None,
) -> Callable[[HookHandler], HookHandler]: ...


def on_error(
    handler: HookHandler | ExceptionType | None = None,
    *exc: ExceptionType,
    include: ExceptionFilter = None,
    exclude: ExceptionFilter = None,
) -> HookNode | Callable[[HookHandler], HookHandler]:
    """
    Register a hook to run on errors.

    This supports both direct calls and decorator usage.

    :param handler: The error hook handler.
    :param exc: Optional positional exception types to include.
    :param include: Whitelist of exception types to include.
    :param exclude: Blacklist of exception types to exclude.
    :returns: The registered hook node or a decorator.
    """
    registry = get_registry()

    def is_exception_type(
        value: HookHandler | ExceptionType | None,
    ) -> TypeGuard[ExceptionType]:
        return isinstance(value, type) and issubclass(value, BaseException)

    def normalize_exception_types(
        value: ExceptionFilter, label: str
    ) -> tuple[ExceptionType, ...] | None:
        if value is None:
            return None

        if isinstance(value, type) and issubclass(value, BaseException):
            return (value,)

        if isinstance(value, (list, tuple, set)):
            types: list[ExceptionType] = []
            for item in value:
                if not isinstance(item, type) or not issubclass(
                    item, BaseException
                ):
                    raise TypeError(
                        f"{label} must contain exception types, got: {item!r}"
                    )
                types.append(item)
            return tuple(types)

        raise TypeError(
            f"{label} must be an exception type or iterable of types"
        )

    if handler is None or is_exception_type(handler):
        exc_types_raw = ((handler,) + exc) if handler is not None else exc

        def decorator(func: HookHandler) -> HookHandler:
            exc_types = (
                normalize_exception_types(exc_types_raw, "exc")
                if exc_types_raw
                else None
            )
            include_types = normalize_exception_types(include, "include")
            exclude_types = normalize_exception_types(exclude, "exclude")

            if exc_types is not None:
                if include_types is None:
                    include_types = exc_types
                else:
                    include_types = tuple((*include_types, *exc_types))

            registry.register(
                HookPhase.ERROR,
                func,
                scope=None,
                include=include_types,
                exclude=exclude_types,
            )
            return func

        return decorator

    exc_types = normalize_exception_types(exc, "exc") if exc else None
    include_types = normalize_exception_types(include, "include")
    exclude_types = normalize_exception_types(exclude, "exclude")

    if exc_types is not None:
        if include_types is None:
            include_types = exc_types
        else:
            include_types = tuple((*include_types, *exc_types))

    return registry.register(
        HookPhase.ERROR,
        handler,
        scope=None,
        include=include_types,
        exclude=exclude_types,
    )
