"""Parent node for generating a random floating point value."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import random
from typing import Any

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomFloat(ParentNode):
    """Parent node for generating random floating point values."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> float:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        if kwargs["max_value"] < kwargs["min_value"]:
            raise ValueError("min_value can not be larger than max_value.")

        value = random.uniform(kwargs["min_value"], kwargs["max_value"])
        return float(round(value, kwargs["decimals"]))


def random_float(
    name: str,
    min_value: float = 0.0,
    max_value: float = 1.0,
    decimals: int = 3,
    seed: int | None = None,
) -> Decorator:
    """
    Generate a random floating point values.

    Type: `ParentNode`

    :param name: The name of the parent node.
    :param min_value: The lower value in the range. Defaults to 0.0.
    :param max_value: The upper value in the range. Defaults to 1.0.
    :param decimals: The number of decimal places to round to. Defaults to 3.
    :param seed: Optional seed for reproducible randomness.
    :returns: The decorator function.
    :rtype: Decorator
    """
    return RandomFloat.as_decorator(
        name=name,
        min_value=min_value,
        max_value=max_value,
        decimals=decimals,
        seed=seed,
    )
