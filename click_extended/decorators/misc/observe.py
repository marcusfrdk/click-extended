"""Child decorator to observe values without modifying them."""

import asyncio
import inspect
from typing import Any, Callable, Coroutine, cast

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class Observe(ChildNode):
    """Child decorator to observe values without modifying them."""

    def handle_all(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> Any:
        handler: (
            Callable[[Any], Any]
            | Callable[[Any, Context], Any]
            | Callable[[Any], Coroutine[Any, Any, Any]]
            | Callable[[Any, Context], Coroutine[Any, Any, Any]]
        ) = kwargs["handler"]

        sig = inspect.signature(handler)
        param_count = len(sig.parameters)

        if param_count == 1:
            if asyncio.iscoroutinefunction(handler):
                async_handler_one = cast(
                    Callable[[Any], Coroutine[Any, Any, Any]], handler
                )
                asyncio.run(async_handler_one(value))
            else:
                sync_handler_one = cast(Callable[[Any], Any], handler)
                sync_handler_one(value)
        elif param_count == 2:
            if asyncio.iscoroutinefunction(handler):
                async_handler_two = cast(
                    Callable[[Any, Context], Coroutine[Any, Any, Any]],
                    handler,
                )
                asyncio.run(async_handler_two(value, context))
            else:
                sync_handler_two = cast(Callable[[Any, Context], Any], handler)
                sync_handler_two(value, context)
        else:
            raise ValueError(
                "observe() handler must accept (value) or (value, context)."
            )

        return value


def observe(
    handler: (
        Callable[[Any], Any]
        | Callable[[Any, Context], Any]
        | Callable[[Any], Coroutine[Any, Any, Any]]
        | Callable[[Any, Context], Coroutine[Any, Any, Any]]
    ),
) -> Decorator:
    """
    Observe a value without modifying it.

    Type: `ChildNode`

    Supports: `Any`

    Args:
        handler (Callable[[Any], Any] | Callable[[Any, Context], Any]):
            Handler to observe the value. Accepts `(value)` or
            `(value, context)`.

    Returns:
        Decorator:
            The decorator function.

    Examples:
        ```python
        @command()
        @option("token")
        @observe(lambda v: print(f"Token seen: {v}"))
        def cmd(token: str) -> None:
            pass
        ```

        ```python
        @command()
        @option("path")
        @observe(lambda v, ctx: print(ctx.get_current_parent_as_parent().name))
        def cmd(path: str) -> None:
            pass
        ```
    """
    return Observe.as_decorator(handler=handler)


__all__ = ["observe", "Observe"]
