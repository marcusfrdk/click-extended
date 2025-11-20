"""Transformer decorator to convert a string to a Path."""

# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-arguments

import fnmatch
import os
from pathlib import Path

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.errors import ValidationError
from click_extended.types import Decorator


class AsPath(ChildNode):
    """Transformer decorator to convert a string to a Path."""

    def process(self, value: str | Path, context: ProcessContext) -> Path:
        exists = context.kwargs["exists"]
        parents = context.kwargs["parents"]
        extensions = context.kwargs["extensions"]
        include_pattern = context.kwargs["include_pattern"]
        exclude_pattern = context.kwargs["exclude_pattern"]
        allow_file = context.kwargs["allow_file"]
        allow_directory = context.kwargs["allow_directory"]
        allow_empty_directory = context.kwargs["allow_empty_directory"]
        allow_empty_file = context.kwargs["allow_empty_file"]
        allow_symlink = context.kwargs["allow_symlink"]
        follow_symlink = context.kwargs["follow_symlink"]
        is_readable = context.kwargs["is_readable"]
        is_writable = context.kwargs["is_writable"]
        is_executable = context.kwargs["is_executable"]

        path = Path(value) if isinstance(value, str) else value
        path = path.expanduser()
        path = path.resolve() if follow_symlink else path.absolute()

        # Symlinks
        if not allow_symlink and path.is_symlink():
            raise ValidationError(
                f"Path '{path}' is a symlink, but symlinks are not allowed."
            )

        # Existence
        if exists and not path.exists():
            raise ValidationError(f"Path '{path}' does not exist.")

        # Parents
        if parents and not path.parent.exists():
            raise ValidationError(
                f"Parent directory '{path.parent}' does not exist."
            )

        if path.exists():
            is_file = path.is_file()
            is_dir = path.is_dir()

            # File disallowed
            if is_file and not allow_file:
                raise ValidationError(
                    f"Path '{path}' is a file, but files are not allowed."
                )

            # Directory disallowed
            if is_dir and not allow_directory:
                raise ValidationError(
                    f"Path '{path}' is a directory, "
                    "but directories are not allowed."
                )

            # Check empty directory
            if is_dir and not allow_empty_directory:
                if not any(path.iterdir()):
                    raise ValidationError(
                        f"Directory '{path}' is empty, but empty directories "
                        f"are not allowed."
                    )

            # Check empty file
            if is_file and not allow_empty_file:
                if path.stat().st_size == 0:
                    raise ValidationError(
                        f"File '{path}' is empty, but empty files are not "
                        f"allowed."
                    )

            # Check permissions
            if is_readable and not os.access(path, os.R_OK):
                raise ValidationError(f"Path '{path}' is not readable.")

            if is_writable and not os.access(path, os.W_OK):
                raise ValidationError(f"Path '{path}' is not writable.")

            if is_executable and not os.access(path, os.X_OK):
                raise ValidationError(f"Path '{path}' is not executable.")

        # Check extensions
        if extensions and (not path.exists() or path.is_file()):
            if not any(path.name.endswith(ext) for ext in extensions):
                raise ValidationError(
                    f"Path '{path}' does not have an allowed extension. "
                    f"Allowed extensions: {', '.join(extensions)}"
                )

        # Patterns
        if include_pattern:
            if not fnmatch.fnmatch(path.name, include_pattern):
                raise ValidationError(
                    f"Path '{path}' does not match include pattern "
                    f"'{include_pattern}'."
                )
        elif exclude_pattern and fnmatch.fnmatch(path.name, exclude_pattern):
            raise ValidationError(
                f"Path '{path}' matches exclude pattern "
                f"'{exclude_pattern}'."
            )

        return path


def as_path(
    *,
    exists: bool = False,
    parents: bool = False,
    extensions: list[str] | None = None,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    allow_file: bool = True,
    allow_directory: bool = True,
    allow_empty_directory: bool = True,
    allow_empty_file: bool = True,
    allow_symlink: bool = False,
    follow_symlink: bool = True,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator:
    """
    Transform a string to a valid path.

    Args:
        exists (bool, optional):
            Whether the path needs to exist.
            Defaults to `True`.

        parents (bool, optional):
            Checks if parents exist.
            Defaults to `False`.

        extensions (list[str], optional):
            A list of extensions to require the path to end with.
            By default, all extensions are allowed.

        include_pattern (str, optional):
            A whitelist pattern. Uses shell-style glob patterns.
            Defaults to `None` (All file names allowed).

            When both `include_pattern` and `exclude_pattern` are provided,
            `include_pattern` takes precedence (files matching include
            are always accepted).

            ```python
            include_pattern="*.py"      # Only Python files
            include_pattern="config_*"  # Files starting with "config_"
            ```

        exclude_pattern (str, optional):
            A blacklist pattern. Uses shell-style glob patterns.
            Defaults to `None` (No file names excluded).

            If provided without `include_pattern`, file names matching this
            pattern will be rejected, and all other file names will be
            allowed.

            When both `include_pattern` and `exclude_pattern` are provided,
            `include_pattern` takes precedence (files matching include
            are always accepted).

        allow_file (bool, optional):
            Whether to allow the path to be a file or not.
            Defaults to `True`.

        allow_directory (bool, optional):
            Whether to allow the path to be a directory or not.
            Defaults to `True`.

        allow_empty_directory (bool, optional):
            If the path points to a directory, whether to allow
            the directory to be empty. Only checked when the path
            is a directory. Defaults to `True`.

        allow_empty_file (bool, optional):
            If the path points to a file, whether to allow the
            file to be empty. Only checked when the path is a file.
            Defaults to `True`.

        allow_symlink (bool, optional):
            Whether to allow the path to be a symlink or not.
            Defaults to `False`.

        follow_symlink (bool, optional):
            Whether to follow symlinks when resolving the path.
            Defaults to `True`.

        is_readable (bool, optional):
            Whether the file has `read` permissions.
            Defaults to `False`.

        is_writable (bool, optional):
            Whether the file has `write` permissions.
            Default to `False`.

        is_executable (bool, optional):
            A unix-only feature that checks if the file has
            `execute` permissions. Defaults to `False`.

    Returns:
        Decorator:
            The decorated function.
    """
    return AsPath.as_decorator(
        exists=exists,
        parents=parents,
        extensions=extensions,
        include_pattern=include_pattern,
        exclude_pattern=exclude_pattern,
        allow_file=allow_file,
        allow_directory=allow_directory,
        allow_empty_directory=allow_empty_directory,
        allow_empty_file=allow_empty_file,
        allow_symlink=allow_symlink,
        follow_symlink=follow_symlink,
        is_readable=is_readable,
        is_writable=is_writable,
        is_executable=is_executable,
    )
