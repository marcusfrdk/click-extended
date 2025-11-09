"""Command decorator for creating a command in the command line interface."""

from typing import Any, Callable, overload

import click

from click_extended.core._context_node import ContextNode


class Command(ContextNode):

    def __init__(
        self, fn: Callable, name: str | None = None, **attrs: Any
    ) -> None:
        super().__init__(fn, name, click.Command, **attrs)


@overload
def command(fn: Callable, /) -> Command: ...


@overload
def command(fn: str, /, **attrs: Any) -> Callable[[Callable], Command]: ...


@overload
def command(
    fn: None = None, /, **attrs: Any
) -> Callable[[Callable], Command]: ...


def command(
    fn: Callable | str | None = None, /, **attrs: Any
) -> Command | Callable[[Callable], Command]:
    return Command.as_decorator(fn, **attrs)
