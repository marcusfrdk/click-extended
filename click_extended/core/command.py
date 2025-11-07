"""Class representing a command in the command line."""

from typing import Any, Callable, Optional, TypeVar

import click

from click_extended.core._child import Child
from click_extended.core._main import Main
from click_extended.core._parent import Parent
from click_extended.errors.no_parent_node_error import NoParentNodeError

F = TypeVar("F", bound=Callable[..., Any])


class Command(Main):
    """Class representing a command in the command line."""

    def __init__(self, name: str | None = None, **kwargs: Any) -> None:
        """Initialize a new Command instance."""
        super().__init__()
        self.name = name
        self.click_kwargs = kwargs
        self.context.main["type"] = "command"
        self.context.main["name"] = name
        self._click_command: Callable[..., Any] | None = None

    def build_click_command(self) -> Callable[..., Any]:
        """Build the Click command with all parent decorators applied."""
        if self.func is None:
            raise RuntimeError("No function to wrap")

        def wrapper_func(**click_kwargs: Any) -> Any:
            """Wrapper that Click will call with parsed arguments."""
            return super(Command, self).__call__(**click_kwargs)

        wrapper_func.__name__ = self.func.__name__

        cmd = wrapper_func

        for parent in reversed(self.parents):
            if hasattr(parent, "apply_click_decorator"):
                cmd = parent.apply_click_decorator(cmd)

        cmd = click.command(name=self.name, **self.click_kwargs)(cmd)

        return cmd

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute via Click command if no args provided, otherwise execute chain."""
        if len(args) == 0 and len(kwargs) == 0:
            if self._click_command is None:
                self._click_command = self.build_click_command()
            return self._click_command()

        return super().__call__(*args, **kwargs)


def command(
    fn: Optional[F] = None,
    *,
    name: str | None = None,
    **kwargs: Any,
) -> Callable[[F], F] | F:
    """Command decorator with flexible invocation patterns."""

    def wrapper(func: F) -> Command:
        """Wrap the function with the Command decorator."""

        if isinstance(func, Parent):
            actual_func = func.pending_func
            func_name = actual_func.__name__ if actual_func else name
            cmd = Command(name=name or func_name, **kwargs)
            cmd.func = actual_func
            cmd.add_parent(func)
            return cmd

        if isinstance(func, Child):
            raise NoParentNodeError(
                f"Child decorator '{func.__class__.__name__}' must be applied to a parent decorator "
                "(option, argument, env, or tag). Cannot apply child directly to a command."
            )

        cmd = Command(name=name or func.__name__, **kwargs)
        cmd.func = func
        return cmd

    if fn is None:
        return wrapper
    return wrapper(fn)
