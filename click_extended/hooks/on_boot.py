"""Hook called before initialization."""

from __future__ import annotations

from typing import Callable, overload

from click_extended.hooks.hook_handler import HookHandler
from click_extended.hooks.hook_node import HookNode
from click_extended.hooks.hook_phase import HookPhase
from click_extended.hooks.hook_registry import get_registry


@overload
def on_boot(handler: HookHandler) -> HookNode: ...


@overload
def on_boot() -> Callable[[HookHandler], HookHandler]: ...


def on_boot(
    handler: HookHandler | None = None,
) -> HookNode | Callable[[HookHandler], HookHandler]:
    """
    Register a hook to run before context initialization.

    This supports both direct calls and decorator usage.

    :param handler: Hook handler callable.
    :returns: The registered hook node or a decorator.
    """
    registry = get_registry()
    if handler is None:

        def decorator(func: HookHandler) -> HookHandler:
            registry.register(HookPhase.BOOT, func, scope=None)
            return func

        return decorator

    return registry.register(HookPhase.BOOT, handler, scope=None)
