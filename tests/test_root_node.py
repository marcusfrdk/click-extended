"""Tests for the RootNode class and its functionality."""

import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import click
import pytest

from click_extended.core._child_node import ChildNode
from click_extended.core._parent_node import ParentNode
from click_extended.core._root_node import RootNode, RootNodeWrapper
from click_extended.core.argument import Argument
from click_extended.core.command import Command
from click_extended.errors import NoRootError


class ConcreteRootNode(RootNode):
    """Concrete RootNode implementation for testing."""

    @classmethod
    def _get_click_decorator(cls) -> Any:
        """Return a mock click decorator."""
        return click.command

    @classmethod
    def _get_click_cls(cls) -> type[click.Command]:
        """Return the Click Command class."""
        return click.Command


class DummyParentForRoot(ParentNode):
    """Dummy ParentNode that returns a fixed value."""

    def __init__(
        self, name: str, value: Any = "test_value", **kwargs: Any
    ) -> None:
        super().__init__(name=name, **kwargs)
        self.value = value

    def get_raw_value(self) -> Any:
        """Return the test value."""
        return self.value


class DummyChildForRoot(ChildNode):
    """Dummy ChildNode that uppercases strings."""

    def process(self, value: Any, *args: Any, **kwargs: Any) -> Any:
        """Uppercase the value if it's a string."""
        return value.upper() if isinstance(value, str) else value


class TestRootNodeInitialization:
    """Tests for RootNode initialization."""

    def test_init_with_name_only(self) -> None:
        """Test initialization with just a name."""
        node = ConcreteRootNode(name="test")
        assert node.name == "test"
        assert node.parent is None
        assert node.children is not None
        assert len(node.children) == 0
        assert node.tree is not None

    def test_init_with_kwargs(self) -> None:
        """Test initialization with additional kwargs."""
        node = ConcreteRootNode(name="test", custom_param="value")
        assert node.name == "test"
        assert node.tree is not None

    def test_children_initialized_as_empty_dict(self) -> None:
        """Test that children dict is initialized empty."""
        node = ConcreteRootNode(name="test")
        assert node.children is not None
        assert isinstance(node.children, dict)
        assert len(node.children) == 0

    def test_tree_created_automatically(self) -> None:
        """Test that Tree is created automatically on init."""
        node = ConcreteRootNode(name="test")
        assert node.tree is not None
        from click_extended.core._tree import Tree

        assert isinstance(node.tree, Tree)


class TestRootNodeAbstractMethods:
    """Tests for RootNode abstract methods."""

    def test_get_click_decorator_not_implemented(self) -> None:
        """Test that _get_click_decorator must be implemented."""

        class IncompleteRootNode(RootNode):
            @classmethod
            def _get_click_cls(cls) -> type[click.Command]:
                return click.Command

        with pytest.raises(NotImplementedError):
            IncompleteRootNode._get_click_decorator()  # type: ignore

    def test_get_click_cls_not_implemented(self) -> None:
        """Test that _get_click_cls must be implemented."""

        class IncompleteRootNode(RootNode):
            @classmethod
            def _get_click_decorator(cls) -> Any:
                return click.command

        with pytest.raises(NotImplementedError):
            IncompleteRootNode._get_click_cls()  # type: ignore


class TestRootNodeAsDecorator:
    """Tests for RootNode.as_decorator method."""

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_as_decorator_with_explicit_name(
        self, mock_pending: MagicMock
    ) -> None:
        """Test as_decorator with explicit name."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator("custom_name")
        def test_func() -> str:
            return "result"

        assert test_func is not None
        assert hasattr(test_func, "_root_instance")
        assert test_func._root_instance.name == "custom_name"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_as_decorator_infers_name_from_function(
        self, mock_pending: MagicMock
    ) -> None:
        """Test as_decorator infers name from function name."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def my_function() -> str:
            return "result"

        assert my_function._root_instance.name == "my_function"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_as_decorator_with_kwargs(self, mock_pending: MagicMock) -> None:
        """Test as_decorator passes kwargs to Click (not RootNode)."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator(help="Test command help")
        def test_func() -> str:
            return "result"

        assert test_func._underlying.help == "Test command help"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_as_decorator_registers_root(self, mock_pending: MagicMock) -> None:
        """Test that as_decorator registers the root in the tree."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> str:
            return "result"

        assert test_func._root_instance.tree.root is not None
        assert test_func._root_instance.tree.root.name == "test_func"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_as_decorator_with_async_function(
        self, mock_pending: MagicMock
    ) -> None:
        """Test as_decorator with async function converts to sync."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        async def async_func() -> str:
            await asyncio.sleep(0)
            return "async_result"

        assert callable(async_func)


class TestRootNodeValueInjection:
    """Tests for RootNode value injection from parent nodes."""

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_injects_env_parent_value(self, mock_pending: MagicMock) -> None:
        """Test that RootNode injects values from Env parent nodes."""
        parent = DummyParentForRoot(name="test_param", value="injected")
        mock_pending.return_value = [("parent", parent)]

        @ConcreteRootNode.as_decorator()
        def test_func(test_param: str) -> str:
            return test_param

        result = test_func._underlying.callback()
        assert result == "injected"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_injects_multiple_parent_values(
        self, mock_pending: MagicMock
    ) -> None:
        """Test injection of multiple parent node values."""
        parent1 = DummyParentForRoot(name="param1", value="value1")
        parent2 = DummyParentForRoot(name="param2", value="value2")
        mock_pending.return_value = [("parent", parent1), ("parent", parent2)]

        @ConcreteRootNode.as_decorator()
        def test_func(param1: str, param2: str) -> str:
            return f"{param1}_{param2}"

        result = test_func._underlying.callback()
        assert result == "value1_value2"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_processes_values_through_children(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that parent values are processed through child transformations."""
        parent = DummyParentForRoot(name="test_param", value="hello")
        child = DummyChildForRoot(name="uppercase")
        mock_pending.return_value = [("child", child), ("parent", parent)]

        @ConcreteRootNode.as_decorator()
        def test_func(test_param: str) -> str:
            return test_param

        result = test_func._underlying.callback()
        assert result == "HELLO"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_handles_option_parent_nodes(self, mock_pending: MagicMock) -> None:
        """Test that Option parent nodes can be registered."""
        parent = DummyParentForRoot(name="test_option", value="option_value")
        mock_pending.return_value = [("parent", parent)]

        @ConcreteRootNode.as_decorator()
        def test_func(test_option: str) -> str:
            return test_option

        assert test_func is not None
        assert isinstance(test_func, RootNodeWrapper)

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_handles_argument_parent_nodes(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that Argument parent nodes are handled correctly."""
        arg_node = Argument(name="filename")
        mock_pending.return_value = [("parent", arg_node)]

        @ConcreteRootNode.as_decorator()
        def test_func(filename: str) -> str:
            return filename

        assert test_func._underlying is not None


class TestRootNodeWrap:
    """Tests for RootNode.wrap method."""

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_wrap_applies_click_decorator(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that wrap applies the Click decorator."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> str:
            return "result"

        assert isinstance(test_func, RootNodeWrapper)
        assert test_func._underlying is not None  # type: ignore
        assert isinstance(test_func._underlying, click.Command)  # type: ignore

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_wrap_applies_option_decorators(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that wrap handles parent nodes correctly."""
        parent = DummyParentForRoot(name="test_param", value="value")
        mock_pending.return_value = [("parent", parent)]

        @ConcreteRootNode.as_decorator()
        def test_func(test_param: str) -> str:
            return test_param

        assert test_func._underlying is not None  # type: ignore
        assert isinstance(test_func._underlying, click.Command)  # type: ignore

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_wrap_applies_argument_decorators(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that wrap applies Argument decorators to the function."""
        argument = Argument(name="filename")
        mock_pending.return_value = [("parent", argument)]

        @ConcreteRootNode.as_decorator()
        def test_func(filename: str) -> str:
            return filename

        assert test_func._underlying is not None
        assert isinstance(test_func._underlying, click.Command)
        assert len(test_func._underlying.params) > 0

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_wrap_returns_wrapper_with_visualize(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that wrap returns a RootNodeWrapper with visualize method."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> str:
            return "result"

        assert hasattr(test_func, "visualize")
        assert callable(test_func.visualize)


class TestRootNodeVisualize:
    """Tests for RootNode.visualize method."""

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_visualize_with_no_children(
        self, mock_pending: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test visualize with a root node that has no children."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> str:
            return "result"

        test_func.visualize()
        captured = capsys.readouterr()
        assert "test_func" in captured.out

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_visualize_with_parent_nodes(
        self, mock_pending: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test visualize displays parent nodes."""
        parent = DummyParentForRoot(name="test_param")
        mock_pending.return_value = [("parent", parent)]

        @ConcreteRootNode.as_decorator()
        def test_func(test_param: str) -> str:
            return test_param

        test_func.visualize()
        captured = capsys.readouterr()
        assert "test_func" in captured.out
        assert "test_param" in captured.out

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_visualize_with_parent_and_child_nodes(
        self, mock_pending: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test visualize displays parent and child nodes."""
        parent = DummyParentForRoot(name="test_param")
        child = DummyChildForRoot(name="uppercase")
        mock_pending.return_value = [("child", child), ("parent", parent)]

        @ConcreteRootNode.as_decorator()
        def test_func(test_param: str) -> str:
            return test_param

        test_func.visualize()
        captured = capsys.readouterr()
        assert "test_func" in captured.out
        assert "test_param" in captured.out
        assert "uppercase" in captured.out

    def test_visualize_raises_without_root(self) -> None:
        """Test that visualize raises NoRootError when root is None."""
        node = ConcreteRootNode(name="test")
        with pytest.raises(NoRootError):
            node.visualize()


class TestRootNodeWrapper:
    """Tests for RootNodeWrapper class."""

    def test_wrapper_delegates_to_underlying(self) -> None:
        """Test that wrapper delegates attribute access to underlying."""
        mock_command = MagicMock(spec=click.Command)
        mock_command.name = "test_command"
        mock_root = MagicMock(spec=RootNode)

        wrapper = RootNodeWrapper(underlying=mock_command, instance=mock_root)
        assert wrapper.name == "test_command"

    def test_wrapper_has_visualize_method(self) -> None:
        """Test that wrapper has visualize method."""
        mock_command = MagicMock(spec=click.Command)
        mock_root = MagicMock(spec=RootNode)

        wrapper = RootNodeWrapper(underlying=mock_command, instance=mock_root)
        assert hasattr(wrapper, "visualize")
        assert callable(wrapper.visualize)

    def test_wrapper_visualize_calls_root_visualize(self) -> None:
        """Test that wrapper.visualize calls root instance visualize."""
        mock_command = MagicMock(spec=click.Command)
        mock_root = MagicMock(spec=RootNode)

        wrapper = RootNodeWrapper(underlying=mock_command, instance=mock_root)
        wrapper.visualize()
        mock_root.visualize.assert_called_once()

    def test_wrapper_is_callable(self) -> None:
        """Test that wrapper can be called like the underlying object."""
        mock_command = MagicMock(spec=click.Command)
        mock_command.return_value = "result"
        mock_root = MagicMock(spec=RootNode)

        wrapper = RootNodeWrapper(underlying=mock_command, instance=mock_root)
        result = wrapper()
        assert result == "result"
        mock_command.assert_called_once()

    def test_wrapper_passes_args_and_kwargs(self) -> None:
        """Test that wrapper passes args and kwargs to underlying."""
        mock_command = MagicMock()
        mock_root = MagicMock(spec=RootNode)

        wrapper = RootNodeWrapper(underlying=mock_command, instance=mock_root)
        wrapper("arg1", "arg2", key="value")
        mock_command.assert_called_once_with("arg1", "arg2", key="value")


class TestRootNodeInheritance:
    """Tests for RootNode inheritance relationships."""

    def test_rootnode_is_node_subclass(self) -> None:
        """Test that RootNode is a subclass of Node."""
        from click_extended.core._node import Node

        assert issubclass(RootNode, Node)

    def test_rootnode_instance_is_node_instance(self) -> None:
        """Test that RootNode instances are Node instances."""
        from click_extended.core._node import Node

        node = ConcreteRootNode(name="test")
        assert isinstance(node, Node)

    def test_command_is_rootnode_subclass(self) -> None:
        """Test that Command is a subclass of RootNode."""
        assert issubclass(Command, RootNode)

    def test_command_instance_is_rootnode_instance(self) -> None:
        """Test that Command instances are RootNode instances."""
        from click_extended.core.command import command

        @command()
        def test_func() -> None:
            pass

        assert isinstance(test_func._root_instance, RootNode)  # type: ignore


class TestRootNodeEdgeCases:
    """Tests for RootNode edge cases."""

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_empty_kwargs_to_as_decorator(
        self, mock_pending: MagicMock
    ) -> None:
        """Test as_decorator with no kwargs."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> str:
            return "result"

        assert test_func._root_instance.name == "test_func"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_function_with_no_parameters(self, mock_pending: MagicMock) -> None:
        """Test decorator on function with no parameters."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> str:
            return "no_params"

        result = test_func._underlying.callback()
        assert result == "no_params"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_function_with_return_type_annotation(
        self, mock_pending: MagicMock
    ) -> None:
        """Test decorator preserves return type annotation."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> int:
            return 42

        result = test_func._underlying.callback()
        assert result == 42
        assert isinstance(result, int)

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_async_function_converted_to_sync(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that async functions are converted to sync wrappers."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        async def async_func() -> str:
            await asyncio.sleep(0)
            return "async_result"

        result = async_func._underlying.callback()
        assert result == "async_result"

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_multiple_decorators_can_be_created(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that multiple root nodes can be created independently."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def func1() -> str:
            return "func1"

        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def func2() -> str:
            return "func2"

        assert func1._root_instance.name == "func1"
        assert func2._root_instance.name == "func2"
        assert func1._root_instance is not func2._root_instance

    @patch("click_extended.core._tree.get_pending_nodes")
    def test_wrapper_preserves_function_metadata(
        self, mock_pending: MagicMock
    ) -> None:
        """Test that decorator preserves function metadata."""
        mock_pending.return_value = []

        @ConcreteRootNode.as_decorator()
        def test_func() -> str:
            """This is a docstring."""
            return "result"

        assert test_func._underlying.callback.__doc__ == "This is a docstring."
        assert test_func._underlying.callback.__name__ == "test_func"
