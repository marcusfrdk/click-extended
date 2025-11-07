"""Class representing a group of commands in the command line."""

from click_extended.core._parent import Parent


class Group(Parent):
    """Class representing a group of commands in the command line."""


def group():
    """Group decorator."""
