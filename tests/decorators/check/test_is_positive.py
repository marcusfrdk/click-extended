from unittest.mock import Mock

import pytest

from click_extended.core.other.context import Context
from click_extended.decorators.check.is_positive import IsPositive


def test_is_positive_int() -> None:
    node = IsPositive(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1, ctx) == 1
    with pytest.raises(ValueError, match="Value '0' is not positive."):
        node.handle_numeric(0, ctx)
    with pytest.raises(ValueError, match="Value '-1' is not positive."):
        node.handle_numeric(-1, ctx)


def test_is_positive_float() -> None:
    node = IsPositive(name="test")
    ctx = Mock(spec=Context)
    assert node.handle_numeric(1.5, ctx) == 1.5
    with pytest.raises(ValueError, match="Value '0.0' is not positive."):
        node.handle_numeric(0.0, ctx)
    with pytest.raises(ValueError, match="Value '-1.5' is not positive."):
        node.handle_numeric(-1.5, ctx)
