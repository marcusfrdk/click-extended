"""Lifecycle phase definitions for hooks."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    import click

    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.other.context import Context


class HookPhase(str, Enum):
    """
    Lifecycle phases for hook execution.

    .. attribute:: BOOT
       Run before click-extended context initialization.

    .. attribute:: INIT
       Run after initialization, before execution.

    .. attribute:: ERROR
       Run when an exception is raised.

    .. attribute:: EXIT
       Run at exit (always).
    """

    BOOT = "boot"
    INIT = "init"
    ERROR = "error"
    EXIT = "exit"


def bind_scoped_hooks(func: Callable[..., object], root: "RootNode") -> None:
    """
    Bind pending hooks on a function to a root scope.

    :param func: Function with pending hook metadata.
    :param root: Root node to scope hooks to.
    """
    from click_extended.hooks.hook_registry import get_registry
    from click_extended.hooks.hook_spec import (
        clear_pending_specs,
        get_pending_specs,
    )

    registry = get_registry()
    specs = get_pending_specs(func)
    if not specs:
        return

    for spec in specs:
        registry.register(
            spec.phase,
            spec.handler,
            scope=root,
            include=spec.include,
            exclude=spec.exclude,
        )

    clear_pending_specs(func)


def run_hook_phase(
    phase: HookPhase,
    click_context: "click.Context",
    root: "RootNode",
    *,
    context: "Context | None" = None,
    exception: BaseException | None = None,
) -> None:
    """
    Execute hooks for a given lifecycle phase.

    :param phase: Lifecycle phase to run.
    :param click_context: Active Click context.
    :param root: Root node of the CLI.
    :param context: click-extended context, if available.
    :param exception: Exception that triggered the hook, if any.
    """
    from click_extended.hooks.hook_registry import get_registry

    get_registry().run(
        phase,
        click_context,
        root,
        context=context,
        exception=exception,
    )
