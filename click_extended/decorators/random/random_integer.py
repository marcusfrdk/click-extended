"""Parent node for generating a random integer."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import random
from typing import Any

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomInteger(ParentNode):
    """Parent node for generating random integers."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> int:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        if kwargs["max_value"] < kwargs["min_value"]:
            raise ValueError("min_value can not be larger than max_value.")
        return random.randint(kwargs["min_value"], kwargs["max_value"])


def random_integer(
    name: str,
    min_value: int = 0,
    max_value: int = 100,
    seed: int | None = None,
) -> Decorator:
    """
    Generate a random integers.

    Type: `ParentNode`

    :param name: The name of the parent node.
    :param min_value: The lower value in the range. Defaults to 0.
    :param max_value: The upper value in the range. Defaults to 100.
    :param seed: Optional seed for reproducible randomness.
    :returns: The decorator function.
    :rtype: Decorator
    """
    return RandomInteger.as_decorator(
        name=name,
        min_value=min_value,
        max_value=max_value,
        seed=seed,
    )
