"""Tests for the hook system."""

from __future__ import annotations

from unittest.mock import Mock

import click
import pytest

from click_extended.core.nodes._root_node import RootNode
from click_extended.hooks.hook_event import HookEvent
from click_extended.hooks.hook_phase import (
    HookPhase,
    bind_scoped_hooks,
    run_hook_phase,
)
from click_extended.hooks.hook_registry import HookRegistry, get_registry
from click_extended.hooks.on_boot import on_boot
from click_extended.hooks.on_error import on_error
from click_extended.hooks.on_exit import on_exit
from click_extended.hooks.on_init import on_init


@pytest.fixture
def hook_registry() -> HookRegistry:  # type: ignore
    """Reset hook registry between tests."""
    registry = get_registry()
    registry._hooks.clear()  # type: ignore
    yield registry  # type: ignore
    registry._hooks.clear()  # type: ignore


def make_click_context() -> click.Context:
    """Create a click context for hook execution."""
    return click.Context(click.Command("cmd"))


def test_on_boot_runs_global_hook(hook_registry: HookRegistry) -> None:
    """Ensure on_boot registers and runs a global hook."""
    events: list[HookPhase] = []

    @on_boot()
    def handler(event: HookEvent) -> None:  # type: ignore
        events.append(event.phase)

    click_context = make_click_context()
    root = Mock(spec=RootNode)

    run_hook_phase(HookPhase.BOOT, click_context, root, context=None)

    assert events == [HookPhase.BOOT]


def test_scoped_hook_is_bound_to_root(hook_registry: HookRegistry) -> None:
    """Ensure scoped hooks are registered only after binding."""
    events: list[object] = []

    def handler(event: HookEvent) -> None:
        events.append(event.root)

    @on_init(handler)
    def cmd() -> None:
        pass

    assert len(hook_registry._hooks) == 0  # type: ignore

    root = Mock(spec=RootNode)
    bind_scoped_hooks(cmd, root)
    assert len(hook_registry._hooks) == 1  # type: ignore

    click_context = make_click_context()

    run_hook_phase(HookPhase.INIT, click_context, root, context=None)

    assert events == [root]


def test_error_hook_filters_exceptions(hook_registry: HookRegistry) -> None:
    """Ensure on_error filters exceptions by type."""
    seen: list[str] = []

    @on_error(ValueError)
    def handler(event: HookEvent) -> None:  # type: ignore
        assert event.exception is not None
        seen.append(event.exception.__class__.__name__)

    click_context = make_click_context()
    root = Mock(spec=RootNode)

    run_hook_phase(
        HookPhase.ERROR,
        click_context,
        root,
        context=None,
        exception=ValueError("boom"),
    )
    assert seen == ["ValueError"]

    seen.clear()
    run_hook_phase(
        HookPhase.ERROR,
        click_context,
        root,
        context=None,
        exception=KeyError("missing"),
    )
    assert seen == []


def test_scoped_hooks_run_before_global(hook_registry: HookRegistry) -> None:
    """Ensure scoped hooks run before global hooks."""
    order: list[str] = []

    def scoped_handler(event: HookEvent) -> None:
        order.append("scoped")

    def global_handler(event: HookEvent) -> None:
        order.append("global")

    root = Mock(spec=RootNode)

    hook_registry.register(HookPhase.INIT, global_handler, scope=None)
    hook_registry.register(HookPhase.INIT, scoped_handler, scope=root)

    click_context = make_click_context()

    run_hook_phase(HookPhase.INIT, click_context, root, context=None)

    assert order == ["scoped", "global"]


def test_on_exit_registers_direct_handler(hook_registry: HookRegistry) -> None:
    """Ensure on_exit registers a direct handler."""
    called: list[bool] = []

    def handler(event: HookEvent) -> None:
        called.append(True)

    on_exit(handler)

    click_context = make_click_context()
    root = Mock(spec=RootNode)

    run_hook_phase(HookPhase.EXIT, click_context, root, context=None)

    assert called == [True]
