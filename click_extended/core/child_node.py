"""ChildNode class for handler-based value processing."""

from abc import ABC
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable
from uuid import UUID

from click_extended.core._tree import Tree
from click_extended.core.context import Context
from click_extended.core.node import Node
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
    ) -> None:
        """
        Initialize a new `ChildNode` instance.

        Args:
            name (str):
                The name of the node.
            process_args (tuple):
                Positional arguments to pass to handler methods.
            process_kwargs (dict[str, Any]):
                Keyword arguments to pass to handler methods.
        """
        super().__init__(name=name, children=None)
        self.process_args = process_args or ()
        self.process_kwargs = process_kwargs or {}

    def handle_none(self, context: "Context", *args: Any, **kwargs: Any) -> Any:
        """
        Handle None values explicitly.

        Called when value is `None` before any other handler.
        If not implemented, `None` values are auto-skipped.

        Args:
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                The processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_all(
        self, value: Any, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        """
        Handle all value types. Called as fallback if no
        specific handler is implemented.

        Also catches `None` values if `handle_none` is not implemented.

        Args:
            value (Any):
                The value to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or None to pass through unchanged.
        """
        raise NotImplementedError

    def handle_primitive(
        self,
        value: str | int | float | bool,
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle primitive types (str, int, float, bool).

        Args:
            value (str | int | float | bool):
                The primitive value to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_flat_tuple(
        self,
        value: tuple[Any, ...],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle tuples containing ONLY primitive types.

        Called for:
            - `(1, 2, 3)`
            - `("a", "b", "c")`
            - `(1, "hello", 3.14, True)`
            - `()` - empty tuple

        Not called for:
            - `((1, 2), (3, 4))`: use `handle_nested_tuple`
            - `(1, [2, 3])`: use `handle_tuple` (mixed)

        Args:
            value (tuple[Any, ...]):
                The flat tuple to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_tuple(
        self,
        value: tuple[Any, ...],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle any tuple structure (fallback).

        Called when:

            - `handle_flat_tuple` not implemented and the tuple is flat
            - `handle_nested_tuple` not implemented and the tuple is nested
            - Tuple has mixed primitive and complex types

        Use this when you want to handle all tuple types with the same logic,
        or when you need to handle mixed-type tuples.

        Examples:

            - `(1, 2, 3)` if `handle_flat_tuple` not implemented
            - `((1, 2),)` if `handle_nested_tuple` not implemented
            - `(1, [2, 3], "hello")`: mixed types (only option)

        Args:
            value (tuple[Any, ...]):
                The tuple to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_list(
        self,
        value: list[Any],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle list values.

        Args:
            value (list[Any]):
                The list to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_nested_tuple(
        self,
        value: tuple[Any, ...],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle tuples containing ONLY complex/collection types.

        Called for:

            - `((1, 2), (3, 4))`: nested tuples
            - `([1, 2], [3, 4])`: tuple of lists
            - `({"a": 1}, {"b": 2})`: tuple of dicts
            - `(Path("a"), Path("b"))`: tuple of Paths

        Not called for:

            - `(1, 2, 3)`: use `handle_flat_tuple`
            - `(1, [2, 3])`: use `handle_tuple` (mixed)

        Type hints specify the internal structure:

            - `tuple[tuple[int, ...], ...]`: validates nested tuples of ints
            - `tuple[list[str], ...]`: validates tuple of string lists
            - `tuple[Path, ...]`: validates tuple of Paths

        Args:
            value (tuple[Any, ...]):
                The nested tuple to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_dict(
        self,
        value: dict[Any, Any],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle dictionary values.

        Args:
            value (dict[Any, Any]):
                The dictionary to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_tag(
        self,
        value: dict[str, Any],
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle values from a `Tag` parent.

        Called when the parent node is a `Tag`. The value is a dictionary
        mapping parameter names to their values from all parent nodes
        (`Option`, `Argument`, `Env`, etc.) that reference this tag.

        Can be implemented as sync or async. This handler is validation-only
        and must not return a value (or return None).

        Args:
            value (dict[str, Any]):
                Dictionary mapping parameter names to values from
                all parent nodes referencing this tag. Keys are parent
                node names (e.g., "username"), values are `None` if not
                provided by the user.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            None:
                Must return None (validation-only).
        """
        raise NotImplementedError

    def handle_datetime(
        self,
        value: datetime | date | time,
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Handle datetime, date, and time objects.

        Args:
            value (datetime | date | time):
                The datetime, date, or time object to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_uuid(
        self, value: UUID, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        """
        Handle UUID objects.

        Args:
            value (UUID):
                The UUID object to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_path(
        self, value: Path, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        """
        Handle Path objects.

        Args:
            value (Path):
                The Path object to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_bytes(
        self, value: bytes, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        """
        Handle bytes objects.

        Args:
            value (bytes):
                The bytes object to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def handle_decimal(
        self, value: Decimal, context: "Context", *args: Any, **kwargs: Any
    ) -> Any:
        """
        Handle Decimal objects.

        Args:
            value (Decimal):
                The Decimal object to process.
            context (Context):
                Information about the current context.
            *args (Any):
                Additional positional arguments from decorator.
            **kwargs (Any):
                Additional keyword arguments from decorator.

        Returns:
            Any:
                Processed value, or `None` to pass through unchanged.
        """
        raise NotImplementedError

    def get(self, _name: str) -> None:
        """
        The ChildNode has no children, thus this method returns None.

        Args:
            _name (str):
                The name of the child.

        Returns:
            None:
                Always returns None as the ChildNode has no children.
        """
        return None

    def __getitem__(self, name: str | int) -> "Node":
        raise KeyError("A ChildNode instance has no children.")

    @classmethod
    def as_decorator(cls, *args: Any, **kwargs: Any) -> "Decorator":
        """
        Return a decorator representation of the child node.

        The provided `args` and `kwargs` are stored and later passed to handler
        methods when called by the parent processing.

        Args:
            *args (Any):
                Positional arguments to pass to handler methods.
            **kwargs (Any):
                Keyword arguments to pass to handler methods.

        Returns:
            Decorator:
                A decorator function that registers the child node.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """The actual decorator that wraps the function."""
            name = Casing.to_snake_case(cls.__name__)
            instance = cls(name=name, process_args=args, process_kwargs=kwargs)
            Tree.queue_child(instance)
            return func

        return decorator


__all__ = ["ChildNode"]
