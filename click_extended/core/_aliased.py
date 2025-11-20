"""Shared aliasing functionality for Click commands and groups."""

# pylint: disable=too-few-public-methods
# pylint: disable=no-value-for-parameter

from typing import TYPE_CHECKING, Any

import click

from click_extended.errors import ParameterError

if TYPE_CHECKING:
    from click_extended.core._root_node import ExtendedCommand, ExtendedGroup


class AliasedMixin:
    """Mixin that provides aliasing support for Click commands and groups."""

    name: str | None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize with alias support.

        Args:
            *args (Any):
                Positional arguments for the base class.
            **kwargs (Any):
                Keyword arguments for the base class.
                `aliases` is extracted and stored separately.
        """
        self.aliases: str | list[str] | None = kwargs.pop("aliases", None)
        super().__init__(*args, **kwargs)

    def _format_help_with_aliases(
        self,
        ctx: click.Context,
        formatter: click.HelpFormatter,
        base_format_help: Any,
    ) -> None:
        """
        Helper to format help text with aliases.

        Args:
            ctx (click.Context):
                The Click context.
            formatter (click.HelpFormatter):
                The formatter to write help text to.
            base_format_help (Any):
                The base class format_help method to call.
        """
        original_name = self.name

        if self.aliases:
            aliases_list = (
                [self.aliases]
                if isinstance(self.aliases, str)
                else self.aliases
            )
            valid_aliases = [a for a in aliases_list if a]
            if valid_aliases:
                self.name = f"{self.name} ({', '.join(valid_aliases)})"

        base_format_help(ctx, formatter)
        self.name = original_name


class AliasedCommand(AliasedMixin, click.Command):
    """
    A Click command that supports aliasing and custom error formatting.

    Note: Will use ExtendedCommand at runtime for custom error handling.
    """

    name: str | None

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Format help with aliases."""
        self._format_help_with_aliases(
            ctx,
            formatter,
            click.Command.format_help.__get__(self, type(self)),
        )

    def invoke(self, ctx: click.Context) -> Any:
        """Override invoke to catch and reformat Click parameter errors."""

        try:
            return super().invoke(ctx)
        except click.BadParameter as e:
            param_hint = None
            if e.param:
                param_hint = (
                    e.param.human_readable_name
                    if hasattr(e.param, "human_readable_name")
                    else e.param.name
                )
                if hasattr(e.param, "opts") and e.param.opts:
                    param_hint = e.param.opts[0]

            message = str(e).split(": ", 1)[-1] if ": " in str(e) else str(e)

            raise ParameterError(
                message=message, param_hint=param_hint, ctx=ctx
            ) from e

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: click.Context | None = None,
        **extra: Any,
    ) -> click.Context:
        """Override make_context to catch Click parameter errors."""
        try:
            return super().make_context(info_name, args, parent, **extra)
        except click.BadParameter as e:
            for key in [
                "allow_extra_args",
                "allow_interspersed_args",
                "ignore_unknown_options",
                "help_option_names",
                "token_normalize_func",
                "color",
            ]:
                extra.setdefault(key, None)
            ctx = click.Context(
                self, info_name=info_name, parent=parent, **extra
            )

            param_hint = None
            if e.param:
                if hasattr(e.param, "opts") and e.param.opts:
                    param_hint = e.param.opts[0]
                elif hasattr(e.param, "name"):
                    param_hint = str(e.param.name).upper()

            message = str(e).split(": ", 1)[-1] if ": " in str(e) else str(e)

            raise ParameterError(
                message=message, param_hint=param_hint, ctx=ctx
            ) from e

    def main(self, *args: Any, **kwargs: Any) -> Any:
        """Override main to catch Click exceptions during parameter parsing."""
        try:
            return super().main(*args, **kwargs)
        except click.BadParameter as e:
            ctx = click.get_current_context(silent=True)

            param_hint = None
            if e.param:
                if hasattr(e.param, "opts") and e.param.opts:
                    param_hint = e.param.opts[0]
                elif hasattr(e.param, "name"):
                    param_hint = str(e.param.name).upper()

            message = str(e).split(": ", 1)[-1] if ": " in str(e) else str(e)

            raise ParameterError(
                message=message, param_hint=param_hint, ctx=ctx
            ) from e


class AliasedGroup(AliasedMixin, click.Group):
    """
    A Click group that supports aliasing and custom error formatting.

    Note: Will use ExtendedGroup at runtime for custom error handling.
    """

    name: str | None

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Format help with aliases."""
        self._format_help_with_aliases(
            ctx,
            formatter,
            click.Group.format_help.__get__(self, type(self)),
        )

    def invoke(self, ctx: click.Context) -> Any:
        """Override invoke to catch and reformat Click parameter errors."""
        try:
            return super().invoke(ctx)
        except click.BadParameter as e:
            param_hint = None
            if e.param:
                param_hint = (
                    e.param.human_readable_name
                    if hasattr(e.param, "human_readable_name")
                    else e.param.name
                )
                if hasattr(e.param, "opts") and e.param.opts:
                    param_hint = e.param.opts[0]

            message = str(e).split(": ", 1)[-1] if ": " in str(e) else str(e)

            raise ParameterError(
                message=message, param_hint=param_hint, ctx=ctx
            ) from e

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: click.Context | None = None,
        **extra: Any,
    ) -> click.Context:
        """Override make_context to catch Click parameter errors."""

        try:
            return super().make_context(info_name, args, parent, **extra)
        except click.BadParameter as e:
            for key in [
                "allow_extra_args",
                "allow_interspersed_args",
                "ignore_unknown_options",
                "help_option_names",
                "token_normalize_func",
                "color",
            ]:
                extra.setdefault(key, None)
            ctx = click.Context(
                self, info_name=info_name, parent=parent, **extra
            )

            param_hint = None
            if e.param:
                if hasattr(e.param, "opts") and e.param.opts:
                    param_hint = e.param.opts[0]
                elif hasattr(e.param, "name"):
                    param_hint = str(e.param.name).upper()

            message = str(e).split(": ", 1)[-1] if ": " in str(e) else str(e)

            raise ParameterError(
                message=message, param_hint=param_hint, ctx=ctx
            ) from e

    def main(self, *args: Any, **kwargs: Any) -> Any:
        """Override main to catch Click exceptions during parameter parsing."""
        try:
            return super().main(*args, **kwargs)
        except click.BadParameter as e:
            ctx = click.get_current_context(silent=True)

            param_hint = None
            if e.param:
                if hasattr(e.param, "opts") and e.param.opts:
                    param_hint = e.param.opts[0]
                elif hasattr(e.param, "name"):
                    param_hint = str(e.param.name).upper()

            message = str(e).split(": ", 1)[-1] if ": " in str(e) else str(e)

            raise ParameterError(
                message=message, param_hint=param_hint, ctx=ctx
            ) from e

    def add_command(self, cmd: click.Command, name: str | None = None) -> None:
        """
        Add a command to the group, including its aliases.

        Args:
            cmd (click.Command):
                The command to add to the group.
            name (str, optional):
                The name to use for the command. If not provided, uses the
                command's default name.
        """
        super().add_command(cmd, name)

        aliases = getattr(cmd, "aliases", None)
        if aliases is not None:
            aliases_list = [aliases] if isinstance(aliases, str) else aliases
            for alias in aliases_list:
                if alias:
                    super().add_command(cmd, alias)

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Format the command list for display in help text.

        Args:
            ctx (click.Context):
                The Click context containing command information.
            formatter (click.HelpFormatter):
                The formatter to write command information to.
        """
        commands: dict[str, click.Command] = {}
        for name, cmd in self.commands.items():
            if name == cmd.name:
                aliases = getattr(cmd, "aliases", None)
                display_name = name

                if aliases is not None:
                    aliases_list = (
                        [aliases] if isinstance(aliases, str) else aliases
                    )
                    valid_aliases = [a for a in aliases_list if a]
                    if valid_aliases:
                        display_name = f"{name} ({', '.join(valid_aliases)})"

                commands[display_name] = cmd

        rows: list[tuple[str, str]] = [
            (name, cmd.get_short_help_str()) for name, cmd in commands.items()
        ]

        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)
