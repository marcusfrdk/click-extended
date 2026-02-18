"""ChildNode class for handler-based value processing."""

# pylint: disable=too-many-public-methods

from abc import ABC
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable
from uuid import UUID

from click_extended.core.nodes.node import Node
from click_extended.core.other._tree import Tree
from click_extended.core.other.context import Context
from click_extended.utils.casing import Casing

if TYPE_CHECKING:
    from click_extended.types import Decorator


class ChildNode(Node, ABC):
    """
    Base class for child nodes with type-specific handlers. Child nodes
    process values through handler methods based on value type.

    Handlers operate on a priority system with specificity deciding the order.
    For example, `handle_flat_tuple` takes priority over `handle_tuple` which in
    turn takes priority over `handle_all`.

    All handlers are optional. Override only the handlers you need.
    Returning None (or no return) passes the value through unchanged and makes
    that type validation-only.

    If a value is passed to the child in which it has not implemented a
    relevant handler, an `UnhandledTypeError` exception is raised.
    """

    def __init__(
        self,
        name: str,
        process_args: tuple[Any, ...] | None = None,
        process_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        r"""
        Initialize a new ``ChildNode`` instance.

        :param name: The name of the node.
        :param process_args: Positional arguments to pass to handler
            methods.
        :param process_kwargs: Keyword arguments to pass to handler
            methods.
        :param \*\*kwargs: Additional keyword arguments for multiple
            inheritance.
        """
        children = kwargs.pop("children", None)
        super().__init__(name=name, children=children, **kwargs)
        self.process_args = process_args or ()
        self.process_kwargs = process_kwargs or {}

    def handle_none(self, context: "Context", *args: Any, **kwargs: Any) -> Any:
        r"""
        Handle None values explicitly.

        Called when value is ``None`` before any other handler.
        If not implemented, ``None`` values are auto-skipped.

        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: The processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_all(
        self, value: Any, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle all value types. Called as fallback if no
        specific handler is implemented.

        Also catches ``None`` values if ``handle_none`` is not implemented.

        :param value: The value to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or None to pass through unchanged.
        """
        raise NotImplementedError

    def handle_str(
        self, value: str, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle string values.

        :param value: The string value to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_int(
        self, value: int, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle integer values.

        :param value: The integer value to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_float(
        self, value: float, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle float values.

        :param value: The float value to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_bool(
        self, value: bool, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle boolean values.

        :param value: The boolean value to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_numeric(
        self, value: int | float, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle numeric values (int or float).

        This is a union handler that works with both integers and floats.
        Use this when your decorator logic applies to all numeric types.

        :param value: The numeric value to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_date(
        self, value: date, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle date objects (datetime.date).

        :param value: The date object to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_time(
        self, value: time, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle time objects (datetime.time).

        :param value: The time object to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_tuple(
        self,
        value: tuple[Any, ...],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        r"""
        Handle any tuple structure (fallback).

        Called when:

            - `handle_flat_tuple` not implemented and the tuple is flat
            - `handle_nested_tuple` not implemented and the tuple is nested
            - Tuple has mixed primitive and complex types

        Use this when you want to handle all tuple types with the same logic,
        or when you need to handle mixed-type tuples.

        Examples:

            - ``(1, 2, 3)`` if ``handle_flat_tuple`` not implemented
            - ``((1, 2),)`` if ``handle_nested_tuple`` not implemented
            - ``(1, [2, 3], "hello")``: mixed types (only option)

        :param value: The tuple to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_list(
        self,
        value: list[Any],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        r"""
        Handle list values.

        :param value: The list to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_dict(
        self,
        value: dict[Any, Any],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        r"""
        Handle dictionary values.

        :param value: The dictionary to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_tag(
        self,
        value: dict[str, Any],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        r"""
        Handle values from a ``Tag`` parent.

        Called when the parent node is a ``Tag``. The value is a dictionary
        mapping parameter names to their values from all parent nodes
        (``Option``, ``Argument``, ``Env``, etc.) that reference this tag.

        Can be implemented as sync or async. This handler is validation-only
        and must not return a value (or return None).

        :param value: Dictionary mapping parameter names to values from
            all parent nodes referencing this tag. Keys are parent
            node names (e.g., "username"), values are ``None`` if not
            provided by the user.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Must return None (validation-only).
        :rtype: None
        """
        raise NotImplementedError

    def handle_datetime(
        self,
        value: datetime,
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        r"""
        Handle datetime objects (datetime.datetime).

        :param value: The datetime object to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_uuid(
        self, value: UUID, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle UUID objects.

        :param value: The UUID object to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_path(
        self, value: Path, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle Path objects.

        :param value: The Path object to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_bytes(
        self, value: bytes, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle bytes objects.

        :param value: The bytes object to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_decimal(
        self, value: Decimal, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        r"""
        Handle Decimal objects.

        :param value: The Decimal object to process.
        :param context: Information about the current context.
        :param \*args: Additional positional arguments from decorator.
        :param \*\*kwargs: Additional keyword arguments from decorator.

        :returns: Processed value, or ``None`` to pass through unchanged.
        """
        raise NotImplementedError

    def get(self, _name: str) -> None:
        """
        The ChildNode has no children, thus this method returns None.

        :param _name: The name of the child.

        :returns: Always returns None as the ChildNode has no children.
        :rtype: None
        """
        return None

    def __getitem__(self, name: str | int) -> "Node":
        raise KeyError("A ChildNode instance has no children.")

    @classmethod
    def as_decorator(cls, *args: Any, **kwargs: Any) -> "Decorator":
        r"""
        Return a decorator representation of the child node.

        The provided ``args`` and ``kwargs`` are stored and later passed
        to handler methods when called by the parent processing.

        :param \*args: Positional arguments to pass to handler methods.
        :param \*\*kwargs: Keyword arguments to pass to handler methods.

        :returns: A decorator function that registers the child node.
        :rtype: Decorator
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """The actual decorator that wraps the function."""
            name = Casing.to_snake_case(cls.__name__)
            instance = cls(name=name, process_args=args, process_kwargs=kwargs)
            Tree.queue_child(instance)
            return func

        return decorator


__all__ = ["ChildNode"]
