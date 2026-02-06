"""Handler type for hook functions."""

from __future__ import annotations

from typing import Any, Callable

from click_extended.hooks.hook_event import HookEvent

HookHandler = Callable[[HookEvent], Any]
