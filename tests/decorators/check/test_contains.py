from unittest.mock import Mock

import pytest

from click_extended.core.other.context import Context
from click_extended.decorators.check.contains import Contains


def test_contains_any() -> None:
    node = Contains(name="test")
    ctx = Mock(spec=Context)

    assert node.handle_str("foo", ctx, "foo", "bar", all=False) == "foo"
    assert node.handle_str("bar", ctx, "foo", "bar", all=False) == "bar"
    assert node.handle_str("foobar", ctx, "foo", "bar", all=False) == "foobar"

    with pytest.raises(
        ValueError,
        match="Value 'baz' does not contain any of the required substrings",
    ):
        node.handle_str("baz", ctx, "foo", "bar", all=False)


def test_contains_all() -> None:
    node = Contains(name="test")
    ctx = Mock(spec=Context)

    assert node.handle_str("foobar", ctx, "foo", "bar", all=True) == "foobar"

    with pytest.raises(
        ValueError,
        match="Value 'foo' does not contain the required substring 'bar'",
    ):
        node.handle_str("foo", ctx, "foo", "bar", all=True)
