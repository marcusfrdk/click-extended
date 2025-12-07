from unittest.mock import Mock

import pytest

from click_extended.core.other.context import Context
from click_extended.decorators.check.is_non_zero import IsNonZero


def test_is_non_zero_int() -> None:
    node = IsNonZero(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1, ctx) == 1
    assert node.handle_numeric(-1, ctx) == -1
    with pytest.raises(ValueError, match="Value '0' is zero."):
        node.handle_numeric(0, ctx)


def test_is_non_zero_float() -> None:
    node = IsNonZero(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1.5, ctx) == 1.5
    assert node.handle_numeric(-1.5, ctx) == -1.5
    with pytest.raises(ValueError, match="Value '0.0' is zero."):
        node.handle_numeric(0.0, ctx)
