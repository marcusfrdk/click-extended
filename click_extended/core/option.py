"""Class representing an option in the context."""

from typing import Any, Callable, TypeVar

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
        return click.option(self.name, **self.click_kwargs)(func)


def option(
    name: str,
    *,
    tags: list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Any], Any]:
    """Option decorator with flexible invocation patterns."""

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Option decorator."""
        opt = Option(name=name, tags=tags, **kwargs)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(opt)
            return main_or_parent

        return opt(main_or_parent)

    return wrapper
