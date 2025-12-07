from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.math.absolute import Absolute


def test_absolute_int() -> None:
    node = Absolute(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1, ctx) == 1
    assert node.handle_numeric(-1, ctx) == 1
    assert node.handle_numeric(0, ctx) == 0


def test_absolute_float() -> None:
    node = Absolute(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1.5, ctx) == 1.5
    assert node.handle_numeric(-1.5, ctx) == 1.5
    assert node.handle_numeric(0.0, ctx) == 0.0
