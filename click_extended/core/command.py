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
def command(
    fn: str,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Callable[[Callable], Command]: ...


@overload
def command(
    fn: None = None,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Callable[[Callable], Command]: ...


def command(
    fn: Callable | str | None = None,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Command | Callable[[Callable], Command]:
    if isinstance(fn, str):
        actual_name = fn
        fn = None
    else:
        actual_name = name

    if actual_name is not None:
        attrs["name"] = actual_name
    if aliases is not None:
        attrs["aliases"] = aliases
    if help is not None:
        attrs["help"] = help

    return Command.as_decorator(fn, **attrs)
