"""Debug GlobalNode for enabling debug mode."""

from click_extended.core.context import Context
from click_extended.core.global_node import GlobalNode
from click_extended.types import Decorator


class Debug(GlobalNode):
    """
    Global node that enables debug mode, this can also be done by setting the
    `CLICK_EXTENDED_DEBUG=1` environment variable.

    When applied as a decorator, this enables full traceback display and
    more detailed errors for exceptions. Always runs first
    before any other processing.

    Example:
        ```python
        from click_extended import command, option
        from click_extended.globals import debug

        @command()
        @debug()
        @option("--value", type=int)
        def cli(value: int):
            # If a handler raises an exception, full traceback will be shown
            ...
        ```
    """

    def handle(self, context: Context) -> None:
        """
        Enable debug mode in the context.

        Args:
            context (Context):
                The execution context. Modifies the metadata to set
                debug=True for all subsequent processing.
        """
        meta = context.click_context.meta.get("click_extended", {})
        meta["debug"] = True


def debug() -> Decorator:
    """
    Decorator to enable debug mode for a context. This decorator can be placed
    anywhere in the stack, as it will run in the initialization phase.

    When debug mode is enabled, handler exceptions will show full tracebacks
    including the value being processed among other values.
    This is useful during development but should typically be
    disabled in production.

    Debugging can also globally be enabled by setting the
    `CLICK_EXTENDED_DEBUG=1` environment variable.

    Returns:
        Decorator:
            A decorator function that registers the debug global node.

    Example:
        ```python
        from click_extended import command, option
        from click_extended.globals import debug

        @command()
        @debug()
        @option("--value", type=int)
        def cli(value: int):
            pass
        ```
    """
    return Debug.as_decorator(run="first")
