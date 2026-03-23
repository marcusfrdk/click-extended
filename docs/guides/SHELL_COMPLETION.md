![Banner](../../assets/click-extended-documentation-banner.png)

# Shell Completion

`click-extended` provides opt-in shell completion via the `register_completion` function. Calling it on a command or group adds four flags that let users install, inspect, locate, or remove the completion script for their shell.

Supported shells: **Bash**, **Zsh**, **Fish**.

## Setup

Call `register_completion` once after defining your root command or group, before invoking it:

```python
from click_extended import group, register_completion

@group()
def cli() -> None:
    """My CLI."""

register_completion(cli)

if __name__ == "__main__":
    cli()
```

This adds four flags to `cli`:

| Flag                     | Description                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| `--show-completion`      | Print the shell completion script to stdout and exit.                                            |
| `--install-completion`   | Write the completion script to the appropriate location and update the shell rc file, then exit. |
| `--completion-path`      | Print the path where the completion script is (or would be) installed, then exit.                |
| `--uninstall-completion` | Remove the completion script and strip the entry from the shell rc file, then exit.              |

Both flags auto-detect the current shell from the `$SHELL` environment variable (Fish is also detected via `$FISH_VERSION`). Override by setting `SHELL` explicitly:

```bash
SHELL=/bin/zsh mycli --show-completion
```

## Installing Completion

For an installed CLI (via a `[project.scripts]` entry point) simply run:

```bash
mycli --install-completion
```

Output:

```txt
Installed Bash completion for 'mycli'.
```

Then reload your shell:

```bash
source ~/.bashrc   # bash
source ~/.zshrc    # zsh
# fish reloads automatically
```

After that, tab-completion is active:

```bash
mycli <TAB>
greet  send
```

### What gets written

| Shell | Completion script                        | Shell config change                                  |
| ----- | ---------------------------------------- | ---------------------------------------------------- |
| Bash  | `~/.bash_completions/<prog>.bash`        | `source` line + marker appended to `~/.bashrc`       |
| Zsh   | `~/.zsh/completions/_<prog>`             | `fpath` + `compinit` + marker appended to `~/.zshrc` |
| Fish  | `~/.config/fish/completions/<prog>.fish` | None as Fish auto-discovers files in this directory  |

Installation is **idempotent**: running `--install-completion` a second time detects the existing install and skips it.

## Finding the Script

`--completion-path` prints the path where the completion script is (or would be) installed, without reading or writing anything:

```bash
mycli --completion-path
# Example output:
/home/marcus/.bash_completions/mycli.bash
```

This is useful for inspecting or editing the script manually.

## Removing Completion

`--uninstall-completion` reverses everything `--install-completion` did:

```bash
mycli --uninstall-completion
# Uninstalled Bash completion for 'mycli'.
```

It deletes the completion script file and strips the marker line (and associated `source` line for Bash) from the shell rc file. Running it when nothing is installed is safe and silent.

## Printing the Script

`--show-completion` prints the raw script without installing anything, which is useful for inspection or manual setup:

```bash
mycli --show-completion
# Source it directly in the current session:
source <(mycli --show-completion)
```

## Aliases

Aliases registered on commands and groups are automatically included in completions and no extra configuration is needed. If `greet` has alias `gr`, both appear when pressing Tab:

```python
@cli.command(aliases=["gr"])
def greet() -> None:
    ...
```

```bash
mycli <TAB>
gr  greet  send
```

## Entry Points vs Local Scripts

`--install-completion` works best when the CLI is installed as an entry point (via `pip install`), because the `prog_name` used to register the completion matches the command name on `$PATH`.

For local scripts invoked as `python script.py`, the completion is keyed to `script.py`, which only fires when the script is called directly (executable + on `$PATH`). The recommended approach for development is an editable install:

```bash
pip install -e .
mycli --install-completion
```
