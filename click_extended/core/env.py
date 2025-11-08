"""Class to inject environment variables into the context."""

import os
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
        key: str | None = None,
        default: str | None = None,
    ) -> None:
        """Initialize a new Env instance.

        Args:
            name: The environment variable name (e.g., "DATABASE_URL")
            tags: Optional tags for grouping
            key: Optional key to inject into kwargs (defaults to snake_case of name)
            default: Default value if environment variable is not found
        """
        super().__init__(name=name, tags=tags)
        self.key = key
        self.default = default

    def get_injection_key(self) -> str:
        """Get the key to use for injecting into function kwargs."""
        if self.key:
            return self.key

        # Convert NAME to snake_case (e.g., DATABASE_URL -> database_url)
        if self.name:
            return self.name.lower()
        return "env_value"

    def get_env_value(self) -> str | None:
        """Get the environment variable value or default."""
        if self.name:
            return os.environ.get(self.name, self.default)
        return self.default


def env(
    name: str,
    *,
    tags: list[str] | None = None,
    key: str | None = None,
    default: str | None = None,
) -> Callable[[Any], Any]:
    """Environment variable decorator which must be called with parentheses."""
    if callable(name):
        raise TypeError(
            "env() must be called with parentheses: use @env('VAR_NAME') "
            "instead of @env"
        )

    def wrapper(main_or_parent: Any) -> Any:
        """Wrap with the Env decorator."""
        environment = Env(name=name, tags=tags, key=key, default=default)

        if isinstance(main_or_parent, Main):
            main_or_parent.add_parent(environment)
            return environment

        return environment(main_or_parent)

    return wrapper
