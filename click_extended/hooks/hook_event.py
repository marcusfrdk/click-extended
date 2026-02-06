"""Hook event payload definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import click

from click_extended.hooks.hook_phase import HookPhase

if TYPE_CHECKING:
    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.other.context import Context


@dataclass(frozen=True)
class HookEvent:
    """
    Data passed to hook handlers.

    :param phase: The lifecycle phase that triggered the hook.
    :param click_context: Active Click context.
    :param root: Root node of the CLI, if scoped.
    :param context: click-extended context, if initialized.
    :param exception: Exception that triggered the hook, if any.
    """

    phase: HookPhase
    click_context: click.Context
    root: "RootNode | None"
    context: "Context | None"
    exception: BaseException | None = None
