"""Utility for converting a string to snake_case."""

import re


def to_snake_case(value: str) -> str:
    """
    Convert a string to snake_case.

    Args:
        value (str):
            The input string.

    Returns:
        str:
            The `snake_case` version of the input string.
    """
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"(_+)", "_", value)
    return value.strip("_")
