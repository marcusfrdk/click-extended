"""Class to inject environment variables into the context."""

from click_extended.core._parent import Parent


class Env(Parent):
    """Class to inject environment variables into the context."""


def env():
    """Environment variable decorator."""
