import asyncio
import inspect
from abc import ABC
from typing import Any, Callable, TypeVar, overload

import click

from click_extended.core._child_node import ChildNode
from click_extended.core._parent_node import ParentNode
from click_extended.errors.name_collision_error import NameCollisionError
from click_extended.errors.no_parent_error import NoParentError
from click_extended.utils.transform import Transform

T = TypeVar("T", bound="ContextNode")


class ContextNode(ABC):
    """Base class for context nodes."""

    def __init__(
        self,
        fn: Callable,
        name: str | None = None,
        click_cls: type = click.Command,
        **attrs: Any,
    ) -> None:
        """
        Initialize a new `ContextNode` instance.

        Args:
            fn (Callable):
                The function to wrap as a command or group.
            name (str | None):
                The name of the command/group. If `None`,
                uses the function name.
            click_cls (click.Command | click.Group):
                The Click class to instantiate.
            **attrs (Any):
                Additional attributes to pass to the Click command/group.
        """
        # Metadata
        self.fn = fn
        self.name = name or fn.__name__
        self.is_async = asyncio.iscoroutinefunction(fn)

        # Parents
        self.parents: dict[str, ParentNode] = {}
        self.active_parent: ParentNode | None = None

        # Aliases
        self.aliases: list[str] = []
        if (aliases := attrs.pop("aliases", None)) is not None:
            if isinstance(aliases, str):
                self.aliases = [aliases]
            elif isinstance(aliases, (list, tuple)):
                self.aliases = [
                    a for a in aliases if isinstance(a, str) and a.strip()
                ]

        # Help
        if "help" not in attrs and fn.__doc__:
            attrs["help"] = fn.__doc__

        # Click
        self.cls = click_cls(
            name=self.name, callback=self._make_callback(), **attrs
        )

    @classmethod
    @overload
    def as_decorator(cls: type[T], fn: Callable, /) -> T: ...

    @classmethod
    @overload
    def as_decorator(
        cls: type[T], fn: str, /, **attrs: Any
    ) -> Callable[[Callable], T]: ...

    @classmethod
    @overload
    def as_decorator(
        cls: type[T], fn: None = None, /, **attrs: Any
    ) -> Callable[[Callable], T]: ...

    @classmethod
    def as_decorator(
        cls: type[T], fn: Callable | str | None = None, /, **attrs: Any
    ) -> T | Callable[[Callable], T]:
        """
        Create a decorator that wraps a function as a ContextNode.

        This method handles three decorator patterns:
        - @decorator: Direct application without parentheses
        - @decorator(): Called with parentheses but no arguments
        - @decorator("name"): Called with a name string
        - @decorator(name="name"): Called with keyword arguments

        Args:
            fn (Callable | str | None):
                The function to decorate, a name string, or `None`.
            **attrs (Any):
                Additional attributes to pass to the `ContextNode` constructor.

        Returns:
            T | Callable[[Callable], T]:
                Either a `ContextNode` instance or a decorator function.
        """
        # Name is provided
        if isinstance(fn, str):

            def decorator(f: Callable) -> T:
                return cls(f, name=fn, **attrs)

            return decorator

        # Decorator is called (@decorator())
        if fn is None:

            def decorator(f: Callable) -> T:
                return cls(f, **attrs)

            return decorator

        # Decorator is not called (@decorator)
        return cls(fn, **attrs)

    def _make_callback(self) -> Callable:
        """
        Create a callback function for the Click command which injects the
        context into the function as the `ctx` parameter and adds support
        for asynchronous functions.

        Returns:
            Callable:
                The wrapped callback function suitable for Click.
        """
        sig = inspect.signature(self.fn)
        expects_ctx = "ctx" in sig.parameters

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if expects_ctx:
                kwargs["ctx"] = self

            if self.is_async:
                return asyncio.run(self.fn(*args, **kwargs))
            return self.fn(*args, **kwargs)

        return wrapper

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the underlying Click instance.

        This allows the ContextNode to act as a transparent proxy to the
        wrapped Click instance.

        Args:
            name (str):
                The attribute name to access.

        Returns:
            Any:
                The attribute value from the wrapped Click instance.
        """
        return getattr(self.cls, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Make the ContextNode callable by calling the underlying Click instance.

        Args:
            *args (Any):
                Positional arguments to pass to the Click command.
            **kwargs (Any):
                Keyword arguments to pass to the Click command.

        Returns:
            Any:
                The result of invoking the Click command/group.
        """
        return self.cls(*args, **kwargs)

    def add_parent(self, parent: ParentNode) -> None:
        """
        Add a parent node to this context node.

        This stores the parent in the parents dictionary using the normalized
        snake_case name and sets it as the active parent. Multiple parents can
        be added, but name collisions will raise an error. As an example,
        `My_name` and `my_name` will cause a name collision.

        Args:
            parent (ParentNode):
                The parent node to add to this context node.

        Raises:
            NameCollisionError:
                If a parent with the normalized name already exists.
        """
        name = Transform(parent.name).to_snake_case()

        if name in self.parents:
            raise NameCollisionError(parent.name)

        self.parents[name] = parent
        self.active_parent = parent

    def add_child(self, child: ChildNode) -> None:
        """
        Add a child node to the active parent.

        Args:
            child (ChildNode):
                The child node to add to the active parent.

        Raises:
            NoParentError:
                If no active parent is set for this context node.
        """
        if self.active_parent is None:
            raise NoParentError(str(type(child).__name__))

        self.active_parent.add_child(child)
