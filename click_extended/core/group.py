"""Group decorator for grouping commands and groups."""

from typing import Any, Callable, overload

import click

from click_extended.core._context_node import ContextNode
from click_extended.core._parent_node import ParentNode
from click_extended.core.command import Command
from click_extended.errors.invalid_command_type_error import (
    InvalidCommandTypeError,
)


class Group(ContextNode):

    def __init__(
        self, fn: Callable, name: str | None = None, **attrs: Any
    ) -> None:
        if "context_settings" not in attrs:
            attrs["context_settings"] = {}
        if "help_option_names" not in attrs["context_settings"]:
            attrs["context_settings"]["help_option_names"] = ["-h", "--help"]

        super().__init__(fn, name, click.Group, **attrs)
        self.commands: dict[str, "Command | Group"] = {}

    def add_parent(self, parent: ParentNode) -> None:
        super().add_parent(parent)

        for parent in self.parents.values():
            if parent.short == "-h":
                if self.cls.params and hasattr(self.cls.params[0], "opts"):
                    help_param = self.cls.params[0]
                    help_param.opts = ["--help"]
                    help_param.secondary_opts = []
                break

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
