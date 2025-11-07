"""Class to inject environment variables into the context."""

from typing import Any, Callable

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
    """Environment variable decorator with flexible invocation patterns."""

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Env decorator."""
        environment = Env(name=name, tags=tags, **kwargs)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(environment)
            return environment

        return environment(main_or_parent)

    return wrapper
