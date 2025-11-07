"""Debugging example."""

from click_extended.debug import debug


@debug
def my_function():
    """Example function."""


if __name__ == "__main__":
    my_function()  # type: ignore[return-value]
