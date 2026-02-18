"""Convert a string to a `pathlib.Path` object for directories only."""

# pylint: disable=too-many-arguments

from click_extended.decorators.transform.to_path import ToPath
from click_extended.types import Decorator


class ToDirectory(ToPath):
    """
    Convert a string to a `pathlib.Path` object, ensuring it's a directory.
    """


def to_directory(
    *,
    exists: bool = True,
    parents: bool = False,
    resolve: bool = True,
    allow_empty_directory: bool = True,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator:
    """
    Convert, validate, and process a string to a `pathlib.Path` directory.

    This decorator is pre-configured to only accept directories:
    - `allow_file=False`
    - `allow_directory=True`
    - `allow_symlink=False`

    Type: `ChildNode`

    Supports: `str`, `Path`

    Args:
        exists (bool, optional):
            Whether the directory needs to exist.
            Defaults to `True`.

        parents (bool, optional):
            Create parent directories if they don't exist.
            Defaults to `False`.

        resolve (bool, optional):
            Convert the path to an absolute path. When `True`, resolves
            `.` and `..` components. When False, only makes the path
            absolute without resolution.
            Defaults to `True`.

        allow_empty_directory (bool, optional):
            Whether to allow the directory to be empty.
            Defaults to `True`.

        include_pattern (str, optional):
            A whitelist pattern. Uses shell-style glob patterns.
            Defaults to `None` (All directory names allowed).

            When both `include_pattern` and `exclude_pattern` are provided,
            `include_pattern` takes precedence (directories matching include
            are always accepted).

            ```python
            include_pattern="src_*"  # Directories starting with "src_"
            ```

        exclude_pattern (str, optional):
            A blacklist pattern. Uses shell-style glob patterns.
            Defaults to `None` (No directory names excluded).

            If provided without `include_pattern`, directory names matching
            this pattern will be rejected, and all other directory names will
            be allowed.

            When both `include_pattern` and `exclude_pattern` are provided,
            `include_pattern` takes precedence (directories matching include
            are always accepted).

        is_readable (bool, optional):
            Whether the directory has `read` permissions.
            Defaults to `False`.

        is_writable (bool, optional):
            Whether the directory has `write` permissions.
            Default to `False`.

        is_executable (bool, optional):
            A unix-only feature that checks if the directory has
            `execute` permissions. Defaults to `False`.

    Returns:
        Decorator:
            The decorated function.
    """
    return ToDirectory.as_decorator(
        exists=exists,
        parents=parents,
        resolve=resolve,
        extensions=None,
        include_pattern=include_pattern,
        exclude_pattern=exclude_pattern,
        allow_file=False,
        allow_directory=True,
        allow_empty_directory=allow_empty_directory,
        allow_empty_file=True,
        allow_symlink=False,
        follow_symlink=True,
        is_readable=is_readable,
        is_writable=is_writable,
        is_executable=is_executable,
    )
