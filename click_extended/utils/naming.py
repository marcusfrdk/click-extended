"""Utilities for validating and parsing naming conventions."""

import re

SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
SCREAMING_SNAKE_CASE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$")
KEBAB_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

LONG_FLAG_PATTERN = re.compile(r"^--[a-z][a-z0-9-]*$")
SHORT_FLAG_PATTERN = re.compile(r"^-[a-zA-Z]$")


def is_valid_name(name: str) -> bool:
    """
    Check if a name follows valid naming conventions.

    Valid conventions:

    - `snake_case`: my_option, config_file
    - `SCREAMING_SNAKE_CASE`: MY_OPTION, CONFIG_FILE
    - `kebab-case`: my-option, config-file

    Args:
        name (str):
            The name to validate.

    Returns:
        bool:
            `True` if the name is valid, `False` otherwise.
    """
    return bool(
        SNAKE_CASE_PATTERN.match(name)
        or SCREAMING_SNAKE_CASE_PATTERN.match(name)
        or KEBAB_CASE_PATTERN.match(name)
    )


def is_long_flag(value: str) -> bool:
    """
    Check if a value is a long flag (e.g., --option).

    Args:
        value (str):
            The value to check.

    Returns:
        `True` if the value is a long flag, `False` otherwise.
    """
    return bool(LONG_FLAG_PATTERN.match(value))


def is_short_flag(value: str) -> bool:
    """
    Check if a value is a short flag (e.g., -o).

    Args:
        value (str):
            The value to check.

    Returns:
        `True` if the value is a short flag, `False` otherwise.
    """
    return bool(SHORT_FLAG_PATTERN.match(value))


def validate_name(name: str, context: str = "name") -> None:
    """
    Validate a name follows naming conventions.

    Args:
        name (str):
            The name to validate.
        context (Context):
            Context string for error messages
            (e.g., "option name", "argument name").

    Raises:
        ValueError:
            If the name doesn't follow valid conventions.
    """
    if not is_valid_name(name):
        raise ValueError(
            f"Invalid {context} '{name}'. "
            f"Must follow one of these conventions:\n"
            f"  - snake_case (e.g., my_option, config_file)\n"
            f"  - SCREAMING_SNAKE_CASE (e.g., MY_OPTION, CONFIG_FILE)\n"
            f"  - kebab-case (e.g., my-option, config-file)"
        )


def parse_option_args(*args: str) -> tuple[str | None, str | None, str | None]:
    """
    Parse option decorator arguments intelligently.

    Supports three forms:

    1. **@option("my_option")**: name only
    2. **@option("--my-option")**: long flag (derives name)
    3. **@option("-m", "--my-option")**: short and long flags

    Args:
        *args (str):
            Positional arguments passed to `@option` decorator.

    Returns:
        Tuple of (name, short, long):

        - **name**: The parameter name (`None` if not provided)
        - **short**: The short flag (`None` if not provided)
        - **long**: The long flag (`None` if not provided)

    Raises:
        ValueError:
            If arguments are invalid or ambiguous.
    """

    if len(args) == 0:
        return None, None, None

    if len(args) == 1:
        arg = args[0]

        # @option("--my-option")
        if is_long_flag(arg):
            return None, None, arg

        # @option("-m")
        if is_short_flag(arg):
            raise ValueError(
                f"Short flag '{arg}' provided without long flag or name. "
                f"Use one of:\n"
                f"  @option('{arg}', '--flag')  # with long flag\n"
                f"  @option('name', short='{arg}')  # with name parameter"
            )

        # @option("my_option")
        validate_name(arg, "option name")
        return arg, None, None

    if len(args) == 2:
        first, second = args

        # @option("-m", "--my-option")
        if is_short_flag(first) and is_long_flag(second):
            return None, first, second

        # @option("--my-option", "-m")
        if is_long_flag(first) and is_short_flag(second):
            raise ValueError(
                "Invalid argument order. "
                "Short flag must come before long flag:\n"
                f"  Use: @option('{second}', '{first}')"
            )

        raise ValueError(
            f"Invalid arguments: '{first}', '{second}'. "
            f"Expected one of:\n"
            f"  @option('name')  # name only\n"
            f"  @option('--flag')  # long flag only\n"
            f"  @option('-f', '--flag')  # short and long flags"
        )

    raise ValueError(
        f"Too many positional arguments ({len(args)}). "
        f"Maximum is 2 (short and long flags)."
    )
