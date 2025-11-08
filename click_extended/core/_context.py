"""Context holding information about the execution environment."""

from typing import Any

from click_extended.core._failure import Failure


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
        self.failures: list[Failure] = []

    def __str__(self) -> str:
        return (
            f"Context(main={self.main}, parents={len(self.parents)}, "
            f"values={len(self.values)})"
        )

    def __repr__(self) -> str:
        return f"<Context main={self.main} parents={self.parents}>"

    def add_failure(
        self, value: Any, message: str, parent_name: str | None = None
    ) -> None:
        """Add a failure with automatic parent tracking."""
        if parent_name is None and self.parents:
            parent_name = self.parents[-1].get("name")

        self.failures.append(Failure(value, message, parent_name))
