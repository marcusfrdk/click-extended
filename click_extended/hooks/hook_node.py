"""Hook node definition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from click_extended.hooks.exception_types import ExceptionType
from click_extended.hooks.hook_handler import HookHandler
from click_extended.hooks.hook_phase import HookPhase
from click_extended.hooks.hook_spec import HookSpec, attach_hook_spec

if TYPE_CHECKING:
    from click_extended.core.nodes._root_node import RootNode


@dataclass(frozen=True)
class HookNode:
    """
    A registered hook handler with optional scope and filters.

    :param phase: The lifecycle phase to run the hook in.
    :param handler: The hook handler callable.
    :param scope: Root node to scope the hook to, or None for global.
    :param include: Exception types to include (whitelist).
    :param exclude: Exception types to exclude (blacklist).
    """

    phase: HookPhase
    handler: HookHandler
    scope: "RootNode | None"
    include: tuple[ExceptionType, ...] | None = None
    exclude: tuple[ExceptionType, ...] | None = None

    def __call__(self, func: Callable[..., object]) -> Callable[..., object]:
        """
        Attach this hook to a command/group function.

        When used as a decorator (e.g., ``@on_init(handler)``), the global
        registration is replaced with a pending hook bound to the function.

        :param func: The command/group function to attach the hook to.
        :returns: The original function.
        """
        from click_extended.hooks.hook_registry import get_registry

        if self.scope is None:
            get_registry().unregister(self)

        attach_hook_spec(
            func,
            HookSpec(
                phase=self.phase,
                handler=self.handler,
                include=self.include,
                exclude=self.exclude,
            ),
        )
        return func
