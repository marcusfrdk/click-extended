"""Convert between different byte units."""

from decimal import Decimal, getcontext
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator

getcontext().prec = 35

UNITS = {
    "B": Decimal("1"),
    "kB": Decimal("1000"),
    "MB": Decimal("1000") ** 2,
    "GB": Decimal("1000") ** 3,
    "TB": Decimal("1000") ** 4,
    "PB": Decimal("1000") ** 5,
    "EB": Decimal("1000") ** 6,
    "ZB": Decimal("1000") ** 7,
    "YB": Decimal("1000") ** 8,
    "RB": Decimal("1000") ** 9,
    "QB": Decimal("1000") ** 10,
    "KiB": Decimal("1024"),
    "MiB": Decimal("1024") ** 2,
    "GiB": Decimal("1024") ** 3,
    "TiB": Decimal("1024") ** 4,
    "PiB": Decimal("1024") ** 5,
    "EiB": Decimal("1024") ** 6,
    "ZiB": Decimal("1024") ** 7,
    "YiB": Decimal("1024") ** 8,
}


class ConvertByteSize(ChildNode):
    """Convert between different byte size units."""

    def handle_numeric(
        self,
        value: int | float,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> float:
        from_unit = kwargs["from_unit"]
        to_unit = kwargs["to_unit"]
        val = Decimal(str(value))

        if from_unit not in UNITS:
            raise ValueError(f"Unknown unit '{from_unit}'")
        if to_unit not in UNITS:
            raise ValueError(f"Unknown unit '{to_unit}'")

        bytes_val = val * UNITS[from_unit]
        return float(bytes_val / UNITS[to_unit])


def convert_byte_size(
    from_unit: Literal[
        "B",
        "kB",
        "MB",
        "GB",
        "TB",
        "PB",
        "EB",
        "ZB",
        "YB",
        "RB",
        "QB",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
    ],
    to_unit: Literal[
        "B",
        "kB",
        "MB",
        "GB",
        "TB",
        "PB",
        "EB",
        "ZB",
        "YB",
        "RB",
        "QB",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
    ],
) -> Decorator:
    """
    Convert between different byte units.

    Type: `ChildNode`

    Supports: `int`, `float`

    Units:
        - **B**: Bytes
        - **kB**: Kilobytes
        - **MB**: Megabytes
        - **GB**: Gigabytes
        - **TB**: Terabytes
        - **PB**: Petabytes
        - **EB**: Exabytes
        - **ZB**: Zettabytes
        - **YB**: Yottabytes
        - **RB**: Ronnabytes
        - **QB**: Quettabytes
        - **KiB**: Kibibytes
        - **MiB**: Mebibytes
        - **GiB**: Gibibytes
        - **TiB**: Tebibytes
        - **PiB**: Pebibytes
        - **EiB**: Exbibytes
        - **ZiB**: Zebibytes
        - **YiB**: Yobibytes

    Returns:
        Decorator:
            The decorated function.
    """
    return ConvertByteSize.as_decorator(from_unit=from_unit, to_unit=to_unit)
