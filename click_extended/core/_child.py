"""Abstract class representing a child node."""

# pylint: disable=unused-argument
# pylint: disable=import-outside-toplevel

from abc import ABC
from collections.abc import Callable
from typing import Any, TypeVar

from click_extended.core._context import Context
from click_extended.errors import (
    DecoratorImplementationError,
    NoParentNodeError,
    TaggedEnvironmentError,
)

F = TypeVar("F", bound=Callable[..., Any])


class Child(ABC):  # noqa: B024
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

        if has_before_multiple and not has_after_multiple:
            raise DecoratorImplementationError(
                f"{cls.__name__}: before_multiple is implemented but "
                "after_multiple is not"
            )

    def before_single(self, value: Any, ctx: Context) -> None:  # noqa: B027
        """Hook called before the decorated function executes."""

    def after_single(self, value: Any, ctx: Context) -> Any:  # noqa: ARG002
        """Hook called after the decorated function executes."""
        return value

    def before_multiple(
        self, values: dict[str, Any], ctx: Context  # noqa: ARG002
    ) -> None:
        """Hook called before function executes in a tagged environment."""
        raise TaggedEnvironmentError(
            f"{self.__class__.__name__} cannot be used in a tagged environment. "
            "Implement before_multiple and after_multiple to support tags."
        )

    def after_multiple(
        self, values: dict[str, Any], ctx: Context  # noqa: ARG002
    ) -> dict[str, Any]:
        """Hook called after function executes in a tagged environment."""
        raise TaggedEnvironmentError(
            f"{self.__class__.__name__} cannot be used in a tagged environment. "
            "Implement before_multiple and after_multiple to support tags."
        )

    def __call__(self, parent_or_fn: Any) -> Any:
        """Register this child with a parent or store function for later.

        This method handles the decorator chain registration.
        """
        from click_extended.core._main import Main
        from click_extended.core._parent import Parent

        if isinstance(parent_or_fn, Parent):
            self.pending_func = (
                parent_or_fn.pending_func
                if hasattr(parent_or_fn, "pending_func")
                else parent_or_fn
            )
            self.wrapped_parent = parent_or_fn
            return self

        if isinstance(parent_or_fn, Main):
            raise NoParentNodeError(
                "Child decorators cannot be applied directly to a main node "
                "(command or group). They must be applied under a parent "
                "decorator (option, argument, env, tag)."
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
        fn: F | None = None,
        *,
        cls: type,
        **default_kwargs: Any,
    ) -> Callable[[F], F] | F:
        """Create a decorator for the class."""

        def wrapper(func: F) -> F:
            """Wrap the function with the decorator class."""
            instance = cls(**default_kwargs)
            return instance(func)  # type: ignore[no-any-return, return-value]

        if fn is None:
            return wrapper
        return wrapper(fn)
