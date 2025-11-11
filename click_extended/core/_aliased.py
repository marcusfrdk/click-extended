"""Shared aliasing functionality for Click commands and groups."""

from typing import Any

import click


class AliasedMixin:
    """Mixin that provides aliasing support for Click commands and groups."""

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
    """A Click command that supports aliasing."""

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Format help with aliases."""
        self._format_help_with_aliases(
            ctx, formatter, click.Command.format_help.__get__(self, type(self))
        )


class AliasedGroup(AliasedMixin, click.Group):
    """A Click group that supports aliasing."""

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Format help with aliases."""
        self._format_help_with_aliases(
            ctx, formatter, click.Group.format_help.__get__(self, type(self))
        )

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
