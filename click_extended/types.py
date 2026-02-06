"""Types used in `click_extended`."""

from __future__ import annotations

from typing import Any, Callable

from click_extended.core.other.context import Context
from click_extended.hooks.hook_event import HookEvent
from click_extended.hooks.hook_handler import HookHandler

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]

__all__ = [
    "Context",
    "Decorator",
    "HookEvent",
    "HookHandler",
]
