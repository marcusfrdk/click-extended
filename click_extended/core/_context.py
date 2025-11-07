"""Context holding information about the execution environment."""

from typing import Any


class Context:
    """Context holding information about the execution environment.

    Contains main context data from Command/Group and parent context data
    from Option/Argument/Env/Tag decorators.
    """

    def __init__(self) -> None:
        """Initialize a new Context instance."""
        self.main: dict[str, Any] = {}
        self.parents: list[dict[str, Any]] = []
        self.values: dict[str, Any] = {}
        self.tags: dict[str, list[str]] = {}

    def __str__(self) -> str:
        return f"Context(main={self.main}, parents={len(self.parents)}, values={len(self.values)})"

    def __repr__(self) -> str:
        return f"<Context main={self.main} parents={self.parents}>"
