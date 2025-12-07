from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.math.minimum import Minimum


def test_minimum_int() -> None:
    node = Minimum(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(5, ctx, min_val=0) == 5
    assert node.handle_numeric(-1, ctx, min_val=0) == 0


def test_minimum_float() -> None:
    node = Minimum(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(5.5, ctx, min_val=0.0) == 5.5
    assert node.handle_numeric(-1.5, ctx, min_val=0.0) == 0.0
