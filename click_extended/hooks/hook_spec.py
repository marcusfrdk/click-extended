"""Hook spec definitions and pending hook helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, cast

from click_extended.hooks.exception_types import ExceptionType

if TYPE_CHECKING:
    from click_extended.hooks.hook_handler import HookHandler
    from click_extended.hooks.hook_phase import HookPhase


@dataclass(frozen=True)
class HookSpec:
    """
    Pending hook metadata attached to a function.

    :param phase: The lifecycle phase to run the hook in.
    :param handler: The hook handler callable.
    :param include: Exception types to include (whitelist).
    :param exclude: Exception types to exclude (blacklist).
    """

    phase: "HookPhase"
    handler: "HookHandler"
    include: tuple[ExceptionType, ...] | None = None
    exclude: tuple[ExceptionType, ...] | None = None


_PENDING_HOOK_ATTR = "__click_extended_hooks__"


def attach_hook_spec(func: Callable[..., object], spec: HookSpec) -> None:
    """
    Attach a pending hook spec to a function.

    :param func: Function to attach hook metadata to.
    :param spec: Hook spec to attach.
    """
    specs = getattr(func, _PENDING_HOOK_ATTR, None)
    if not isinstance(specs, list):
        specs = []
        setattr(func, _PENDING_HOOK_ATTR, specs)
    specs = cast(list[HookSpec], specs)
    specs.append(spec)


def get_pending_specs(func: Callable[..., object]) -> list[HookSpec]:
    """
    Return pending hook specs attached to a function.

    :param func: Function with pending hook metadata.
    :returns: List of pending hook specs.
    """
    specs = getattr(func, _PENDING_HOOK_ATTR, None)
    return list(specs) if specs else []


def clear_pending_specs(func: Callable[..., object]) -> None:
    """
    Clear pending hook specs from a function.

    :param func: Function with pending hook metadata.
    """
    setattr(func, _PENDING_HOOK_ATTR, [])
