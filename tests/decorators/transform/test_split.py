from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.transform.split import Split


def test_split() -> None:
    node = Split(name="test")
    ctx = Mock(spec=Context)

    assert node.handle_str("a,b,c", ctx, sep=",", maxsplit=-1) == [
        "a",
        "b",
        "c",
    ]
    assert node.handle_str("a,b,c", ctx, sep=",", maxsplit=1) == ["a", "b,c"]
    assert node.handle_str("abc", ctx, sep=",", maxsplit=-1) == ["abc"]
