"""Convert datetime, date, or time objects to Unix timestamps."""

from datetime import date, datetime, time, timezone
from typing import Any, Literal

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.types import Decorator


class ToTimestamp(ChildNode):
    """Convert datetime, date, or time objects to Unix timestamps."""

    def handle_datetime(
        self, value: datetime, context: Context, *args: Any, **kwargs: Any
    ) -> int:
        unit = kwargs["unit"]

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        timestamp = value.timestamp()

        if unit == "s":
            return int(timestamp)

        if unit == "ms":
            return int(timestamp * 1000)

        if unit == "us":
            return int(timestamp * 1_000_000)

        return int(timestamp * 1_000_000_000)

    def handle_date(
        self, value: date, context: Context, *args: Any, **kwargs: Any
    ) -> int:
        dt = datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
        return self.handle_datetime(dt, context, *args, **kwargs)

    def handle_time(
        self, value: time, context: Context, *args: Any, **kwargs: Any
    ) -> int:
        today = datetime.now(timezone.utc).date()

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        dt = datetime.combine(today, value)
        return self.handle_datetime(dt, context, *args, **kwargs)

    def handle_flat_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[int, ...]:
        return tuple(
            self._handle_single(v, context, *args, **kwargs) for v in value
        )

    def handle_nested_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple(self._handle_single(v, context, *args, **kwargs) for v in t)
            for t in value
        )

    def _handle_single(
        self, value: Any, context: Context, *args: Any, **kwargs: Any
    ) -> int:
        """Handle a single value of any supported type."""
        if isinstance(value, datetime):
            return self.handle_datetime(value, context, *args, **kwargs)

        if isinstance(value, date):
            return self.handle_date(value, context, *args, **kwargs)

        if isinstance(value, time):
            return self.handle_time(value, context, *args, **kwargs)

        raise TypeError(
            "Expected datetime, date, or "
            f"time object, got {type(value).__name__}"
        )


def to_timestamp(unit: Literal["s", "ms", "us", "ns"] = "s") -> Decorator:
    """
    Convert datetime, date, or time objects to Unix timestamps.

    Type: `ChildNode`

    Supports: `datetime`, `date`, `time`, `flat tuple`, `nested tuple`

    Args:
        unit (Literal["s", "ms", "us", "ns"], optional):
            The unit of the timestamp:
            - `"s"`: Seconds (standard Unix timestamp)
            - `"ms"`: Milliseconds (JavaScript/Java style)
            - `"us"`: Microseconds (Python datetime precision)
            - `"ns"`: Nanoseconds (high-precision logging)
            Defaults to `"s"`.

    Returns:
        Decorator:
            The decorated function.

    Examples:
        Basic usage with datetime:

        ```python
        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp()
        def cmd(dt: int) -> None:
            click.echo(f"Timestamp: {dt}")
        ```

        With milliseconds for JavaScript:

        ```python
        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp("ms")
        def cmd(dt: int) -> None:
            click.echo(f"Milliseconds: {dt}")
        ```

        Multiple timestamps:

        ```python
        @command()
        @option("dates", default=None, nargs=3)
        @to_date()
        @to_timestamp()
        def cmd(dates: tuple[int, ...]) -> None:
            for ts in dates:
                click.echo(f"Timestamp: {ts}")
        ```
    """
    return ToTimestamp.as_decorator(unit=unit)
