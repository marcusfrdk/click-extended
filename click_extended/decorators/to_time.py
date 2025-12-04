"""Child decorator to convert a string to a time."""

from datetime import datetime, time
from typing import Any

from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.types import Decorator
from click_extended.utils import humanize_iterable


def _normalize_format(fmt: str) -> str:
    """
    Convert simplified format strings to Python strptime format.

    Supports both Python strptime format (%H:%M:%S) and simplified
    format (HH:mm:SS).
    """
    if "%" in fmt:
        return fmt

    replacements = {
        "HH": "%H",
        "mm": "%M",
        "SS": "%S",
        "ss": "%S",
    }

    result = fmt
    for simple, strp in replacements.items():
        result = result.replace(simple, strp)

    return result


class ToTime(ChildNode):
    """Child decorator to convert a string to a time."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> time:
        formats = kwargs["formats"] or (
            "%H:%M:%S",
            "%H:%M",
            "%I:%M:%S %p",
            "%I:%M %p",
        )

        for fmt in formats:
            try:
                normalized_fmt = _normalize_format(fmt)

                dt = datetime.strptime(value, normalized_fmt)
                return dt.time()
            except ValueError:
                continue

        fmt_text = (
            "either of the formats" if len(formats) != 1 else "in the format"
        )
        raise ValueError(
            f"Invalid time '{value}', must be in "
            f"{fmt_text} {humanize_iterable(formats, sep='or')}"
        )

    def handle_flat_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[time, ...]:
        return tuple(
            self.handle_str(str(v), context, *args, **kwargs) for v in value
        )

    def handle_nested_tuple(
        self,
        value: tuple[Any, ...],
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return tuple(
            tuple(self.handle_str(str(v), context, *args, **kwargs) for v in t)
            for t in value
        )


def to_time(
    *formats: str,
) -> Decorator:
    """
    Convert a string to a time by trying multiple formats.

    Type: `ChildNode`

    Supports: `str`, `flat tuple`, `nested tuple`

    Args:
        *formats (str):
            One or more time format strings to try. Supports both Python
            strptime format (e.g., "%H:%M:%S", "%I:%M %p") and simplified format
            (e.g., "HH:mm:SS", "HH:mm"). The decorator will attempt each
            format in order until one succeeds. Defaults to `"%H:%M:%S"`,
            `"%H:%M"`, `"%I:%M:%S %p"`, and `"%I:%M %p"`.

    Returns:
        Decorator:
            The decorated function.

    Example:
        @to_time("HH:mm:SS", "HH:mm")
        # Or using Python strptime format:
        @to_time("%H:%M:%S", "%H:%M")
        def process_time(time_val: time):
            print(time_val)
    """
    return ToTime.as_decorator(formats=formats)
