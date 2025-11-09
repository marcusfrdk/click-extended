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

    def __init__(
        self,
        fn: Callable,
        name: str | None = None,
        click_cls: type = click.Command,
        **attrs: Any,
    ) -> None:
        self.fn = fn
        self.name = name or fn.__name__
        self.is_async = asyncio.iscoroutinefunction(fn)
        self.parents: dict[str, ParentNode] = {}
        self.active_parent: ParentNode | None = None
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
        sig = inspect.signature(self.fn)
        expects_ctx = "ctx" in sig.parameters

        if self.is_async:

            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                if expects_ctx:
                    kwargs["ctx"] = self
                return asyncio.run(self.fn(*args, **kwargs))

            return sync_wrapper
        else:

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if expects_ctx:
                    kwargs["ctx"] = self
                return self.fn(*args, **kwargs)

            return wrapper

    def __getattr__(self, name: str) -> Any:
        return getattr(self.cls, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.cls(*args, **kwargs)

    def add_parent(self, parent: ParentNode) -> None:
        name = Transform(parent.name).to_snake_case()

        if name in self.parents:
            raise NameCollisionError(parent.name)

        self.parents[name] = parent
        self.active_parent = parent

    def add_child(self, child: ChildNode) -> None:
        if self.active_parent is None:
            raise NoParentError(str(type(child).__name__))

        self.active_parent.add_child(child)
