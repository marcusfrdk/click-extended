"""Global node to visualize the tree of the root node."""

from click_extended.core.global_node import GlobalNode
from click_extended.types import Context, Decorator


class Visualize(GlobalNode):
    """
    Global node to visualize the tree of the root node



    Example:
        ```python
        from click_extended import command, option, argument
        from click_extended.globals import visualize

        @command()
        @argument("my_argument")
        @option("--value", type=int)
        @visualize()
        def cli(my_argument: str, value: int):
            pass

        # Output:
        # cli
        #   my_argument
        #   value
        ```
    """

    def handle(self, context: Context) -> None:
        context.root.tree.visualize()


def visualize() -> Decorator:
    """
    Visualize the tree structure of the root node. This decorator runs once all
    other decorators have executed.

    Returns:
        Decorator:
            The decorated function.
    """
    return Visualize.as_decorator(run="last")
