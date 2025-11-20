"""Test the ChildNode class."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core._node import Node
from click_extended.core.argument import argument
from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.core.tag import Tag
from click_extended.errors import TypeMismatchError, ValidationError
from click_extended.validation.is_positive import is_positive


def make_context(
    parent: Any = None,
    siblings: list[str] | None = None,
    tags: dict[str, Tag] | None = None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> ProcessContext:
    """Helper to create a ProcessContext for testing."""
    return ProcessContext(
        parent=parent,  # type: ignore
        siblings=siblings or [],
        tags=tags or {},
        args=args or (),
        kwargs=kwargs or {},
    )


class ConcreteChildNode(ChildNode):
    """Concrete ChildNode implementation for testing."""

    def process(self, value: Any, context: ProcessContext) -> Any:
        """Simple process that returns the value unchanged."""
        return value


class UppercaseNode(ChildNode):
    """ChildNode that uppercases string values."""

    def process(self, value: Any, context: ProcessContext) -> Any:
        """Convert value to uppercase."""
        return str(value).upper()


class MultiplyNode(ChildNode):
    """ChildNode that multiplies numeric values."""

    def process(self, value: Any, context: ProcessContext) -> Any:
        """Multiply value by the first arg or 2 if no args."""
        multiplier = context.args[0] if context.args else 2
        return value * multiplier


class PrefixNode(ChildNode):
    """ChildNode that adds a prefix to values."""

    def process(self, value: Any, context: ProcessContext) -> Any:
        """Add prefix from kwargs or default."""
        prefix = context.kwargs.get("prefix", "PREFIX: ")
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
        context = ProcessContext(
            parent=None, siblings=[], tags={}, args=(), kwargs={}  # type: ignore
        )
        result = node.process("value", context)
        assert result == "value"

    def test_process_receives_all_parameters(self) -> None:
        """Test that process receives all expected parameters."""

        class InspectorNode(ChildNode):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.last_call: dict[str, Any] | None = None

            def process(self, value: Any, context: ProcessContext) -> Any:
                self.last_call = {
                    "value": value,
                    "parent": context.parent,
                    "siblings": context.siblings,
                    "tags": context.tags,
                    "args": context.args,
                    "kwargs": context.kwargs,
                }
                return value

        node = InspectorNode(name="inspector")

        dummy_tag = Tag(name="tag1")
        dummy_tag.parent_nodes = []

        context = ProcessContext(
            parent=None,  # type: ignore
            siblings=["SiblingOne", "SiblingTwo"],
            tags={"tag1": dummy_tag},
            args=("arg1", "arg2"),
            kwargs={"custom_param": "custom"},
        )

        result = node.process("test_value", context)

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
        assert node.process("hello", make_context()) == "HELLO"
        assert node.process("world", make_context()) == "WORLD"
        assert node.process("", make_context()) == ""

    def test_multiply_node_with_args(self) -> None:
        """Test MultiplyNode with process_args."""
        node = MultiplyNode(name="multiply", process_args=(3,))
        assert node.process(5, make_context(args=node.process_args)) == 15
        assert node.process(10, make_context(args=node.process_args)) == 30

    def test_multiply_node_without_args(self) -> None:
        """Test MultiplyNode without process_args (uses default)."""
        node = MultiplyNode(name="multiply")
        assert node.process(5, make_context()) == 10
        assert node.process(7, make_context()) == 14

    def test_prefix_node_with_kwargs(self) -> None:
        """Test PrefixNode with process_kwargs."""
        node = PrefixNode(name="prefix", process_kwargs={"prefix": ">>> "})
        result = node.process(
            "message", make_context(kwargs=node.process_kwargs)
        )
        assert result == ">>> message"

    def test_prefix_node_without_kwargs(self) -> None:
        """Test PrefixNode without process_kwargs (uses default)."""
        node = PrefixNode(name="prefix")
        result = node.process("message", make_context())
        assert result == "PREFIX: message"

    def test_siblings_parameter(self) -> None:
        """Test that siblings parameter is properly passed."""

        class SiblingsInspectorNode(ChildNode):
            def process(
                self,
                value: Any,
                context: ProcessContext,
            ) -> Any:
                return f"Value: {value}, Siblings: {len(context.siblings)}"

        node = SiblingsInspectorNode(name="inspector")
        result = node.process(
            "test",
            make_context(siblings=["NodeOne", "NodeTwo", "NodeThree"]),
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
        result = node.process("value", make_context())
        assert result == "value"

    def test_process_with_none_value(self) -> None:
        """Test process with None value."""
        node = ConcreteChildNode(name="test")
        result = node.process(None, make_context())
        assert result is None

    def test_process_with_complex_value(self) -> None:
        """Test process with complex data types."""
        node = ConcreteChildNode(name="test")

        result = node.process([1, 2, 3], make_context())
        assert result == [1, 2, 3]

        result = node.process({"key": "value"}, make_context())
        assert result == {"key": "value"}

        result = node.process((1, 2, 3), make_context())
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


class TestChildNodeTypeValidation:
    """Test ChildNode type validation system."""

    def test_default_get_supported_types_is_empty(self) -> None:
        """Test that default get_supported_types returns empty (accepts all types)."""
        node = ConcreteChildNode(name="test")
        assert node.get_supported_types() == []

    def test_types_inferred_from_type_hints(self) -> None:
        """Test that types are inferred from process() type hints."""

        class IntOnlyNode(ChildNode):
            """Node that only accepts int types."""

            def process(self, value: int, context: ProcessContext) -> Any:
                return value * 2

        node = IntOnlyNode(name="test")
        assert node.get_supported_types() == [int]
        assert int in node.get_supported_types()

    def test_validate_type_with_no_type_hint(self) -> None:
        """Test that validation passes when no type hint specified."""

        node = ConcreteChildNode(name="test")
        parent = MagicMock()
        parent.name = "test_parent"
        parent.type = str

        node.validate_type(parent)  # Should not raise

    def test_validate_type_with_matching_type(self) -> None:
        """Test that validation passes when parent type matches."""

        class IntOnlyNode(ChildNode):
            """Node that only accepts int types."""

            def process(self, value: int, context: ProcessContext) -> Any:
                return value

        node = IntOnlyNode(name="test")
        parent = MagicMock()
        parent.name = "count"
        parent.type = int

        # Should not raise
        node.validate_type(parent)

    def test_validate_type_with_mismatched_type(self) -> None:
        """Test that validation fails when parent type doesn't match."""

        class IntOnlyNode(ChildNode):
            """Node that only accepts int types."""

            def process(self, value: int, context: ProcessContext) -> Any:
                return value

        node = IntOnlyNode(name="test")
        parent = MagicMock()
        parent.name = "name"
        parent.type = str

        with pytest.raises(TypeMismatchError) as exc_info:
            node.validate_type(parent)

        error_msg = str(exc_info.value)
        assert "test" in error_msg
        assert "name" in error_msg
        assert "str" in error_msg
        assert "int" in error_msg

    def test_validate_type_with_none_parent_type(self) -> None:
        """Test that validation passes when parent type is None."""

        class IntOnlyNode(ChildNode):
            """Node that only accepts int types."""

            def process(self, value: int, context: ProcessContext) -> Any:
                return value

        node = IntOnlyNode(name="test")
        parent = MagicMock()
        parent.name = "value"
        parent.type = None

        node.validate_type(parent)

    def test_validate_type_with_multiple_supported_types(self) -> None:
        """Test validation with multiple supported types using union syntax."""

        class NumericNode(ChildNode):
            """Node that accepts int and float types."""

            def process(
                self, value: int | float, context: ProcessContext
            ) -> Any:
                return value

        node = NumericNode(name="test")
        parent_int = MagicMock()
        parent_int.name = "count"
        parent_int.type = int

        parent_float = MagicMock()
        parent_float.name = "ratio"
        parent_float.type = float

        # Both should pass
        node.validate_type(parent_int)
        node.validate_type(parent_float)

    def test_validate_type_error_message_format(self) -> None:
        """Test that TypeMismatchError has proper formatting."""

        class IntFloatNode(ChildNode):
            """Node that accepts int and float."""

            def process(
                self, value: int | float, context: ProcessContext
            ) -> Any:
                return value

        node = IntFloatNode(name="test")
        parent = MagicMock()
        parent.name = "username"
        parent.type = str

        with pytest.raises(TypeMismatchError) as exc_info:
            node.validate_type(parent)

        error_msg = str(exc_info.value)
        assert "test" in error_msg
        assert "username" in error_msg
        assert "str" in error_msg
        assert "int" in error_msg

    def test_validate_type_with_parent_without_type_attribute(self) -> None:
        """Test validation when parent has no type attribute."""

        class IntOnlyNode(ChildNode):
            """Node that only accepts int types."""

            def process(self, value: int, context: ProcessContext) -> Any:
                return value

        node = IntOnlyNode(name="test")
        parent = MagicMock(spec=[])
        parent.name = "value"

        node.validate_type(parent)


class TestTypeValidationIntegration:
    """Integration tests for type validation across the CLI."""

    def test_type_validation_with_option_and_argument(self) -> None:
        """Test type validation works with both options and arguments."""

        @command()
        @option("--count", type=int, default=5)
        @is_positive()
        @argument("amount", type=float)
        @is_positive()
        def test_cmd(count: int, amount: float) -> None:
            """Test command with multiple validated parameters."""
            print(f"Count: {count}, Amount: {amount}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["10.5", "--count", "3"])  # type: ignore

        assert result.exit_code == 0
        assert "Count: 3, Amount: 10.5" in result.output

    def test_type_validation_rejects_invalid_option_type(self) -> None:
        """Test that invalid option type is rejected early."""

        @command()
        @option("--name", type=str, default="test")
        @is_positive()  # Should fail as str is not supported
        def test_cmd(name: str) -> None:
            """Test command."""
            print(f"Name: {name}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--name", "hello"])  # type: ignore

        assert result.exit_code != 0
        assert result.exception is not None
        assert isinstance(result.exception, TypeMismatchError)

    def test_type_validation_rejects_invalid_argument_type(self) -> None:
        """Test that invalid argument type is rejected early."""

        @command()
        @argument("username", type=str)
        @is_positive()  # Should fail as str is not supported
        def test_cmd(username: str) -> None:
            """Test command."""
            print(f"Username: {username}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["john"])  # type: ignore

        assert result.exit_code != 0
        assert result.exception is not None
        assert isinstance(result.exception, TypeMismatchError)
        assert "str" in str(result.exception)

    def test_type_validation_with_multiple_validators_same_parent(
        self,
    ) -> None:
        """Test multiple validators on the same parent."""

        class IsEven(ChildNode):
            """Validator that checks if value is even."""

            def process(self, value: int, context: ProcessContext) -> None:
                if value % 2 != 0:
                    raise ValueError(f"Value must be even, got {value}")

        @command()
        @option("--count", type=int, default=2)
        @is_positive()
        @IsEven.as_decorator()
        def test_cmd(count: int) -> None:
            """Test command."""
            print(f"Count: {count}")

        runner = CliRunner()

        result = runner.invoke(test_cmd, ["--count", "4"])  # type: ignore
        assert result.exit_code == 0
        assert "Count: 4" in result.output

        result = runner.invoke(test_cmd, ["--count", "3"])  # type: ignore
        assert result.exit_code != 0
        assert "must be even" in str(result.exception).lower()

    def test_type_validation_with_inferred_type_from_default(self) -> None:
        """Test that type validation works when type is inferred from default."""

        @command()
        @option("--value", default=5)  # Type inferred as int from default
        @is_positive()  # Supports int, float
        def test_cmd(value: int) -> None:
            """Test command."""
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--value", "10"])  # type: ignore

        assert result.exit_code == 0
        assert "Value: 10" in result.output

    def test_type_validation_with_no_type_no_default(self) -> None:
        """Test that type defaults to str when neither type nor default specified."""

        @command()
        @option("--name")
        @is_positive()
        def test_cmd(name: str) -> None:
            """Test command."""
            print(f"Name: {name}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--name", "hello"])  # type: ignore

        assert result.exit_code != 0
        assert result.exception is not None
        assert isinstance(result.exception, TypeMismatchError)
        assert "str" in str(result.exception)

    def test_type_validation_with_mixed_type_requirements(self) -> None:
        """Test validators with different type requirements."""

        class StringLength(ChildNode):
            """Validator for string length."""

            def process(self, value: str, context: ProcessContext) -> None:
                if len(value) < 3:
                    raise ValidationError(
                        f"String must be at least 3 characters, got {len(value)}"
                    )

        @command()
        @option("--count", type=int, default=5)
        @is_positive()  # Accepts int, float
        @option("--name", type=str, default="test")
        @StringLength.as_decorator()  # Accepts str
        def test_cmd(count: int, name: str) -> None:
            """Test command with different validators."""
            print(f"Count: {count}, Name: {name}")

        runner = CliRunner()

        # Valid values
        result = runner.invoke(
            test_cmd, ["--count", "10", "--name", "alice"]  # type: ignore
        )
        assert result.exit_code == 0
        assert "Count: 10, Name: alice" in result.output

        # Invalid count
        result = runner.invoke(
            test_cmd, ["--count", "-5", "--name", "alice"]  # type: ignore
        )
        assert result.exit_code != 0
        assert "-5 is not positive" in result.output

        # Invalid name
        result = runner.invoke(
            test_cmd, ["--count", "10", "--name", "ab"]  # type: ignore
        )
        assert result.exit_code != 0
        assert "at least 3 characters" in result.output

    def test_type_validation_error_provides_clear_message(self) -> None:
        """Test that type validation errors provide helpful messages."""

        @command()
        @option("--port", type=int, default=8080)
        @argument("host", type=str)
        @is_positive()  # Will fail on str argument
        def test_cmd(port: int, host: str) -> None:
            """Test command."""
            print(f"Port: {port}, Host: {host}")

        runner = CliRunner()
        result = runner.invoke(
            test_cmd, ["localhost", "--port", "3000"]  # type: ignore
        )

        assert result.exit_code != 0
        assert result.exception is not None

        error_msg = str(result.exception)
        assert "Decorator" in error_msg
        assert "is_positive" in error_msg
        assert "host" in error_msg
        assert "str" in error_msg
        assert "int" in error_msg or "float" in error_msg

    def test_type_validation_with_default_values(self) -> None:
        """Test that type validation works with default values."""

        @command()
        @option("--count", type=int, default=10)
        @is_positive()
        def test_cmd(count: int) -> None:
            """Test command."""
            print(f"Count: {count}")

        runner = CliRunner()

        # Using default value
        result = runner.invoke(test_cmd, [])  # type: ignore
        assert result.exit_code == 0
        assert "Count: 10" in result.output

        # Overriding with valid value
        result = runner.invoke(test_cmd, ["--count", "5"])  # type: ignore
        assert result.exit_code == 0
        assert "Count: 5" in result.output

        # Overriding with invalid value
        result = runner.invoke(test_cmd, ["--count", "-1"])  # type: ignore
        assert result.exit_code != 0
        assert "-1 is not positive" in result.output

    def test_type_validation_fails_before_processing(self) -> None:
        """Test that type validation happens before value processing."""

        process_called: list[bool] = []

        class TrackingNode(ChildNode):
            """Node that tracks if process was called."""

            def process(self, value: int, context: ProcessContext) -> Any:
                process_called.append(True)
                return value * 2

        @command()
        @option("--name", type=str, default="test")
        @TrackingNode.as_decorator()  # Should fail before processing
        def test_cmd(name: str) -> None:
            """Test command."""
            print(f"Name: {name}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--name", "hello"])  # type: ignore

        # Should fail with TypeMismatchError
        assert result.exit_code != 0
        assert isinstance(result.exception, TypeMismatchError)

        # Process should not have been called
        assert len(process_called) == 0


class TestTypeValidationPerformance:
    """Test that type validation doesn't significantly impact performance."""

    def test_validation_with_many_parameters(self) -> None:
        """Test validation works efficiently with many parameters."""

        @command()
        @option("--a", type=int, default=1)
        @is_positive()
        @option("--b", type=int, default=2)
        @is_positive()
        @option("--c", type=int, default=3)
        @is_positive()
        @option("--d", type=int, default=4)
        @is_positive()
        @option("--e", type=int, default=5)
        @is_positive()
        def test_cmd(a: int, b: int, c: int, d: int, e: int) -> None:
            """Test command with many parameters."""
            print(f"Sum: {a + b + c + d + e}")

        runner = CliRunner()
        result = runner.invoke(
            test_cmd,  # type: ignore
            ["--a", "1", "--b", "2", "--c", "3", "--d", "4", "--e", "5"],
        )

        assert result.exit_code == 0
        assert "Sum: 15" in result.output
