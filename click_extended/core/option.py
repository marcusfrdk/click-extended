"""Class representing an option in the context."""

from collections.abc import Callable
from typing import Any, TypeVar

import click

from click_extended.core._main import Main
from click_extended.core._parent import Parent

F = TypeVar("F", bound=Callable[..., Any])


class Option(Parent):
    """Class representing an option in the context."""

    def __init__(
        self,
        name: str,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new Option instance."""
        super().__init__(name=name, tags=tags)
        self.click_kwargs = kwargs

    def apply_click_decorator(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Apply Click's option decorator to a function."""
        if self.name is None:
            raise ValueError("Option name cannot be None")
        return click.option(self.name, **self.click_kwargs)(func)  # type: ignore[arg-type]


def option(
    name: str,
    *,
    tags: list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Any], Any]:
    """Option decorator - must be called with parentheses."""
    if callable(name):
        raise TypeError(
            "option() must be called with parentheses: use @option('--name') "
            "instead of @option"
        )

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Option decorator."""
        opt = Option(name=name, tags=tags, **kwargs)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(opt)
            return main_or_parent

        return opt(main_or_parent)

    return wrapper
