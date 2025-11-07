"""Class representing an argument in the command line."""

from typing import Any, Callable

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


def argument(name: str, *, tags: list[str] | None = None) -> Callable[[Any], Any]:
    """Argument decorator with flexible invocation patterns."""

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Argument decorator."""
        arg = Argument(name=name, tags=tags)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(arg)
            return arg

        return arg(main_or_parent)

    return wrapper
