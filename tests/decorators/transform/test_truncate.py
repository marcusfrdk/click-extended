from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.transform.truncate import Truncate


def test_truncate() -> None:
    node = Truncate(name="test")
    ctx = Mock(spec=Context)

    assert node.handle_str("hello", ctx, length=5, suffix="...") == "hello"
    assert (
        node.handle_str("hello world", ctx, length=5, suffix="...") == "he..."
    )
    assert node.handle_str("hi", ctx, length=5, suffix="...") == "hi"


def test_truncate_custom_suffix() -> None:
    node = Truncate(name="test")
    ctx = Mock(spec=Context)

    assert node.handle_str("hello world", ctx, length=5, suffix=".") == "hell."
