"""Class representing a group of commands in the command line."""

from typing import Any, Callable, Optional, TypeVar

from click_extended.core._main import Main

F = TypeVar("F", bound=Callable[..., Any])


class Group(Main):
    """Class representing a group of commands in the command line."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize a new Group instance."""
        super().__init__()
        self.name = name
        self.context.main["type"] = "group"
        self.context.main["name"] = name


def group(fn: Optional[F] = None, *, name: str | None = None) -> Callable[[F], F] | F:
    """Group decorator with flexible invocation patterns."""

    def wrapper(func: F) -> Group:
        """Wrap the function with the Group decorator."""
        grp = Group(name=name or func.__name__)
        grp.func = func
        return grp

    if fn is None:
        return wrapper
    return wrapper(fn)
