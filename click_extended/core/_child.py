"""Abstract class representing a child node."""

# pylint: disable=unused-argument

from abc import ABC
from typing import Any, Callable, Optional, TypeVar

from click_extended.core._context import Context
from click_extended.core._main import Main
from click_extended.core._parent import Parent
from click_extended.errors.decorator_implementation_error import (
    DecoratorImplementationError,
)
from click_extended.errors.no_parent_node_error import NoParentNodeError
from click_extended.errors.tagged_environment_error import TaggedEnvironmentError

F = TypeVar("F", bound=Callable[..., Any])


class Child(ABC):
    """Abstract class representing a child node.

    Children process values through a context-aware pipeline with optional
    before/after hooks for transformations and side effects.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Validate that before/after methods are properly paired."""
        super().__init_subclass__(**kwargs)

        has_before_single = cls.before_single is not Child.before_single
        has_after_single = cls.after_single is not Child.after_single

        has_before_multiple = cls.before_multiple is not Child.before_multiple
        has_after_multiple = cls.after_multiple is not Child.after_multiple

        if has_before_single and not has_after_single:
            raise DecoratorImplementationError(
                f"{cls.__name__}: before_single is implemented but after_single is not"
            )

        if has_after_single and not has_before_single:
            raise DecoratorImplementationError(
                f"{cls.__name__}: after_single is implemented but before_single is not"
            )

        if has_before_multiple and not has_after_multiple:
            raise DecoratorImplementationError(
                f"{cls.__name__}: before_multiple is implemented but after_multiple is not"
            )

        if has_after_multiple and not has_before_multiple:
            raise DecoratorImplementationError(
                f"{cls.__name__}: after_multiple is implemented but before_multiple is not"
            )

    def before_single(self, value: Any, ctx: Context) -> None:
        """Hook called before the decorated function executes."""

    def after_single(self, value: Any, ctx: Context) -> Any:
        """Hook called after the decorated function executes."""
        return value

    def before_multiple(self, values: dict[str, Any], ctx: Context) -> None:
        """Hook called before the decorated function executes in a tagged environment."""
        raise TaggedEnvironmentError(
            f"{self.__class__.__name__} cannot be used in a tagged environment. "
            "Implement before_multiple and after_multiple to support tags."
        )

    def after_multiple(self, values: dict[str, Any], ctx: Context) -> dict[str, Any]:
        """Hook called after the decorated function executes in a tagged environment."""
        raise TaggedEnvironmentError(
            f"{self.__class__.__name__} cannot be used in a tagged environment. "
            "Implement before_multiple and after_multiple to support tags."
        )

    def __call__(self, parent_or_fn: Any) -> Any:
        """Register this child with a parent or store function for later.

        This method handles the decorator chain registration.
        """

        if isinstance(parent_or_fn, Parent):
            parent_or_fn.add_child(self)
            return parent_or_fn

        if isinstance(parent_or_fn, Main):
            raise NoParentNodeError(
                "Child decorators cannot be applied directly to a main node (command or group). "
                "They must be applied under a parent decorator (option, argument, env, tag)."
            )

        if callable(parent_or_fn):
            self.pending_func = parent_or_fn
            return self

        raise NoParentNodeError(
            "Child decorators must be applied under a parent decorator "
            "(option, argument, env, tag)."
        )

    @staticmethod
    def decorator(
        fn: Optional[F] = None,
        *,
        cls: type,
        **default_kwargs: Any,
    ) -> Callable[[F], F] | F:
        """Create a decorator for the class."""

        def wrapper(func: F) -> F:
            """Wrap the function with the decorator class."""
            instance = cls(**default_kwargs)
            return instance(func)

        if fn is None:
            return wrapper
        return wrapper(fn)
