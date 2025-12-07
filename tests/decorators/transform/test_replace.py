from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.transform.replace import Replace


def test_replace() -> None:
    node = Replace(name="test")
    ctx = Mock(spec=Context)

    assert (
        node.handle_str("foo baz foo", ctx, old="foo", new="bar", count=-1)
        == "bar baz bar"
    )
    assert (
        node.handle_str("foo baz foo", ctx, old="foo", new="bar", count=1)
        == "bar baz foo"
    )
    assert node.handle_str("baz", ctx, old="foo", new="bar", count=-1) == "baz"
