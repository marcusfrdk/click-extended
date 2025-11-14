"""Test the ParentNode class."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from click_extended.core._child_node import ChildNode
from click_extended.core._node import Node
from click_extended.core._parent_node import ParentNode


class ConcreteParentNode(ParentNode):
    """Concrete ParentNode implementation for testing."""

    def get_raw_value(self) -> Any:
        """Return a test value."""
        return "raw_value"


class EnvParentNode(ParentNode):
    """ParentNode that simulates environment variable."""

    def __init__(self, name: str, env_value: Any = None, **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)
        self.env_value = env_value

    def get_raw_value(self) -> Any:
        """Return the env value or default."""
        if self.env_value is None:
            if self.required:
                raise ValueError(f"Required value for '{self.name}' not set")
            return self.default
        return self.env_value


class DummyChildForParent(ChildNode):
    """Simple ChildNode for testing with ParentNode."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: Any,
        parent: Any,
        **kwargs: Any,
    ) -> Any:
        """Uppercase the value."""
        return str(value).upper()


class MultiplyChild(ChildNode):
    """Child that multiplies numeric values."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: Any,
        parent: Any,
        **kwargs: Any,
    ) -> Any:
        """Multiply by 2."""
        return value * 2


class TestParentNodeInitialization:
    """Test ParentNode initialization."""

    def test_init_with_name_only(self) -> None:
        """Test initialization with only name parameter."""
        node = ConcreteParentNode(name="test_parent")
        assert node.name == "test_parent"
        assert node.help is None
        assert node.required is False
        assert node.default is None
        assert node.children == {}

    def test_init_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        node = ConcreteParentNode(
            name="test_parent",
            help="Test help text",
            required=True,
            default="default_value",
        )
        assert node.name == "test_parent"
        assert node.help == "Test help text"
        assert node.required is True
        assert node.default == "default_value"
        assert node.children == {}

    def test_init_with_help(self) -> None:
        """Test initialization with help text."""
        node = ConcreteParentNode(name="test", help="Help text")
        assert node.help == "Help text"

    def test_init_with_required(self) -> None:
        """Test initialization with required parameter."""
        node = ConcreteParentNode(name="test", required=True)
        assert node.required is True

    def test_init_with_default(self) -> None:
        """Test initialization with default value."""
        node = ConcreteParentNode(name="test", default="default")
        assert node.default == "default"

    def test_children_initialized_as_empty_dict(self) -> None:
        """Test that children is initialized as empty dict."""
        node = ConcreteParentNode(name="test")
        assert isinstance(node.children, dict)
        assert len(node.children) == 0


class TestParentNodeAsDecorator:
    """Test ParentNode.as_decorator() classmethod."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_without_args(
        self, mock_queue_parent: MagicMock
    ) -> None:
        """Test as_decorator with minimal arguments."""
        decorator = ConcreteParentNode.as_decorator(name="test")

        def dummy_func() -> str:
            return "test"

        result = decorator(dummy_func)

        assert callable(result)
        assert result() == "test"
        mock_queue_parent.assert_called_once()
        call_args = mock_queue_parent.call_args
        assert call_args is not None
        node_instance = call_args[0][0]
        assert isinstance(node_instance, ConcreteParentNode)
        assert node_instance.name == "test"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_with_all_config(
        self, mock_queue_parent: MagicMock
    ) -> None:
        """Test as_decorator with all configuration parameters."""
        decorator = ConcreteParentNode.as_decorator(
            name="test",
            help="Help text",
            required=True,
            default="default",
        )

        def dummy_func() -> str:
            return "test"

        result = decorator(dummy_func)

        assert callable(result)
        assert result() == "test"
        mock_queue_parent.assert_called_once()
        call_args = mock_queue_parent.call_args
        assert call_args is not None
        node_instance = call_args[0][0]
        assert isinstance(node_instance, ConcreteParentNode)
        assert node_instance.name == "test"
        assert node_instance.help == "Help text"
        assert node_instance.required is True
        assert node_instance.default == "default"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_preserves_function_behavior(
        self, mock_queue_parent: MagicMock
    ) -> None:
        """Test that decorator preserves original function behavior."""
        decorator = ConcreteParentNode.as_decorator(name="test")

        def add_numbers(a: int, b: int) -> int:
            return a + b

        decorated = decorator(add_numbers)

        assert decorated(2, 3) == 5
        assert decorated(10, 20) == 30

    @patch("click_extended.core._parent_node.queue_parent")
    async def test_as_decorator_with_async_function(
        self, mock_queue_parent: MagicMock
    ) -> None:
        """Test as_decorator with async function."""
        decorator = ConcreteParentNode.as_decorator(name="test")

        async def async_func() -> str:
            return "async_result"

        decorated = decorator(async_func)

        result = await decorated()
        assert result == "async_result"

        assert mock_queue_parent.called

    @patch("click_extended.core._parent_node.queue_parent")
    async def test_as_decorator_preserves_async_function_behavior(
        self, mock_queue_parent: MagicMock
    ) -> None:
        """Test that decorator preserves async function behavior."""
        decorator = ConcreteParentNode.as_decorator(name="test")

        async def async_add(a: int, b: int) -> int:
            return a + b

        decorated = decorator(async_add)

        result = await decorated(5, 7)
        assert result == 12


class TestParentNodeGetRawValue:
    """Test ParentNode.get_raw_value() method."""

    def test_get_raw_value_not_implemented_on_base_class(self) -> None:
        """Test that get_raw_value raises NotImplementedError on abstract class."""
        node = ConcreteParentNode(name="test")
        assert node.get_raw_value() == "raw_value"

    def test_concrete_implementation_get_raw_value(self) -> None:
        """Test get_raw_value with concrete implementation."""
        node = ConcreteParentNode(name="test")
        assert node.get_raw_value() == "raw_value"

    def test_get_raw_value_with_env_simulation(self) -> None:
        """Test get_raw_value with simulated environment variable."""
        node = EnvParentNode(name="test", env_value="env_test_value")
        assert node.get_raw_value() == "env_test_value"

    def test_get_raw_value_with_default_when_none(self) -> None:
        """Test get_raw_value returns default when value is None."""
        node = EnvParentNode(
            name="test", env_value=None, default="default_value"
        )
        assert node.get_raw_value() == "default_value"

    def test_get_raw_value_required_raises_error(self) -> None:
        """Test get_raw_value raises error when required and no value."""
        node = EnvParentNode(name="test", env_value=None, required=True)
        with pytest.raises(ValueError) as exc_info:
            node.get_raw_value()
        assert "Required value for 'test' not set" in str(exc_info.value)


class TestParentNodeGetValue:
    """Test ParentNode.get_value() method."""

    def test_get_value_without_children(self) -> None:
        """Test get_value returns raw value when no children."""
        node = ConcreteParentNode(name="test")
        assert node.get_value() == "raw_value"

    def test_get_value_with_single_child(self) -> None:
        """Test get_value processes through single child."""
        node = ConcreteParentNode(name="test")
        child = DummyChildForParent(name="uppercase")
        assert node.children is not None
        node["uppercase"] = child

        result = node.get_value()
        assert result == "RAW_VALUE"

    def test_get_value_with_multiple_children(self) -> None:
        """Test get_value processes through multiple children."""
        node = EnvParentNode(name="test", env_value=5)
        child1 = MultiplyChild(name="multiply1")
        child2 = MultiplyChild(name="multiply2")
        assert node.children is not None
        node["multiply1"] = child1
        node["multiply2"] = child2

        result = node.get_value()
        # 5 * 2 * 2 = 20
        assert result == 20

    def test_get_value_chain_transformation(self) -> None:
        """Test get_value applies transformations in sequence."""
        node = EnvParentNode(name="test", env_value="hello")

        class AppendChild(ChildNode):
            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                return value + "_world"

        class UppercaseChild(ChildNode):
            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                return str(value).upper()

        child1 = AppendChild(name="append")
        child2 = UppercaseChild(name="uppercase")
        assert node.children is not None
        node["append"] = child1
        node["uppercase"] = child2

        result = node.get_value()
        assert result == "HELLO_WORLD"

    def test_get_value_passes_siblings_to_children(self) -> None:
        """Test that get_value passes siblings list to each child."""

        class SiblingsCheckChild(ChildNode):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.received_siblings: list[str] | None = None

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                self.received_siblings = siblings
                return value

        node = ConcreteParentNode(name="test")
        child1 = SiblingsCheckChild(name="child1")
        child2 = SiblingsCheckChild(name="child2")
        child3 = SiblingsCheckChild(name="child3")

        assert node.children is not None
        node["child1"] = child1
        node["child2"] = child2
        node["child3"] = child3

        node.get_value()

        assert child1.received_siblings is not None
        assert "SiblingsCheckChild" in child1.received_siblings
        assert len(child1.received_siblings) == 1

    def test_get_value_with_child_process_args(self) -> None:
        """Test get_value passes process_args to children."""

        class MultiplierChild(ChildNode):
            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                multiplier = args[0] if args else 1
                return value * multiplier

        node = EnvParentNode(name="test", env_value=10)
        child = MultiplierChild(name="multiply", process_args=(3,))
        assert node.children is not None
        node["multiply"] = child

        result = node.get_value()
        assert result == 30

    def test_get_value_with_child_process_kwargs(self) -> None:
        """Test get_value passes process_kwargs to children."""

        class PrefixChild(ChildNode):
            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                prefix = kwargs.get("prefix", "")
                return f"{prefix}{value}"

        node = ConcreteParentNode(name="test")
        child = PrefixChild(name="prefix", process_kwargs={"prefix": ">> "})
        assert node.children is not None
        node["prefix"] = child

        result = node.get_value()
        assert result == ">> raw_value"

    def test_get_value_with_validation_child_returns_none(self) -> None:
        """Test that validation children returning None don't break the chain."""

        class ValidationChild(ChildNode):
            """Validation child that returns None."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                if not value:
                    raise ValueError("Value cannot be empty")
                return None

        node = EnvParentNode(name="test", env_value="hello")
        child = ValidationChild(name="validate")
        assert node.children is not None
        node["validate"] = child

        result = node.get_value()
        assert result == "hello"

    def test_get_value_with_validation_between_transformations(self) -> None:
        """Test validation child between two transformation children preserves value."""

        class UppercaseChild(ChildNode):
            """Transform to uppercase."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                return str(value).upper()

        class ValidationChild(ChildNode):
            """Validation that returns None."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                if len(str(value)) < 3:
                    raise ValueError("Value too short")
                return None

        class ExclamationChild(ChildNode):
            """Add exclamation mark."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                return f"{value}!"

        node = EnvParentNode(name="test", env_value="hello")
        assert node.children is not None
        node["uppercase"] = UppercaseChild(name="uppercase")
        node["validate"] = ValidationChild(name="validate")
        node["exclaim"] = ExclamationChild(name="exclaim")

        result = node.get_value()
        assert result == "HELLO!"

    def test_get_value_with_multiple_validations_in_chain(self) -> None:
        """Test multiple validation children in a transformation chain."""

        class DoubleChild(ChildNode):
            """Double the number."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                return value * 2

        class PositiveValidation(ChildNode):
            """Validate value is positive."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                if value <= 0:
                    raise ValueError("Value must be positive")
                return None

        class RangeValidation(ChildNode):
            """Validate value is in range."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                if value > 100:
                    raise ValueError("Value too large")
                return None

        class AddTenChild(ChildNode):
            """Add 10 to value."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                return value + 10

        node = EnvParentNode(name="test", env_value=5)
        assert node.children is not None
        node["double"] = DoubleChild(name="double")
        node["positive"] = PositiveValidation(name="positive")
        node["range"] = RangeValidation(name="range")
        node["add_ten"] = AddTenChild(name="add_ten")

        result = node.get_value()
        assert result == 20

    def test_get_value_validation_child_raises_error(self) -> None:
        """Test that validation child errors propagate correctly."""

        class StrictValidation(ChildNode):
            """Validation that raises for invalid input."""

            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: Any,
                parent: Any,
                **kwargs: Any,
            ) -> Any:
                if value != "valid":
                    raise ValueError("Invalid value")
                return None

        node = EnvParentNode(name="test", env_value="invalid")
        assert node.children is not None
        node["validate"] = StrictValidation(name="validate")

        with pytest.raises(ValueError, match="Invalid value"):
            node.get_value()


class TestParentNodeInheritance:
    """Test ParentNode inheritance from Node."""

    def test_parentnode_is_node_subclass(self) -> None:
        """Test that ParentNode is a subclass of Node."""
        assert issubclass(ParentNode, Node)

    def test_parentnode_instance_is_node_instance(self) -> None:
        """Test that ParentNode instance is also a Node instance."""
        node = ConcreteParentNode(name="test")
        assert isinstance(node, Node)
        assert isinstance(node, ParentNode)

    def test_parentnode_has_name_attribute(self) -> None:
        """Test that ParentNode inherits name attribute from Node."""
        node = ConcreteParentNode(name="my_parent")
        assert hasattr(node, "name")
        assert node.name == "my_parent"

    def test_parentnode_has_children_dict(self) -> None:
        """Test that ParentNode has children as dict."""
        node = ConcreteParentNode(name="test")
        assert hasattr(node, "children")
        assert isinstance(node.children, dict)


class TestParentNodeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_get_value_with_none_value(self) -> None:
        """Test get_value when raw value is None."""
        node = EnvParentNode(name="test", env_value=None, default=None)
        result = node.get_value()
        assert result is None

    def test_get_value_with_empty_children_dict(self) -> None:
        """Test get_value with explicitly empty children dict."""
        node = ConcreteParentNode(name="test")
        node.children = {}
        assert node.get_value() == "raw_value"

    def test_multiple_parent_nodes_independent(self) -> None:
        """Test that multiple ParentNode instances are independent."""
        node1 = ConcreteParentNode(name="node1", help="Help 1")
        node2 = ConcreteParentNode(name="node2", help="Help 2")

        assert node1.name != node2.name
        assert node1.help != node2.help
        assert node1.children is not node2.children

    def test_required_and_default_together(self) -> None:
        """Test behavior when both required and default are set."""
        node = EnvParentNode(
            name="test", env_value=None, required=True, default="default_value"
        )
        with pytest.raises(ValueError, match="Required.*not set"):
            node.get_raw_value()

    def test_help_text_empty_string(self) -> None:
        """Test that empty string help text is preserved."""
        node = ConcreteParentNode(name="test", help="")
        assert node.help == ""

    def test_default_can_be_any_type(self) -> None:
        """Test that default can be various types."""
        node1 = ConcreteParentNode(name="test1", default="string")
        assert node1.default == "string"

        node2 = ConcreteParentNode(name="test2", default=42)
        assert node2.default == 42

        node3 = ConcreteParentNode(name="test3", default=[1, 2, 3])
        assert node3.default == [1, 2, 3]

        node4 = ConcreteParentNode(name="test4", default={"key": "value"})
        assert node4.default == {"key": "value"}

        node5 = ConcreteParentNode(name="test5", default=False)
        assert node5.default is False

    def test_name_with_special_characters(self) -> None:
        """Test parent node names with special characters."""
        node = ConcreteParentNode(name="test_node_123")
        assert node.name == "test_node_123"

        node2 = ConcreteParentNode(name="node-with-hyphens")
        assert node2.name == "node-with-hyphens"

    def test_children_can_be_added_dynamically(self) -> None:
        """Test that children can be added after initialization."""
        node = ConcreteParentNode(name="test")
        assert node.children is not None
        assert len(node.children) == 0

        child = DummyChildForParent(name="child1")
        assert node.children is not None
        node["child1"] = child
        assert node.children is not None
        assert len(node.children) == 1

        child2 = DummyChildForParent(name="child2")
        assert node.children is not None
        node["child2"] = child2
        assert node.children is not None
        assert len(node.children) == 2

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_with_custom_subclass_params(
        self, mock_queue_parent: MagicMock
    ) -> None:
        """Test as_decorator with subclass-specific parameters."""
        decorator = EnvParentNode.as_decorator(
            name="test",
            env_value="custom_env",
            help="Custom help",
        )

        def dummy_func() -> str:
            return "test"

        result = decorator(dummy_func)

        assert callable(result)
        assert result() == "test"
        mock_queue_parent.assert_called_once()
        call_args = mock_queue_parent.call_args
        assert call_args is not None
        node_instance = call_args[0][0]
        assert isinstance(node_instance, EnvParentNode)
        assert node_instance.name == "test"
        assert node_instance.env_value == "custom_env"
        assert node_instance.help == "Custom help"

    def test_get_value_preserves_type(self) -> None:
        """Test that get_value preserves value type through chain."""
        node = EnvParentNode(name="test", env_value=42)
        assert node.get_value() == 42
        assert isinstance(node.get_value(), int)

        node2 = EnvParentNode(name="test2", env_value=[1, 2, 3])
        assert node2.get_value() == [1, 2, 3]
        assert isinstance(node2.get_value(), list)

    def test_empty_name_allowed(self) -> None:
        """Test that empty string name is allowed."""
        node = ConcreteParentNode(name="")
        assert node.name == ""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_decorator_can_be_reused(
        self, mock_queue_parent: MagicMock
    ) -> None:
        """Test that the same decorator can be applied to multiple functions."""
        decorator = ConcreteParentNode.as_decorator(name="test")

        def func1() -> str:
            return "func1"

        def func2() -> str:
            return "func2"

        result1 = decorator(func1)
        result2 = decorator(func2)

        assert result1() == "func1"
        assert result2() == "func2"
        assert mock_queue_parent.call_count == 2
