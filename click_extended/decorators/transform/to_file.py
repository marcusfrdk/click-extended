"""Convert a string to a `pathlib.Path` object for files only."""

# pylint: disable=too-many-arguments

from click_extended.decorators.transform.to_path import ToPath
from click_extended.types import Decorator


class ToFile(ToPath):
    """
    Convert a string to a `pathlib.Path` object, ensuring it's a file.

    This is a specialized version of ToPath pre-configured to only allow files.
    """


def to_file(
    *,
    exists: bool = True,
    parents: bool = False,
    resolve: bool = True,
    extensions: list[str] | None = None,
    allow_empty_file: bool = True,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator:
    """
    Convert, validate, and process a string to a ``pathlib.Path`` file.

    Type: `ChildNode`

    Supports: `str`, `Path`

    :param exists: Whether the file needs to exist. Defaults to ``True``.
    :param parents: Create parent directories if they don't exist. Defaults to
        ``False``.
    :param resolve: Convert the path to an absolute path. When ``True``,
        resolves ``.`` and ``..`` components. When False, only makes the path
        absolute without resolution. Defaults to ``True``.
    :param extensions: A list of extensions to require the file to end with.
        By default, all extensions are allowed.

        ```python
        extensions=[".py", ".pyx"]  # Only Python files
        extensions=[".txt"]         # Only text files
        ```

    :param allow_empty_file: Whether to allow the file to be empty (0 bytes).
        Defaults to ``True``.
    :param include_pattern: A whitelist pattern. Uses shell-style glob patterns.
        Defaults to ``None`` (All file names allowed).

        When both ``include_pattern`` and ``exclude_pattern`` are provided,
        ``include_pattern`` takes precedence (files matching include
        are always accepted).

        ```python
        include_pattern="*.py"      # Only Python files
        include_pattern="config_*"  # Files starting with "config_"
        ```

    :param exclude_pattern: A blacklist pattern. Uses shell-style glob patterns.
        Defaults to ``None`` (No file names excluded).

        If provided without ``include_pattern``, file names matching this
        pattern will be rejected, and all other file names will be
        allowed.

        When both ``include_pattern`` and ``exclude_pattern`` are provided,
        ``include_pattern`` takes precedence (files matching include
        are always accepted).

    :param is_readable: Whether the file has ``read`` permissions. Defaults to
        ``False``.
    :param is_writable: Whether the file has ``write`` permissions. Default to
        ``False``.
    :param is_executable: A unix-only feature that checks if the file has
        ``execute`` permissions. Defaults to ``False``.
    :returns: The decorated function.
    :rtype: Decorator
    """
    return ToFile.as_decorator(
        exists=exists,
        parents=parents,
        resolve=resolve,
        extensions=extensions,
        include_pattern=include_pattern,
        exclude_pattern=exclude_pattern,
        allow_file=True,
        allow_directory=False,
        allow_empty_directory=True,
        allow_empty_file=allow_empty_file,
        allow_symlink=False,
        follow_symlink=True,
        is_readable=is_readable,
        is_writable=is_writable,
        is_executable=is_executable,
    )
