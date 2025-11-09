"""Exception for when an invalid command type is provided."""

from click_extended.errors.click_extended_error import ClickExtendedError


class InvalidCommandTypeError(ClickExtendedError):
    """Exception for when a raw Click command is used instead of click-extended."""

    def __init__(self, cmd_type: str):
        """
        Initialize a new `InvalidCommandTypeError`.

        Args:
            cmd_type (str):
                The type of the invalid command.
        """
        msg = (
            f"Cannot add {cmd_type} to group. "
            "Please use @command or @group decorators from click_extended "
            "instead of raw Click commands."
        )
        super().__init__(msg)
