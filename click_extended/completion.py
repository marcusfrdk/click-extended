"""Shell completion registration for click-extended CLIs."""

import os
from pathlib import Path
from typing import Any

import click
from click.shell_completion import get_completion_class

_SUPPORTED_SHELLS = ("bash", "zsh", "fish")

_UNSUPPORTED_SHELL_MSG = (
    "Could not detect a supported shell. "
    f"Supported shells: {', '.join(_SUPPORTED_SHELLS)}. "
    "Set $SHELL to one of these and try again."
)

_MARKER = "# click-extended:{prog_name}:completion"


def _comp_path(shell: str, prog_name: str) -> Path:
    """Return the path where the completion script is (or would be) installed."""
    if shell == "bash":
        return Path.home() / ".bash_completions" / f"{prog_name}.bash"
    if shell == "zsh":
        return Path.home() / ".zsh" / "completions" / f"_{prog_name}"
    if shell == "fish":
        return Path.home() / ".config" / "fish" / "completions" / f"{prog_name}.fish"
    raise click.ClickException(f"Shell {shell!r} is not supported for completion.")


def _detect_shell() -> str | None:
    """Detect the current shell from environment variables.

    Checks ``$FISH_VERSION`` first (set by Fish), then falls back to
    the basename of ``$SHELL``.  Returns ``None`` if the shell cannot
    be determined or is not supported.
    """
    if os.environ.get("FISH_VERSION"):
        return "fish"

    shell_path = os.environ.get("SHELL", "")
    if not shell_path:
        return None

    name = os.path.basename(shell_path)
    if name in _SUPPORTED_SHELLS:
        return name

    return None


def _generate_script(cmd: click.Command, shell: str, prog_name: str) -> str:
    """Generate a completion script using Click's built-in machinery."""
    cls = get_completion_class(shell)
    if cls is None:
        raise click.ClickException(f"Shell {shell!r} is not supported for completion.")

    comp = cls(cmd, {}, prog_name, f"_{prog_name.upper().replace('-', '_')}_COMPLETE")
    return comp.source()


def _install_bash(prog_name: str, script: str) -> None:
    """Install Bash completion for *prog_name*."""
    marker = _MARKER.format(prog_name=prog_name)

    rc_path = Path.home() / ".bashrc"
    if rc_path.exists() and marker in rc_path.read_text():
        click.echo(f"Bash completion for {prog_name!r} is already installed.")
        return

    comp_dir = Path.home() / ".bash_completions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    comp_file = comp_dir / f"{prog_name}.bash"
    comp_file.write_text(script)

    with rc_path.open("a") as f:
        f.write(f"\n{marker}\nsource {comp_file}\n")

    click.echo(f"Installed Bash completion for {prog_name!r}.")


def _install_zsh(prog_name: str, script: str) -> None:
    """Install Zsh completion for *prog_name*."""
    marker = _MARKER.format(prog_name=prog_name)

    rc_path = Path.home() / ".zshrc"
    if rc_path.exists() and marker in rc_path.read_text():
        click.echo(f"Zsh completion for {prog_name!r} is already installed.")
        return

    comp_dir = Path.home() / ".zsh" / "completions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    comp_file = comp_dir / f"_{prog_name}"
    comp_file.write_text(script)

    lines: list[str] = []
    if rc_path.exists():
        existing = rc_path.read_text()
        if str(comp_dir) not in existing:
            lines.append(f"fpath=({comp_dir} $fpath)")
        if "compinit" not in existing:
            lines.append("autoload -Uz compinit && compinit")
    else:
        lines.append(f"fpath=({comp_dir} $fpath)")
        lines.append("autoload -Uz compinit && compinit")

    with rc_path.open("a") as f:
        if lines:
            f.write("\n" + "\n".join(lines))
        f.write(f"\n{marker}\n")

    click.echo(f"Installed Zsh completion for {prog_name!r}.")


def _install_fish(prog_name: str, script: str) -> None:
    """Install Fish completion for *prog_name*."""
    comp_dir = Path.home() / ".config" / "fish" / "completions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    comp_file = comp_dir / f"{prog_name}.fish"

    if comp_file.exists() and comp_file.read_text() == script:
        click.echo(f"Fish completion for {prog_name!r} is already installed.")
        return

    comp_file.write_text(script)
    click.echo(f"Installed Fish completion for {prog_name!r}.")


_INSTALLERS: dict[str, Any] = {
    "bash": _install_bash,
    "zsh": _install_zsh,
    "fish": _install_fish,
}


def _uninstall_bash(prog_name: str) -> None:
    """Remove Bash completion for *prog_name*."""
    marker = _MARKER.format(prog_name=prog_name)
    comp_file = _comp_path("bash", prog_name)

    if comp_file.exists():
        comp_file.unlink()

    rc_path = Path.home() / ".bashrc"
    if rc_path.exists():
        lines = rc_path.read_text().splitlines(keepends=True)
        filtered = [
            line for line in lines if marker not in line and str(comp_file) not in line
        ]
        rc_path.write_text("".join(filtered))

    click.echo(f"Uninstalled Bash completion for {prog_name!r}.")


def _uninstall_zsh(prog_name: str) -> None:
    """Remove Zsh completion for *prog_name*."""
    marker = _MARKER.format(prog_name=prog_name)
    comp_file = _comp_path("zsh", prog_name)

    if comp_file.exists():
        comp_file.unlink()

    rc_path = Path.home() / ".zshrc"
    if rc_path.exists():
        lines = rc_path.read_text().splitlines(keepends=True)
        filtered = [line for line in lines if marker not in line]
        rc_path.write_text("".join(filtered))

    click.echo(f"Uninstalled Zsh completion for {prog_name!r}.")


def _uninstall_fish(prog_name: str) -> None:
    """Remove Fish completion for *prog_name*."""
    comp_file = _comp_path("fish", prog_name)

    if comp_file.exists():
        comp_file.unlink()

    click.echo(f"Uninstalled Fish completion for {prog_name!r}.")


_UNINSTALLERS: dict[str, Any] = {
    "bash": _uninstall_bash,
    "zsh": _uninstall_zsh,
    "fish": _uninstall_fish,
}


def _show_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Eager callback for ``--show-completion``."""
    if not value or ctx.resilient_parsing:
        return

    shell = _detect_shell()
    if shell is None:
        raise click.ClickException(_UNSUPPORTED_SHELL_MSG)

    prog_name = ctx.find_root().info_name or "cli"
    script = _generate_script(ctx.find_root().command, shell, prog_name)
    click.echo(script)
    ctx.exit()


def _install_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Eager callback for ``--install-completion``."""
    if not value or ctx.resilient_parsing:
        return

    shell = _detect_shell()
    if shell is None:
        raise click.ClickException(_UNSUPPORTED_SHELL_MSG)

    prog_name = ctx.find_root().info_name or "cli"
    script = _generate_script(ctx.find_root().command, shell, prog_name)
    _INSTALLERS[shell](prog_name, script)
    ctx.exit()


def _path_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Eager callback for ``--completion-path``."""
    if not value or ctx.resilient_parsing:
        return

    shell = _detect_shell()
    if shell is None:
        raise click.ClickException(_UNSUPPORTED_SHELL_MSG)

    prog_name = ctx.find_root().info_name or "cli"
    click.echo(_comp_path(shell, prog_name))
    ctx.exit()


def _uninstall_callback(
    ctx: click.Context, _param: click.Parameter, value: bool
) -> None:
    """Eager callback for ``--uninstall-completion``."""
    if not value or ctx.resilient_parsing:
        return

    shell = _detect_shell()
    if shell is None:
        raise click.ClickException(_UNSUPPORTED_SHELL_MSG)

    prog_name = ctx.find_root().info_name or "cli"
    _UNINSTALLERS[shell](prog_name)
    ctx.exit()


def register_completion(cmd: click.Command) -> None:
    """Register ``--show-completion`` and ``--install-completion``
    flags on *cmd*.

    Call this once after defining a command or group::

        @group()
        def cli():
            pass

        register_completion(cli)

    ``--show-completion`` prints the shell completion script to stdout.

    ``--install-completion`` writes the script to the appropriate
    shell config directory and updates the shell's rc file.

    The shell is auto-detected from ``$SHELL`` (override by setting
    ``SHELL=/bin/zsh mycli --install-completion``).
    """
    cmd.params.append(
        click.Option(
            ["--show-completion"],
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=_show_callback,
            help="Print the shell completion script and exit.",
        )
    )
    cmd.params.append(
        click.Option(
            ["--install-completion"],
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=_install_callback,
            help="Install shell completion and exit.",
        )
    )
    cmd.params.append(
        click.Option(
            ["--completion-path"],
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=_path_callback,
            help="Print the path where the completion script is installed and exit.",
        )
    )
    cmd.params.append(
        click.Option(
            ["--uninstall-completion"],
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=_uninstall_callback,
            help="Uninstall shell completion and exit.",
        )
    )
