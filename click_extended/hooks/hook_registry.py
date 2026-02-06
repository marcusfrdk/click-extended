"""Hook registry implementation."""

# pylint: disable=too-many-arguments
# pylint: disable=broad-exception-caught

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import click

from click_extended.hooks.exception_types import ExceptionType

if TYPE_CHECKING:
    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.other.context import Context
    from click_extended.hooks.hook_event import HookEvent
    from click_extended.hooks.hook_handler import HookHandler
    from click_extended.hooks.hook_node import HookNode
    from click_extended.hooks.hook_phase import HookPhase


class HookRegistry:
    """Registry of hook handlers."""

    def __init__(self) -> None:
        """Initialize a new hook registry."""
        self._hooks: list[HookNode] = []
        self._async_loop: asyncio.AbstractEventLoop | None = None

    def register(
        self,
        phase: "HookPhase",
        handler: "HookHandler",
        *,
        scope: "RootNode | None" = None,
        include: tuple[ExceptionType, ...] | None = None,
        exclude: tuple[ExceptionType, ...] | None = None,
    ) -> "HookNode":
        """
        Register a hook handler.

        :param phase: Lifecycle phase to register the hook for.
        :param handler: Hook handler callable.
        :param scope: Root node scope, or None for global.
        :param include: Exception types to include.
        :param exclude: Exception types to exclude.
        :returns: The registered hook node.
        """
        from click_extended.hooks.hook_node import HookNode

        node = HookNode(
            phase=phase,
            handler=handler,
            scope=scope,
            include=include,
            exclude=exclude,
        )
        self._hooks.append(node)
        return node

    def unregister(self, node: "HookNode") -> None:
        """
        Remove a previously registered hook node.

        :param node: Hook node to remove.
        """
        try:
            self._hooks.remove(node)
        except ValueError:
            pass

    def iter_hooks(
        self, phase: "HookPhase", root: "RootNode"
    ) -> list["HookNode"]:
        """
        Return ordered hooks for the given phase and root.

        Ordering is scoped-first (most specific) and bottom-up within
        each scope.

        :param phase: Lifecycle phase to filter by.
        :param root: Root node to resolve scope against.
        :returns: Ordered hook nodes to execute.
        """
        scoped = [
            hook
            for hook in self._hooks
            if hook.phase == phase and hook.scope is root
        ]
        global_hooks = [
            hook
            for hook in self._hooks
            if hook.phase == phase and hook.scope is None
        ]
        return list(reversed(scoped)) + list(reversed(global_hooks))

    def run(
        self,
        phase: "HookPhase",
        click_context: click.Context,
        root: "RootNode",
        *,
        context: "Context | None" = None,
        exception: BaseException | None = None,
    ) -> None:
        """
        Execute all hooks for the given phase.

        :param phase: Lifecycle phase to run.
        :param click_context: Active Click context.
        :param root: Root node of the CLI.
        :param context: click-extended context, if available.
        :param exception: Exception that triggered the hook, if any.
        """
        from click_extended.hooks.hook_event import HookEvent
        from click_extended.hooks.hook_phase import HookPhase

        for hook in self.iter_hooks(phase, root):
            hook_context = context if hook.scope is not None else None
            event = HookEvent(
                phase=phase,
                click_context=click_context,
                root=hook.scope,
                context=hook_context,
                exception=exception,
            )
            if phase == HookPhase.ERROR:
                if exception is None:
                    continue
                if not self._matches_exception(exception, hook):
                    continue

            self._invoke_handler(hook.handler, event, phase)

        if phase == HookPhase.EXIT:
            self._close_async_loop()

    @staticmethod
    def _matches_exception(exception: BaseException, hook: "HookNode") -> bool:
        include = hook.include
        exclude = hook.exclude

        if include is not None:
            if len(include) == 0:
                return False
            if not isinstance(exception, include):
                return False

        if exclude and isinstance(exception, exclude):
            return False

        return True

    def _invoke_handler(
        self, handler: "HookHandler", event: "HookEvent", phase: "HookPhase"
    ) -> None:
        try:
            if asyncio.iscoroutinefunction(handler):
                loop = self._get_async_loop()
                loop.run_until_complete(handler(event))
            else:
                handler(event)
        except RuntimeError as exc:
            if "already running" in str(exc).lower():
                from click_extended.errors import ProcessError

                raise ProcessError(
                    "Cannot use async hook handlers in an existing event loop.",
                    tip=(
                        "Use synchronous hooks or run the CLI outside async "
                        "contexts."
                    ),
                ) from exc
            raise
        except Exception:
            from click_extended.hooks.hook_phase import HookPhase

            if phase in (HookPhase.ERROR, HookPhase.EXIT):
                click.echo(
                    f"Hook handler failed during {phase.value} phase.",
                    err=True,
                )
            else:
                raise

    def _get_async_loop(self) -> asyncio.AbstractEventLoop:
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        if running_loop is not None:
            from click_extended.errors import ProcessError

            raise ProcessError(
                "Cannot use async hook handlers in an existing event loop.",
                tip=(
                    "Use synchronous hooks or run the CLI outside async "
                    "contexts."
                ),
            )

        if self._async_loop is None or self._async_loop.is_closed():
            self._async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._async_loop)

        return self._async_loop

    def _close_async_loop(self) -> None:
        if self._async_loop is None:
            return

        if not self._async_loop.is_closed():
            self._async_loop.close()

        self._async_loop = None


_REGISTRY = HookRegistry()


def get_registry() -> HookRegistry:
    """Return the singleton hook registry."""
    return _REGISTRY
