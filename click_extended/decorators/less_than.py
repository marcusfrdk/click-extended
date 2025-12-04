"""Child decorator to validate that a value is less than a threshold."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.types import Decorator


class LessThan(ChildNode):
    """Child decorator to validate that a value is less than a threshold."""

    def handle_numeric(
        self,
        value: int | float | Decimal,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value > threshold:
                raise ValueError(
                    f"Value must be at most {threshold}, got {value}"
                )
        else:
            if value >= threshold:
                raise ValueError(
                    f"Value must be less than {threshold}, got {value}"
                )

    def handle_datetime(
        self,
        value: datetime,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value > threshold:
                raise ValueError(
                    f"Value must be at most {threshold}, got {value}"
                )
        else:
            if value >= threshold:
                raise ValueError(
                    f"Value must be less than {threshold}, got {value}"
                )

    def handle_date(
        self,
        value: date,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value > threshold:
                raise ValueError(
                    f"Value must be at most {threshold}, got {value}"
                )
        else:
            if value >= threshold:
                raise ValueError(
                    f"Value must be less than {threshold}, got {value}"
                )

    def handle_time(
        self,
        value: time,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        threshold = kwargs["threshold"]
        inclusive = kwargs["inclusive"]

        if inclusive:
            if value > threshold:
                raise ValueError(
                    f"Value must be at most {threshold}, got {value}"
                )
        else:
            if value >= threshold:
                raise ValueError(
                    f"Value must be less than {threshold}, got {value}"
                )

    def handle_flat_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for v in value:
            self._validate_single(v, context, *args, **kwargs)

    def handle_nested_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for item in value:
            if isinstance(item, tuple):
                self.handle_nested_tuple(
                    item, context, *args, **kwargs  # type: ignore
                )
            else:
                self._validate_single(item, context, *args, **kwargs)

    def _validate_single(
        self,
        value: Any,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if isinstance(value, bool):
            raise TypeError("Cannot compare boolean with threshold")

        if isinstance(value, int):
            self.handle_numeric(value, context, *args, **kwargs)
        elif isinstance(value, float):
            self.handle_numeric(value, context, *args, **kwargs)
        elif isinstance(value, Decimal):
            self.handle_numeric(value, context, *args, **kwargs)
        elif isinstance(value, datetime):
            self.handle_datetime(value, context, *args, **kwargs)
        elif isinstance(value, date):
            self.handle_date(value, context, *args, **kwargs)
        elif isinstance(value, time):
            self.handle_time(value, context, *args, **kwargs)
        else:
            raise TypeError(
                f"Cannot compare {type(value).__name__} with threshold"
            )


def less_than(
    threshold: int | float | Decimal | datetime | date | time,
    inclusive: bool = False,
) -> Decorator:
    """
    Validate that a value is less than a threshold.

    Type: `ChildNode`

    Supports: `int`, `float`, `Decimal`, `datetime`, `date`, `time`,
    `flat tuple`, `nested tuple`

    Args:
        value (int | float | Decimal | datetime | date | time):
            The threshold value to compare against.
        inclusive (bool):
            If `True`, allows values equal to threshold (<=).
            If `False`, requires values strictly less (<).
            Defaults to `False`.

    Raises:
        ValueError:
            If value is not less than (or at most) the threshold.
        TypeError:
            If value type cannot be compared with threshold.

    Examples:
        Basic numeric validation:

        >>> @command()
        >>> @option("age", type=int)
        >>> @less_than(100)
        >>> def cmd(age):
        ...     click.echo(f"Age: {age}")

        >>> # Valid: 99, 50, 0, -5
        >>> # Invalid: 100, 101, 200

        With inclusive parameter:

        >>> @command()
        >>> @option("percentage", type=float)
        >>> @less_than(100.0, inclusive=True)
        >>> def cmd(percentage):
        ...     click.echo(f"Percentage: {percentage}")

        >>> # Valid: 100.0, 99.9, 50.0, 0.0
        >>> # Invalid: 100.1, 150.0

        Datetime validation:

        >>> @command()
        >>> @option("deadline")
        >>> @to_date()
        >>> @less_than(date(2025, 12, 31), inclusive=True)
        >>> def cmd(deadline):
        ...     click.echo(f"Deadline: {deadline}")

        >>> # Valid: 2025-12-31, 2025-01-01, 2024-12-31
        >>> # Invalid: 2026-01-01, 2026-12-31

        Tuple validation:

        >>> @command()
        >>> @option("scores", type=int, multiple=True)
        >>> @less_than(100, inclusive=True)
        >>> def cmd(scores):
        ...     click.echo(f"Scores: {scores}")

        >>> # Valid: (90, 85, 100), (50, 60, 70)
        >>> # Invalid: (90, 101, 85), (100, 100, 105)
    """
    return LessThan.as_decorator(
        threshold=threshold,
        inclusive=inclusive,
    )
