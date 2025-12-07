from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.math.clamp import Clamp


def test_clamp_int() -> None:
    node = Clamp(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(5, ctx, min_val=0, max_val=10) == 5
    assert node.handle_numeric(-1, ctx, min_val=0, max_val=10) == 0
    assert node.handle_numeric(11, ctx, min_val=0, max_val=10) == 10


def test_clamp_float() -> None:
    node = Clamp(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(5.5, ctx, min_val=0.0, max_val=10.0) == 5.5
    assert node.handle_numeric(-1.5, ctx, min_val=0.0, max_val=10.0) == 0.0
    assert node.handle_numeric(11.5, ctx, min_val=0.0, max_val=10.0) == 10.0


def test_clamp_partial() -> None:
    node_min = Clamp(name="test")
    ctx = Mock(spec=Context)
    assert node_min.handle_numeric(-1, ctx, min_val=0, max_val=None) == 0
    assert node_min.handle_numeric(100, ctx, min_val=0, max_val=None) == 100

    node_max = Clamp(name="test")
    assert node_max.handle_numeric(-100, ctx, max_val=10, min_val=None) == -100
    assert node_max.handle_numeric(11, ctx, max_val=10, min_val=None) == 10
