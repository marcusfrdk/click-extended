"""Initialization file for the `click_extended.hooks` module."""

from click_extended.hooks.hook_event import HookEvent
from click_extended.hooks.hook_handler import HookHandler
from click_extended.hooks.hook_node import HookNode
from click_extended.hooks.hook_phase import (
    HookPhase,
    bind_scoped_hooks,
    run_hook_phase,
)
from click_extended.hooks.hook_registry import HookRegistry, get_registry
from click_extended.hooks.hook_spec import HookSpec
from click_extended.hooks.on_boot import on_boot
from click_extended.hooks.on_error import on_error
from click_extended.hooks.on_exit import on_exit
from click_extended.hooks.on_init import on_init
from click_extended.hooks.types import ExceptionFilter, ExceptionType

__all__ = [
    "ExceptionFilter",
    "ExceptionType",
    "HookEvent",
    "HookHandler",
    "HookNode",
    "HookPhase",
    "HookRegistry",
    "HookSpec",
    "bind_scoped_hooks",
    "get_registry",
    "on_boot",
    "on_error",
    "on_exit",
    "on_init",
    "run_hook_phase",
]
