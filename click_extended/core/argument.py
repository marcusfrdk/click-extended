"""Class representing an argument in the command line."""

from collections.abc import Callable
from typing import Any

import click

from click_extended.core._main import Main
from click_extended.core._parent import Parent


class Argument(Parent):
    """Class representing an argument in the command line."""

    def __init__(
        self,
        name: str,
        tags: list[str] | None = None,
    ) -> None:
        """Initialize a new Argument instance."""
        super().__init__(name=name, tags=tags)

    def apply_click_decorator(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Apply Click's argument decorator to a function."""
        if self.name is None:
            raise ValueError("Argument name cannot be None")
        return click.argument(self.name)(func)  # type: ignore[arg-type]


def argument(name: str, *, tags: list[str] | None = None) -> Callable[[Any], Any]:
    """Argument decorator - must be called with parentheses."""
    if callable(name):
        raise TypeError(
            "argument() must be called with parentheses: use @argument('name') "
            "instead of @argument"
        )

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Argument decorator."""
        arg = Argument(name=name, tags=tags)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(arg)
            return arg

        return arg(main_or_parent)

    return wrapper
