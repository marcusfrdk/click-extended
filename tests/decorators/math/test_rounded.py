from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.math.rounded import Rounded


def test_round_int() -> None:
    node = Rounded(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1, ctx, digits=0) == 1


def test_round_float() -> None:
    node = Rounded(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1.55, ctx, digits=1) == 1.6
    assert node.handle_numeric(1.54, ctx, digits=1) == 1.5

    node_0 = Rounded(name="test")
    assert node_0.handle_numeric(1.6, ctx, digits=0) == 2.0
