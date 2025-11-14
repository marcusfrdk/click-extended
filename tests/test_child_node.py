"""Test the ChildNode class."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from click_extended.core._child_node import ChildNode
from click_extended.core._node import Node
from click_extended.core.tag import Tag


class ConcreteChildNode(ChildNode):
    """Concrete ChildNode implementation for testing."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: dict[str, Tag],
        parent: Any,
        **kwargs: Any,
    ) -> Any:
        """Simple process that returns the value unchanged."""
        return value


class UppercaseNode(ChildNode):
    """ChildNode that uppercases string values."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: dict[str, Tag],
        parent: Any,
        **kwargs: Any,
    ) -> Any:
        """Convert value to uppercase."""
        return str(value).upper()


class MultiplyNode(ChildNode):
    """ChildNode that multiplies numeric values."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: dict[str, Tag],
        parent: Any,
        **kwargs: Any,
    ) -> Any:
        """Multiply value by the first arg or 2 if no args."""
        multiplier = args[0] if args else 2
        return value * multiplier


class PrefixNode(ChildNode):
    """ChildNode that adds a prefix to values."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: dict[str, Tag],
        parent: Any,
        **kwargs: Any,
    ) -> Any:
        """Add prefix from kwargs or default."""
        prefix = kwargs.get("prefix", "PREFIX: ")
        return f"{prefix}{value}"


class TestChildNodeInitialization:
    """Test ChildNode initialization."""

    def test_init_with_name_only(self) -> None:
        """Test initialization with only name parameter."""
        node = ConcreteChildNode(name="test_node")
        assert node.name == "test_node"
        assert node.process_args == ()
        assert node.process_kwargs == {}
        assert node.children is None

    def test_init_with_process_args(self) -> None:
        """Test initialization with process_args."""
        node = ConcreteChildNode(name="test_node", process_args=(1, 2, 3))
        assert node.name == "test_node"
        assert node.process_args == (1, 2, 3)
        assert node.process_kwargs == {}

    def test_init_with_process_kwargs(self) -> None:
        """Test initialization with process_kwargs."""
        node = ConcreteChildNode(
            name="test_node", process_kwargs={"key": "value", "number": 42}
        )
        assert node.name == "test_node"
        assert node.process_args == ()
        assert node.process_kwargs == {"key": "value", "number": 42}

    def test_init_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        node = ConcreteChildNode(
            name="test_node",
            process_args=(1, 2, 3),
            process_kwargs={"key": "value"},
        )
        assert node.name == "test_node"
        assert node.process_args == (1, 2, 3)
        assert node.process_kwargs == {"key": "value"}

    def test_init_with_none_args_defaults_to_empty_tuple(self) -> None:
        """Test that None process_args defaults to empty tuple."""
        node = ConcreteChildNode(name="test_node", process_args=None)
        assert node.process_args == ()
        assert isinstance(node.process_args, tuple)

    def test_init_with_none_kwargs_defaults_to_empty_dict(self) -> None:
        """Test that None process_kwargs defaults to empty dict."""
        node = ConcreteChildNode(name="test_node", process_kwargs=None)
        assert node.process_kwargs == {}
        assert isinstance(node.process_kwargs, dict)


class TestChildNodeGetMethod:
    """Test ChildNode.get() method."""

    def test_get_always_returns_none(self) -> None:
        """Test that get() always returns None."""
        node = ConcreteChildNode(name="test_node")
        assert node.get("any_name") is None  # type: ignore
        assert node.get("another_name") is None  # type: ignore
        assert node.get("") is None  # type: ignore

    def test_get_with_different_types(self) -> None:
        """Test get() with different name types."""
        node = ConcreteChildNode(name="test_node")
        assert node.get("string") is None  # type: ignore
        assert node.get("") is None  # type: ignore


class TestChildNodeGetItem:
    """Test ChildNode.__getitem__() method."""

    def test_getitem_raises_keyerror(self) -> None:
        """Test that __getitem__ raises KeyError."""
        node = ConcreteChildNode(name="test_node")
        with pytest.raises(KeyError) as exc_info:
            _ = node["child"]
        assert "A ChildNode instance has no children" in str(exc_info.value)

    def test_getitem_with_different_names(self) -> None:
        """Test __getitem__ raises KeyError for any name."""
        node = ConcreteChildNode(name="test_node")
        with pytest.raises(KeyError):
            _ = node["any_name"]
        with pytest.raises(KeyError):
            _ = node["another_name"]


class TestChildNodeAsDecorator:
    """Test ChildNode.as_decorator() classmethod."""

    @patch("click_extended.core._child_node.queue_child")
    def test_as_decorator_without_args(
        self, mock_queue_child: MagicMock
    ) -> None:
        """Test as_decorator without arguments."""
        decorator = ConcreteChildNode.as_decorator()

        def dummy_func() -> str:
            return "test"

        result = decorator(dummy_func)

        assert result is dummy_func
        assert result() == "test"

        assert mock_queue_child.called
        call_args = mock_queue_child.call_args[0]
        assert isinstance(call_args[0], ConcreteChildNode)
        assert call_args[0].name == "concrete_child_node"
        assert call_args[0].process_args == ()
        assert call_args[0].process_kwargs == {}

    @patch("click_extended.core._child_node.queue_child")
    def test_as_decorator_with_args(self, mock_queue_child: MagicMock) -> None:
        """Test as_decorator with positional arguments."""
        decorator = ConcreteChildNode.as_decorator(1, 2, 3)

        def dummy_func() -> str:
            return "test"

        result = decorator(dummy_func)

        assert result is dummy_func
        assert mock_queue_child.called
        call_args = mock_queue_child.call_args[0]
        assert call_args[0].process_args == (1, 2, 3)
        assert call_args[0].process_kwargs == {}

    @patch("click_extended.core._child_node.queue_child")
    def test_as_decorator_with_kwargs(
        self, mock_queue_child: MagicMock
    ) -> None:
        """Test as_decorator with keyword arguments."""
        decorator = ConcreteChildNode.as_decorator(key="value", number=42)

        def dummy_func() -> str:
            return "test"

        result = decorator(dummy_func)

        assert result is dummy_func
        assert mock_queue_child.called
        call_args = mock_queue_child.call_args[0]
        assert call_args[0].process_args == ()
        assert call_args[0].process_kwargs == {"key": "value", "number": 42}

    @patch("click_extended.core._child_node.queue_child")
    def test_as_decorator_with_mixed_args(
        self, mock_queue_child: MagicMock
    ) -> None:
        """Test as_decorator with both positional and keyword arguments."""
        decorator = ConcreteChildNode.as_decorator(1, 2, key="value")

        def dummy_func() -> str:
            return "test"

        result = decorator(dummy_func)

        assert result is dummy_func
        assert mock_queue_child.called
        call_args = mock_queue_child.call_args[0]
        assert call_args[0].process_args == (1, 2)
        assert call_args[0].process_kwargs == {"key": "value"}

    @patch("click_extended.core._child_node.queue_child")
    def test_as_decorator_creates_snake_case_name(
        self, mock_queue_child: MagicMock
    ) -> None:
        """Test that as_decorator converts class name to snake_case."""
        decorator = UppercaseNode.as_decorator()

        def dummy_func() -> None:
            pass

        decorator(dummy_func)

        call_args = mock_queue_child.call_args[0]
        assert call_args[0].name == "uppercase_node"

    @patch("click_extended.core._child_node.queue_child")
    def test_as_decorator_preserves_function_behavior(
        self, mock_queue_child: MagicMock
    ) -> None:
        """Test that decorator preserves original function behavior."""
        decorator = ConcreteChildNode.as_decorator()

        def add_numbers(a: int, b: int) -> int:
            return a + b

        decorated = decorator(add_numbers)

        assert decorated(2, 3) == 5
        assert decorated(10, 20) == 30


class TestChildNodeProcess:
    """Test ChildNode.process() abstract method."""

    def test_process_not_implemented_on_base_class(self) -> None:
        """Test that process() raises NotImplementedError on abstract class."""
        with pytest.raises(TypeError):
            ChildNode(name="test")  # type: ignore

    def test_concrete_implementation_must_implement_process(self) -> None:
        """Test that concrete implementations must implement process()."""

        class IncompleteChild(ChildNode):
            pass

        with pytest.raises(TypeError):
            IncompleteChild(name="test")  # type: ignore

    def test_process_with_simple_implementation(self) -> None:
        """Test process with simple implementation."""
        node = ConcreteChildNode(name="test")
        result = node.process("value", siblings=[], tags={}, parent=None)
        assert result == "value"

    def test_process_receives_all_parameters(self) -> None:
        """Test that process receives all expected parameters."""

        class InspectorNode(ChildNode):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.last_call: dict[str, Any] | None = None

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: dict[str, Tag],
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                self.last_call = {
                    "value": value,
                    "args": args,
                    "siblings": siblings,
                    "tags": tags,
                    "kwargs": kwargs,
                }
                return value

        node = InspectorNode(name="inspector")

        dummy_tag = Tag(name="tag1")
        dummy_tag.parent_nodes = []

        result = node.process(
            "test_value",
            "arg1",
            "arg2",
            siblings=["SiblingOne", "SiblingTwo"],
            tags={"tag1": dummy_tag},
            parent=None,
            custom_param="custom",
        )

        assert result == "test_value"
        assert node.last_call is not None
        assert node.last_call["value"] == "test_value"
        assert node.last_call["args"] == ("arg1", "arg2")
        assert node.last_call["siblings"] == ["SiblingOne", "SiblingTwo"]
        assert node.last_call["tags"] == {"tag1": dummy_tag}
        assert node.last_call["kwargs"] == {"custom_param": "custom"}


class TestConcreteImplementations:
    """Test concrete ChildNode implementations."""

    def test_uppercase_node(self) -> None:
        """Test UppercaseNode implementation."""
        node = UppercaseNode(name="uppercase")
        assert (
            node.process("hello", siblings=[], tags={}, parent=None) == "HELLO"
        )
        assert (
            node.process("world", siblings=[], tags={}, parent=None) == "WORLD"
        )
        assert node.process("", siblings=[], tags={}, parent=None) == ""

    def test_multiply_node_with_args(self) -> None:
        """Test MultiplyNode with process_args."""
        node = MultiplyNode(name="multiply", process_args=(3,))
        assert (
            node.process(
                5, *node.process_args, siblings=[], tags={}, parent=None
            )
            == 15
        )
        assert (
            node.process(
                10, *node.process_args, siblings=[], tags={}, parent=None
            )
            == 30
        )

    def test_multiply_node_without_args(self) -> None:
        """Test MultiplyNode without process_args (uses default)."""
        node = MultiplyNode(name="multiply")
        assert (
            node.process(
                5, *node.process_args, siblings=[], tags={}, parent=None
            )
            == 10
        )
        assert (
            node.process(
                7, *node.process_args, siblings=[], tags={}, parent=None
            )
            == 14
        )

    def test_prefix_node_with_kwargs(self) -> None:
        """Test PrefixNode with process_kwargs."""
        node = PrefixNode(name="prefix", process_kwargs={"prefix": ">>> "})
        result = node.process(
            "message", siblings=[], tags={}, parent=None, **node.process_kwargs
        )
        assert result == ">>> message"

    def test_prefix_node_without_kwargs(self) -> None:
        """Test PrefixNode without process_kwargs (uses default)."""
        node = PrefixNode(name="prefix")
        result = node.process("message", siblings=[], tags={}, parent=None)
        assert result == "PREFIX: message"

    def test_siblings_parameter(self) -> None:
        """Test that siblings parameter is properly passed."""

        class SiblingsInspectorNode(ChildNode):
            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: dict[str, Tag],
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                return f"Value: {value}, Siblings: {len(siblings)}"

        node = SiblingsInspectorNode(name="inspector")
        result = node.process(
            "test",
            siblings=["NodeOne", "NodeTwo", "NodeThree"],
            tags={},
            parent=None,
            tag=None,
        )
        assert result == "Value: test, Siblings: 3"


class TestChildNodeInheritance:
    """Test ChildNode inheritance from Node."""

    def test_childnode_is_node_subclass(self) -> None:
        """Test that ChildNode is a subclass of Node."""
        assert issubclass(ChildNode, Node)

    def test_childnode_instance_is_node_instance(self) -> None:
        """Test that ChildNode instance is also a Node instance."""
        node = ConcreteChildNode(name="test")
        assert isinstance(node, Node)
        assert isinstance(node, ChildNode)

    def test_childnode_has_name_attribute(self) -> None:
        """Test that ChildNode inherits name attribute from Node."""
        node = ConcreteChildNode(name="my_node")
        assert hasattr(node, "name")
        assert node.name == "my_node"

    def test_childnode_children_always_none(self) -> None:
        """Test that ChildNode.children is always None."""
        node = ConcreteChildNode(name="test")
        assert node.children is None

        node2 = ConcreteChildNode(name="test2")
        assert node2.children is None


class TestChildNodeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_process_with_empty_siblings(self) -> None:
        """Test process with empty siblings list."""
        node = ConcreteChildNode(name="test")
        result = node.process("value", siblings=[], tags={}, parent=None)
        assert result == "value"

    def test_process_with_none_value(self) -> None:
        """Test process with None value."""
        node = ConcreteChildNode(name="test")
        result = node.process(None, siblings=[], tags={}, parent=None)
        assert result is None

    def test_process_with_complex_value(self) -> None:
        """Test process with complex data types."""
        node = ConcreteChildNode(name="test")

        result = node.process([1, 2, 3], siblings=[], tags={}, parent=None)
        assert result == [1, 2, 3]

        result = node.process(
            {"key": "value"}, siblings=[], tags={}, parent=None
        )
        assert result == {"key": "value"}

        result = node.process((1, 2, 3), siblings=[], tags={}, parent=None)
        assert result == (1, 2, 3)

    def test_process_args_immutability(self) -> None:
        """Test that process_args tuple is immutable."""
        node = ConcreteChildNode(name="test", process_args=(1, 2, 3))
        with pytest.raises((TypeError, AttributeError)):
            node.process_args[0] = 99  # type: ignore

    def test_multiple_decorator_applications(self) -> None:
        """Test applying decorator multiple times."""
        with patch("click_extended.core._child_node.queue_child"):
            decorator1 = ConcreteChildNode.as_decorator()
            decorator2 = UppercaseNode.as_decorator()

            def dummy_func() -> str:
                return "test"

            result = decorator1(decorator2(dummy_func))
            assert result() == "test"

    def test_name_with_special_characters(self) -> None:
        """Test node names with special characters."""
        node = ConcreteChildNode(name="test_node_123")
        assert node.name == "test_node_123"

        node2 = ConcreteChildNode(name="node-with-hyphens")
        assert node2.name == "node-with-hyphens"

    def test_empty_process_args_and_kwargs(self) -> None:
        """Test explicitly setting empty process args and kwargs."""
        node = ConcreteChildNode(
            name="test", process_args=(), process_kwargs={}
        )
        assert node.process_args == ()
        assert node.process_kwargs == {}
        assert len(node.process_args) == 0
        assert len(node.process_kwargs) == 0
