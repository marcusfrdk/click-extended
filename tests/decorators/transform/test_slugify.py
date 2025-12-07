from unittest.mock import Mock, patch

from click_extended.core.other.context import Context
from click_extended.decorators.transform.slugify import Slugify


def test_slugify() -> None:
    node = Slugify(name="test")
    ctx = Mock(spec=Context)

    try:
        assert node.handle_str("Hello World", ctx) == "hello-world"
        assert node.handle_str("  Foo  Bar  ", ctx) == "foo-bar"
    except ImportError:
        with patch(
            "click_extended.decorators.transform.slugify.slugify"
        ) as mock_slugify:
            mock_slugify.return_value = "mock-slug"
            assert node.handle_str("Hello World", ctx) == "mock-slug"
            mock_slugify.assert_called_with("Hello World")


def test_slugify_kwargs() -> None:
    node = Slugify(name="test")
    ctx = Mock(spec=Context)

    try:
        assert (
            node.handle_str("Hello World", ctx, separator="_") == "hello_world"
        )
    except ImportError:
        with patch(
            "click_extended.decorators.transform.slugify.slugify"
        ) as mock_slugify:
            mock_slugify.return_value = "mock_slug"
            node.handle_str("Hello World", ctx, separator="_")
            mock_slugify.assert_called_with("Hello World", separator="_")
