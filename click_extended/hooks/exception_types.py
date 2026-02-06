"""Exception type aliases for hooks."""

from __future__ import annotations

from typing import Iterable, TypeAlias

ExceptionType: TypeAlias = type[BaseException]
ExceptionFilter: TypeAlias = ExceptionType | Iterable[ExceptionType] | None
