"""Click Command class for integration with RootNode."""

import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from click_extended.core.nodes._root_node import RootNode


class ClickCommand(click.Command):
    """
    A Click Command that integrates with the ``RootNode``.

    This is a regular ``click.Command`` that works everywhere Click works,
    with built-in support for aliasing and ``click-extended`` features.
    """

    def __init__(
        self, *args: Any, root_instance: "RootNode | None" = None, **kwargs: Any
    ) -> None:
        """
        Initialize a new ``ClickCommand`` instance..

        :param \\*args:
            Positional arguments for ``click.Command``
        :param root_instance:
            The RootNode instance that manages this command
        :param \\*\\*kwargs:
            Keyword arguments for ``click.Command``
        """
        if root_instance is None:
            raise ValueError("root_instance is required for ClickCommand")

        self.root = root_instance
        self.aliases = root_instance.aliases

        kwargs.pop("aliases", None)
        super().__init__(*args, **kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """
        Format help text with aliases.

        :param ctx:
            The Click context.
        :param formatter:
            The Click help formatter instance.
        """
        original_name = self.name

        if self.aliases:
            self.name = self.root.format_name_with_aliases()

        super().format_help(ctx, formatter)
        self.name = original_name

    def main(
        self,
        args: Sequence[str] | None = None,
        prog_name: str | None = None,
        complete_var: str | None = None,
        standalone_mode: bool = True,
        **extra: Any,
    ) -> Any:
        """Invoke the command, suppressing the ``Aborted!`` message on abort."""
        try:
            return super().main(
                args, prog_name, complete_var, standalone_mode=False, **extra
            )
        except click.exceptions.Abort:
            sys.exit(1)
        except click.exceptions.Exit as exc:
            sys.exit(getattr(exc, "code", 1))
        except click.exceptions.ClickException as exc:
            exc.show()
            sys.exit(exc.exit_code)
