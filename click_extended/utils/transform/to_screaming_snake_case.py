"""Utility for converting a string to SCREAMING_SNAKE_CASE."""

from click_extended.utils.transform.to_snake_case import to_snake_case


def to_screaming_snake_case(value: str) -> str:
    """
    Convert a string to SCREAMING_SNAKE_CASE.

    Args:
        value (str):
            The string to transform.

    Returns:
        str:
            The transformed string.
    """
    return to_snake_case(value).upper()
