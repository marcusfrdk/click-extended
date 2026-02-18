"""Convert a string to a `pathlib.Path` object for symlinks only."""

# pylint: disable=too-many-arguments

from click_extended.decorators.transform.to_path import ToPath
from click_extended.types import Decorator


class ToSymlink(ToPath):
    """
    Convert a string to a `pathlib.Path` object, ensuring it's a symlink.
    """


def to_symlink(
    *,
    exists: bool = True,
    resolve: bool = False,
    follow_symlink: bool = False,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator:
    """
    Convert, validate, and process a string to a `pathlib.Path` symlink.

    This decorator is pre-configured to only accept symlinks:
    - `allow_symlink=True`
    - `allow_file=True` (the symlink target can be a file)
    - `allow_directory=True` (the symlink target can be a directory)

    Type: `ChildNode`

    Supports: `str`, `Path`

    Args:
        exists (bool, optional):
            Whether the symlink needs to exist.
            Defaults to `True`.

        resolve (bool, optional):
            Convert the path to an absolute path. When `True`, resolves
            `.` and `..` components and follows the symlink if
            `follow_symlink=True`.
            Defaults to `False` (to preserve symlink).

        follow_symlink (bool, optional):
            Whether to follow the symlink when resolving the path.
            Only applies when `resolve=True`.
            Defaults to `False` (to preserve symlink).

        is_readable (bool, optional):
            Whether the symlink has `read` permissions.
            Defaults to `False`.

        is_writable (bool, optional):
            Whether the symlink has `write` permissions.
            Default to `False`.

        is_executable (bool, optional):
            A unix-only feature that checks if the symlink has
            `execute` permissions. Defaults to `False`.

    Returns:
        Decorator:
            The decorated function.
    """
    return ToSymlink.as_decorator(
        exists=exists,
        parents=False,
        resolve=resolve,
        extensions=None,
        include_pattern=None,
        exclude_pattern=None,
        allow_file=True,
        allow_directory=True,
        allow_empty_directory=True,
        allow_empty_file=True,
        allow_symlink=True,
        follow_symlink=follow_symlink,
        is_readable=is_readable,
        is_writable=is_writable,
        is_executable=is_executable,
    )
