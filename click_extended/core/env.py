"""Class to inject environment variables into the context."""

from collections.abc import Callable
from typing import Any

from click_extended.core._main import Main
from click_extended.core._parent import Parent


class Env(Parent):
    """Class to inject environment variables into the context."""

    def __init__(
        self,
        name: str,
        tags: list[str] | None = None,
    ) -> None:
        """Initialize a new Env instance."""
        super().__init__(name=name, tags=tags)


def env(
    name: str,
    *,
    tags: list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Any], Any]:
    """Environment variable decorator - must be called with parentheses."""
    if callable(name):
        raise TypeError(
            "env() must be called with parentheses: use @env('VAR_NAME') "
            "instead of @env"
        )

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Env decorator."""
        environment = Env(name=name, tags=tags, **kwargs)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(environment)
            return environment

        return environment(main_or_parent)

    return wrapper
