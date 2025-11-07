"""Class representing a command in the command line."""

from click_extended.core._parent import Parent


class Command(Parent):
    """Class representing a command in the command line."""


def command():
    """Command decorator."""
