from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.math.maximum import Maximum


def test_maximum_int() -> None:
    node = Maximum(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(5, ctx, max_val=10) == 5
    assert node.handle_numeric(11, ctx, max_val=10) == 10


def test_maximum_float() -> None:
    node = Maximum(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(5.5, ctx, max_val=10.0) == 5.5
    assert node.handle_numeric(11.5, ctx, max_val=10.0) == 10.0
