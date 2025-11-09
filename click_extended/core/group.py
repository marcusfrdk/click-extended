"""Group decorator for grouping commands and groups."""

from typing import Any, Callable, overload

import click

from click_extended.core._context_node import ContextNode
from click_extended.core.command import Command
from click_extended.errors.invalid_command_type_error import (
    InvalidCommandTypeError,
)


class Group(ContextNode):

    def __init__(
        self, fn: Callable, name: str | None = None, **attrs: Any
    ) -> None:
        super().__init__(fn, name, click.Group, **attrs)
        self.commands: dict[str, "Command | Group"] = {}

    def add(self, cmd: "Command | Group", name: str | None = None) -> None:
        if not isinstance(cmd, ContextNode):
            cmd_type = type(cmd).__name__
            raise InvalidCommandTypeError(cmd_type)

        self.commands[cmd.name] = cmd
        self.cls.add_command(cmd.cls, name)


@overload
def group(fn: Callable, /) -> Group: ...


@overload
def group(fn: str, /, **attrs: Any) -> Callable[[Callable], Group]: ...


@overload
def group(fn: None = None, /, **attrs: Any) -> Callable[[Callable], Group]: ...


def group(
    fn: Callable | str | None = None, /, **attrs: Any
) -> Group | Callable[[Callable], Group]:
    return Group.as_decorator(fn, **attrs)
