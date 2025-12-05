"""Comprehensive tests for ParentNode functionality."""

from typing import Any

import pytest

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context


class ConcreteParentNode(ParentNode):
    """Concrete implementation of ParentNode for testing."""

    def load(self, context: Context, *args: Any, **kwargs: Any) -> Any:
        """Simple load implementation that returns the default value."""
        return self.default


class CustomLoadParentNode(ParentNode):
    """ParentNode with custom load behavior for testing."""

    def __init__(self, load_fn: Any = None, **kwargs: Any):
        """Initialize with optional custom load function."""
        super().__init__(**kwargs)
        self._load_fn = load_fn

    def load(self, context: Context, *args: Any, **kwargs: Any) -> Any:
        """Use custom load function if provided, otherwise return default."""
        if self._load_fn:
            return self._load_fn(context, *args, **kwargs)
        return self.default


class TestParentNodeInit:
    """Test ParentNode initialization with various configurations."""

    def test_init_with_only_name(self) -> None:
        """Test initialization with only required name parameter."""
        node = ConcreteParentNode(name="test_node")

        assert node.name == "test_node"
        assert node.param == "test_node"  # defaults to name
        assert node.help is None
        assert node.required is False
        assert node.default is None
        assert node.tags == []
        assert node.was_provided is False
        assert node.cached_value is None
        assert node._value_computed is False
        assert node.decorator_kwargs == {}
        assert node.children == {}

    def test_init_with_explicit_param(self) -> None:
        """Test that param parameter is used when provided."""
        node = ConcreteParentNode(name="test_node", param="custom_param")

        assert node.name == "test_node"
        assert node.param == "custom_param"

    def test_init_param_defaults_to_name(self) -> None:
        """Test that param defaults to name when not provided."""
        node = ConcreteParentNode(name="my_option")

        assert node.param == "my_option"

    def test_init_with_help_text(self) -> None:
        """Test initialization with help text."""
        help_text = "This is help text"
        node = ConcreteParentNode(name="test_node", help=help_text)

        assert node.help == help_text

    def test_init_with_required_true(self) -> None:
        """Test initialization with required=True."""
        node = ConcreteParentNode(name="test_node", required=True)

        assert node.required is True

    def test_init_with_required_false(self) -> None:
        """Test initialization with required=False (default)."""
        node = ConcreteParentNode(name="test_node", required=False)

        assert node.required is False

    def test_init_with_string_default(self) -> None:
        """Test initialization with string default value."""
        node = ConcreteParentNode(name="test_node", default="default_value")

        assert node.default == "default_value"

    def test_init_with_int_default(self) -> None:
        """Test initialization with integer default value."""
        node = ConcreteParentNode(name="test_node", default=42)

        assert node.default == 42

    def test_init_with_list_default(self) -> None:
        """Test initialization with list default value."""
        default_list = ["a", "b", "c"]
        node = ConcreteParentNode(name="test_node", default=default_list)

        assert node.default == default_list

    def test_init_with_dict_default(self) -> None:
        """Test initialization with dict default value."""
        default_dict = {"key": "value", "num": 123}
        node = ConcreteParentNode(name="test_node", default=default_dict)

        assert node.default == default_dict

    def test_init_with_none_default(self) -> None:
        """Test initialization with None default value (explicit)."""
        node = ConcreteParentNode(name="test_node", default=None)

        assert node.default is None

    def test_init_tags_none_creates_empty_list(self) -> None:
        """Test that tags=None creates an empty list."""
        node = ConcreteParentNode(name="test_node", tags=None)

        assert node.tags == []
        assert isinstance(node.tags, list)

    def test_init_tags_single_string_converts_to_list(self) -> None:
        """Test that a single tag string is converted to a list."""
        node = ConcreteParentNode(name="test_node", tags="validation")

        assert node.tags == ["validation"]
        assert isinstance(node.tags, list)

    def test_init_tags_list_of_strings(self) -> None:
        """Test initialization with list of tag strings."""
        tags = ["validation", "transform", "custom"]
        node = ConcreteParentNode(name="test_node", tags=tags)

        assert node.tags == tags
        assert isinstance(node.tags, list)

    def test_init_tags_list_is_copied(self) -> None:
        """Test that tags list is copied, not referenced."""
        original_tags = ["tag1", "tag2"]
        node = ConcreteParentNode(name="test_node", tags=original_tags)

        # Modify original
        original_tags.append("tag3")

        # Node's tags should be unaffected
        assert node.tags == ["tag1", "tag2"]

    def test_init_allows_name_matching_tag_during_init(self) -> None:
        """Test that node name matching a tag is allowed during init.

        Note: The actual validation happens later during Tree._validate_names().
        """
        # Should not raise during initialization
        node = ConcreteParentNode(name="symbol", tags="symbol")

        assert node.name == "symbol"
        assert node.tags == ["symbol"]

    def test_init_with_extra_kwargs(self) -> None:
        """Test that extra kwargs are accepted (for subclasses)."""
        # Should not raise an error
        node = ConcreteParentNode(
            name="test_node", extra_param="value", another="test"
        )

        assert node.name == "test_node"

    def test_init_children_is_empty_dict(self) -> None:
        """Test that children is initialized as empty dict."""
        node = ConcreteParentNode(name="test_node")

        assert node.children == {}
        assert isinstance(node.children, dict)

    def test_init_all_parameters(self) -> None:
        """Test initialization with all parameters specified."""
        node = ConcreteParentNode(
            name="test_node",
            param="custom_param",
            help="Help text",
            required=True,
            default="default_val",
            tags=["tag1", "tag2"],
        )

        assert node.name == "test_node"
        assert node.param == "custom_param"
        assert node.help == "Help text"
        assert node.required is True
        assert node.default == "default_val"
        assert node.tags == ["tag1", "tag2"]


class TestParentNodeMethods:
    """Test ParentNode public methods."""

    def test_get_value_returns_cached_value(self) -> None:
        """Test that get_value() returns the cached_value."""
        node = ConcreteParentNode(name="test_node")
        node.cached_value = "test_value"

        assert node.get_value() == "test_value"

    def test_get_value_with_none(self) -> None:
        """Test get_value() with None cached value."""
        node = ConcreteParentNode(name="test_node")
        node.cached_value = None

        assert node.get_value() is None

    def test_get_value_with_string(self) -> None:
        """Test get_value() with string cached value."""
        node = ConcreteParentNode(name="test_node")
        node.cached_value = "hello"

        assert node.get_value() == "hello"

    def test_get_value_with_int(self) -> None:
        """Test get_value() with integer cached value."""
        node = ConcreteParentNode(name="test_node")
        node.cached_value = 42

        assert node.get_value() == 42

    def test_get_value_with_list(self) -> None:
        """Test get_value() with list cached value."""
        node = ConcreteParentNode(name="test_node")
        test_list = [1, 2, 3]
        node.cached_value = test_list

        assert node.get_value() == test_list

    def test_get_value_with_dict(self) -> None:
        """Test get_value() with dict cached value."""
        node = ConcreteParentNode(name="test_node")
        test_dict = {"key": "value"}
        node.cached_value = test_dict

        assert node.get_value() == test_dict

    def test_get_value_with_custom_object(self) -> None:
        """Test get_value() with custom object cached value."""
        node = ConcreteParentNode(name="test_node")

        class CustomObject:
            def __init__(self, value: str):
                self.value = value

        obj = CustomObject("test")
        node.cached_value = obj

        assert node.get_value() is obj
        assert node.get_value().value == "test"

    def test_repr_format(self) -> None:
        """Test __repr__ returns correct format."""
        node = ConcreteParentNode(name="my_node")

        repr_str = repr(node)

        assert "ConcreteParentNode" in repr_str
        assert "my_node" in repr_str
        assert repr_str == "<ConcreteParentNode name='my_node'>"

    def test_repr_with_different_names(self) -> None:
        """Test __repr__ with various node names."""
        node1 = ConcreteParentNode(name="option1")
        node2 = ConcreteParentNode(name="test_param")

        assert repr(node1) == "<ConcreteParentNode name='option1'>"
        assert repr(node2) == "<ConcreteParentNode name='test_param'>"

    def test_load_is_abstract(self) -> None:
        """Test that ParentNode.load() is abstract."""
        # Cannot instantiate ParentNode directly
        with pytest.raises(TypeError, match="abstract"):
            ParentNode(name="test")  # type: ignore

    def test_concrete_load_implementation(self) -> None:
        """Test that concrete implementation can override load()."""
        node = ConcreteParentNode(name="test_node", default="loaded_value")

        # Create a minimal context
        from click_extended.core.decorators.command import command

        @command()
        def dummy_cmd() -> None:
            pass

        from click.testing import CliRunner

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(dummy_cmd, [])
            assert hasattr(node, "load")
            assert callable(node.load)


class TestParentNodeDecorator:
    """Test ParentNode.as_decorator() functionality."""

    def test_decorator_can_be_applied_to_sync_function(self) -> None:
        """Test that decorator can be applied to synchronous functions."""

        @ConcreteParentNode.as_decorator(name="test_param")
        def test_func() -> str:
            return "result"

        assert callable(test_func)
        assert test_func() == "result"

    def test_decorator_can_be_applied_to_async_function(self) -> None:
        """Test that decorator can be applied to asynchronous functions."""
        import asyncio

        @ConcreteParentNode.as_decorator(name="test_param")
        async def test_func() -> str:
            return "async_result"

        assert callable(test_func)
        result = asyncio.run(test_func())
        assert result == "async_result"

    def test_decorator_preserves_function_name(self) -> None:
        """Test that decorated function preserves original name."""

        @ConcreteParentNode.as_decorator(name="test_param")
        def my_function() -> None:
            pass

        assert my_function.__name__ == "my_function"

    def test_decorator_preserves_function_docstring(self) -> None:
        """Test that decorated function preserves docstring."""

        @ConcreteParentNode.as_decorator(name="test_param")
        def my_function() -> None:
            """This is the docstring."""
            pass

        assert my_function.__doc__ == "This is the docstring."

    def test_decorator_returns_callable_with_same_signature(self) -> None:
        """Test decorated function has same signature."""

        @ConcreteParentNode.as_decorator(name="test_param")
        def test_func(arg1: str, arg2: int) -> str:
            return f"{arg1}-{arg2}"

        # Function should still accept the same arguments
        result = test_func("hello", 42)
        assert result == "hello-42"

    def test_decorator_kwargs_stores_all_config(self) -> None:
        """Test that decorator_kwargs stores all configuration."""
        from click_extended.core.other._tree import Tree

        # Clear any pending nodes
        Tree._pending_nodes.clear()

        @ConcreteParentNode.as_decorator(
            name="test_param",
            param="custom_param",
            help="Help text",
            required=True,
            default="default_val",
            tags=["tag1", "tag2"],
        )
        def test_func() -> None:
            pass

        # Get the queued parent node
        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        node_type, node = pending[0]

        assert node_type == "parent"
        assert isinstance(node, ParentNode)
        assert node.decorator_kwargs["name"] == "test_param"
        assert node.decorator_kwargs["param"] == "custom_param"
        assert node.decorator_kwargs["help"] == "Help text"
        assert node.decorator_kwargs["required"] is True
        assert node.decorator_kwargs["default"] == "default_val"
        assert node.decorator_kwargs["tags"] == ["tag1", "tag2"]

    def test_decorator_kwargs_includes_extra_kwargs(self) -> None:
        """Test that extra kwargs are included in decorator_kwargs."""
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @CustomLoadParentNode.as_decorator(
            name="test_param", custom_arg="value", another_arg=123
        )
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]

        assert isinstance(node, ParentNode)
        assert node.decorator_kwargs["custom_arg"] == "value"
        assert node.decorator_kwargs["another_arg"] == 123

    def test_decorator_creates_instance(self) -> None:
        """Test that decorator creates a node instance."""
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @ConcreteParentNode.as_decorator(name="test_param")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        node_type, node = pending[0]

        assert node_type == "parent"
        assert isinstance(node, ConcreteParentNode)
        assert node.name == "test_param"

    def test_decorator_queues_parent_in_tree(self) -> None:
        """Test that Tree.queue_parent() is called."""
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @ConcreteParentNode.as_decorator(name="test_param")
        def test_func() -> None:
            pass

        # Check that node was queued
        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        assert pending[0][0] == "parent"

    def test_multiple_decorators_queue_in_order(self) -> None:
        """Test that multiple decorators are queued correctly."""
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @ConcreteParentNode.as_decorator(name="param1")
        def test_func() -> None:
            pass

        @ConcreteParentNode.as_decorator(name="param2")
        def test_func2() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 2
        assert pending[0][1].name == "param1"
        assert pending[1][1].name == "param2"

    def test_sync_function_remains_sync(self) -> None:
        """Test that synchronous functions remain synchronous."""
        import asyncio

        @ConcreteParentNode.as_decorator(name="test_param")
        def test_func() -> str:
            return "sync"

        # Function should not be a coroutine
        result = test_func()
        assert not asyncio.iscoroutine(result)
        assert result == "sync"

    def test_async_function_wrapped_correctly(self) -> None:
        """Test that async functions are wrapped correctly."""
        import asyncio

        @ConcreteParentNode.as_decorator(name="test_param")
        async def test_func() -> str:
            await asyncio.sleep(0.01)
            return "async"

        # Function should return a coroutine
        result_coro = test_func()
        assert asyncio.iscoroutine(result_coro)
        result = asyncio.run(result_coro)
        assert result == "async"

    def test_decorated_function_arguments_pass_through(self) -> None:
        """Test that function arguments are passed through correctly."""

        @ConcreteParentNode.as_decorator(name="test_param")
        def test_func(a: int, b: int, c: str = "default") -> str:
            return f"{a + b}-{c}"

        result = test_func(1, 2)
        assert result == "3-default"

        result = test_func(5, 10, c="custom")
        assert result == "15-custom"

    def test_decorator_with_all_parameters(self) -> None:
        """Test decorator with all possible parameters."""
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @ConcreteParentNode.as_decorator(
            name="full_param",
            param="injection_name",
            help="Detailed help text",
            required=True,
            default="default_value",
            tags=["tag1", "tag2", "tag3"],
        )
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]

        assert isinstance(node, ParentNode)
        assert node.name == "full_param"
        assert node.param == "injection_name"
        assert node.help == "Detailed help text"
        assert node.required is True
        assert node.default == "default_value"
        assert node.tags == ["tag1", "tag2", "tag3"]


class TestParentNodeSubclassIntegration:
    """Test ParentNode integration with OptionNode, ArgumentNode, and Env."""

    def test_option_node_extends_parent_node(self) -> None:
        """Test that OptionNode properly extends ParentNode."""
        from click_extended.core.nodes.option_node import OptionNode

        assert issubclass(OptionNode, ParentNode)

    def test_option_node_inherits_parent_attributes(self) -> None:
        """Test that OptionNode inherits all ParentNode attributes."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option(name="test_opt", param="custom_param", default="value")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]

        # Check ParentNode inherited attributes
        assert hasattr(node, "name")
        assert hasattr(node, "param")
        assert hasattr(node, "default")
        assert hasattr(node, "required")
        assert hasattr(node, "tags")
        assert hasattr(node, "was_provided")
        assert hasattr(node, "cached_value")
        assert hasattr(node, "decorator_kwargs")

    def test_argument_node_extends_parent_node(self) -> None:
        """Test that ArgumentNode properly extends ParentNode."""
        from click_extended.core.nodes.argument_node import ArgumentNode

        assert issubclass(ArgumentNode, ParentNode)

    def test_argument_node_inherits_parent_attributes(self) -> None:
        """Test that ArgumentNode inherits all ParentNode attributes."""
        from click_extended.core.decorators.argument import argument
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @argument(name="test_arg", default="value")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]

        # Check ParentNode inherited attributes
        assert hasattr(node, "name")
        assert hasattr(node, "param")
        assert hasattr(node, "default")
        assert hasattr(node, "required")
        assert hasattr(node, "tags")

    def test_env_node_extends_parent_node(self) -> None:
        """Test that Env properly extends ParentNode."""
        from click_extended.core.decorators.env import Env

        assert issubclass(Env, ParentNode)

    def test_env_node_inherits_parent_attributes(self) -> None:
        """Test that Env inherits all ParentNode attributes."""
        from click_extended.core.decorators.env import Env

        env_node = Env(name="TEST_VAR", env_name="TEST_ENV")

        # Check ParentNode inherited attributes
        assert hasattr(env_node, "name")
        assert hasattr(env_node, "param")
        assert hasattr(env_node, "default")
        assert hasattr(env_node, "required")
        assert hasattr(env_node, "tags")
        assert env_node.name == "TEST_VAR"


class TestParentNodeCommandIntegration:
    """Test ParentNode integration with Click commands."""

    def test_option_parent_with_simple_command(self, cli_runner: Any) -> None:
        """Test option parent node in a simple command."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("--name", default="World")
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_argument_parent_with_simple_command(self, cli_runner: Any) -> None:
        """Test argument parent node in a simple command."""
        import click

        from click_extended.core.decorators.argument import argument
        from click_extended.core.decorators.command import command

        @command()
        @argument("name", default="World")
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_env_parent_with_simple_command(self, cli_runner: Any) -> None:
        """Test env parent node in a simple command."""
        import os

        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.env import env

        @command()
        @env("TEST_VAR", default="default_value")
        def show_env(test_var: str) -> None:
            click.echo(f"Value: {test_var}")

        # Without env var
        result = cli_runner.invoke(show_env, [])
        assert result.exit_code == 0
        assert "Value: default_value" in result.output

        # With env var
        os.environ["TEST_VAR"] = "from_env"
        result = cli_runner.invoke(show_env, [])
        assert result.exit_code == 0
        assert "Value: from_env" in result.output
        del os.environ["TEST_VAR"]

    def test_multiple_options_on_same_command(self, cli_runner: Any) -> None:
        """Test multiple option parent nodes on same command."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("--first", default="A")
        @option("--second", default="B")
        def combine(first: str, second: str) -> None:
            click.echo(f"{first}-{second}")

        result = cli_runner.invoke(combine, ["--first", "X", "--second", "Y"])
        assert result.exit_code == 0
        assert "X-Y" in result.output

    def test_mix_of_options_and_arguments(self, cli_runner: Any) -> None:
        """Test mix of option and argument parent nodes."""
        import click

        from click_extended.core.decorators.argument import argument
        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @argument("name")
        @option("--greeting", default="Hello")
        def greet(name: str, greeting: str) -> None:
            click.echo(f"{greeting}, {name}!")

        result = cli_runner.invoke(greet, ["Alice", "--greeting", "Hi"])
        assert result.exit_code == 0
        assert "Hi, Alice!" in result.output

    def test_param_injection_name(self, cli_runner: Any) -> None:
        """Test that param determines injection name."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("my_option", param="injected_name", default="test")
        def show(injected_name: str) -> None:
            click.echo(f"Value: {injected_name}")

        # CLI uses kebab-case: my_option -> --my-option
        result = cli_runner.invoke(show, ["--my-option", "custom"])
        assert result.exit_code == 0
        assert "Value: custom" in result.output

    def test_was_provided_flag_with_option(self, cli_runner: Any) -> None:
        """Test that was_provided flag is set correctly."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @command()
        @option("--value", default="default")
        def check_provided(value: str) -> None:
            # Access the tree to check was_provided
            context = click.get_current_context()
            meta = context.meta.get("click_extended", {})
            click.echo(f"Value: {value}")

        # Test with provided value
        result = cli_runner.invoke(check_provided, ["--value", "custom"])
        assert result.exit_code == 0
        assert "Value: custom" in result.output

        # Test with default value
        result = cli_runner.invoke(check_provided, [])
        assert result.exit_code == 0
        assert "Value: default" in result.output

    def test_cached_value_is_set(self, cli_runner: Any) -> None:
        """Test that cached_value is set after processing."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        captured_value = None

        class ValueCapture:
            value: int | None = None

        @command()
        @option("--num", type=int, default=42)
        def process_value(num: int) -> None:
            ValueCapture.value = num
            click.echo(f"Number: {num}")

        result = cli_runner.invoke(process_value, ["--num", "100"])
        assert result.exit_code == 0
        assert "Number: 100" in result.output
        assert ValueCapture.value == 100


class TestParentNodeWithChildren:
    """Test ParentNode with child nodes attached."""

    def test_parent_with_single_child(self, cli_runner: Any) -> None:
        """Test parent node with one child node."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Uppercase(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @option("--text", default="hello")
        @Uppercase.as_decorator()
        def process(text: str) -> None:
            click.echo(f"Result: {text}")

        result = cli_runner.invoke(process, ["--text", "world"])
        assert result.exit_code == 0
        assert "Result: WORLD" in result.output

    def test_parent_with_multiple_children(self, cli_runner: Any) -> None:
        """Test parent node with multiple child nodes."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class AddPrefix(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return f"PREFIX-{value}"

        class AddSuffix(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return f"{value}-SUFFIX"

        @command()
        @option("--text", default="hello")
        @AddPrefix.as_decorator()
        @AddSuffix.as_decorator()
        def process(text: str) -> None:
            click.echo(f"Result: {text}")

        result = cli_runner.invoke(process, ["--text", "test"])
        assert result.exit_code == 0
        assert "Result: PREFIX-test-SUFFIX" in result.output

    def test_processed_value_is_cached(self, cli_runner: Any) -> None:
        """Test that processed value (after children) is cached."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Double(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

        @command()
        @option("--num", type=int, default=5)
        @Double.as_decorator()
        def calculate(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(calculate, ["--num", "10"])
        assert result.exit_code == 0
        assert "Result: 20" in result.output


class TestEnvNode:
    """Test Env node specific functionality."""

    def test_env_load_with_missing_env_name(self) -> None:
        """Test that load raises ValueError when env_name is not provided."""
        from click_extended.core.decorators.env import Env
        from click_extended.core.other.context import Context

        env_node = Env(name="test")
        context = Context(
            root=None,  # type: ignore[arg-type]
            parent=None,  # type: ignore[arg-type]
            current=env_node,
            click_context=None,  # type: ignore[arg-type]
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(ValueError, match="env_name must be provided"):
            env_node.load(context)

    def test_env_required_but_not_set(self) -> None:
        """Test that required env var raises ValueError when not set."""
        import os

        from click_extended.core.decorators.env import Env
        from click_extended.core.other.context import Context

        # Ensure the env var doesn't exist
        env_name = "NONEXISTENT_REQUIRED_VAR_12345"
        if env_name in os.environ:
            del os.environ[env_name]

        env_node = Env(name="test", env_name=env_name, required=True)
        context = Context(
            root=None,  # type: ignore[arg-type]
            parent=None,  # type: ignore[arg-type]
            current=env_node,
            click_context=None,  # type: ignore[arg-type]
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(
            ValueError,
            match=f"Required environment variable '{env_name}' is not set",
        ):
            env_node.load(context, env_name=env_name)

    def test_env_check_required_returns_name_when_missing(self) -> None:
        """Test check_required returns env name when required and missing."""
        import os

        from click_extended.core.decorators.env import Env

        env_name = "NONEXISTENT_CHECK_VAR_67890"
        if env_name in os.environ:
            del os.environ[env_name]

        env_node = Env(name="test", required=True)
        # Simulate what the decorator does - store env_name in decorator_kwargs
        env_node.decorator_kwargs["env_name"] = env_name

        result = env_node.check_required()

        assert result == env_name

    def test_env_check_required_returns_none_when_not_required(self) -> None:
        """Test check_required returns None when not required."""
        import os

        from click_extended.core.decorators.env import Env

        env_name = "NONEXISTENT_OPTIONAL_VAR"
        if env_name in os.environ:
            del os.environ[env_name]

        env_node = Env(name="test", required=False)
        env_node.decorator_kwargs["env_name"] = env_name

        result = env_node.check_required()

        assert result is None

    def test_env_check_required_returns_none_when_set(self) -> None:
        """Test check_required returns None when env var is set."""
        import os

        from click_extended.core.decorators.env import Env

        env_name = "EXISTING_REQUIRED_VAR"
        os.environ[env_name] = "some_value"

        try:
            env_node = Env(name="test", required=True)
            env_node.decorator_kwargs["env_name"] = env_name
            result = env_node.check_required()
            assert result is None
        finally:
            del os.environ[env_name]
