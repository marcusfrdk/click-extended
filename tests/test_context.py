"""Tests for the Context class and its methods."""

from typing import Any
from unittest.mock import MagicMock, Mock

import click
import pytest

from click_extended.core._root_node import RootNode
from click_extended.core.argument import Argument
from click_extended.core.child_node import ChildNode
from click_extended.core.context import Context
from click_extended.core.env import Env
from click_extended.core.global_node import GlobalNode
from click_extended.core.group import Group
from click_extended.core.node import Node
from click_extended.core.option import Option
from click_extended.core.tag import Tag


# Simple stub classes for testing isinstance checks
class StubNode(Node):
    """Stub Node for testing."""

    pass


class StubChildNode(ChildNode):
    """Stub ChildNode for testing."""

    pass


@pytest.fixture
def mock_click_context() -> MagicMock:
    """Create a mock Click context."""
    ctx = MagicMock(spec=click.Context)
    ctx.meta = {}
    return ctx


@pytest.fixture
def mock_root_node() -> Mock:
    """Create a mock RootNode."""
    root = Mock(spec=RootNode)
    root.name = "root"
    root.__class__ = RootNode  # type: ignore[assignment]
    return root


@pytest.fixture
def mock_argument() -> Mock:
    """Create a mock Argument node."""
    arg = Mock(spec=Argument)
    arg.name = "test_arg"
    arg.tags = []
    arg.__class__ = Argument  # type: ignore[assignment]
    arg.was_provided = Mock(return_value=True)
    arg.get_value = Mock(return_value="arg_value")
    arg.get_raw_value = Mock(return_value="raw_arg_value")
    return arg


@pytest.fixture
def mock_option() -> Mock:
    """Create a mock Option node."""
    opt = Mock(spec=Option)
    opt.name = "test_opt"
    opt.tags = []
    opt.__class__ = Option  # type: ignore[assignment]
    opt.was_provided = Mock(return_value=True)
    opt.get_value = Mock(return_value="opt_value")
    opt.get_raw_value = Mock(return_value="raw_opt_value")
    return opt


@pytest.fixture
def mock_env() -> Mock:
    """Create a mock Env node."""
    env = Mock(spec=Env)
    env.name = "test_env"
    env.tags = []
    env.__class__ = Env  # type: ignore[assignment]
    env.was_provided = Mock(return_value=True)
    env.get_value = Mock(return_value="env_value")
    env.get_raw_value = Mock(return_value="raw_env_value")
    return env


@pytest.fixture
def mock_tag() -> Mock:
    """Create a mock Tag node."""
    tag = Mock(spec=Tag)
    tag.name = "test_tag"
    tag.__class__ = Tag  # type: ignore[assignment]
    return tag


@pytest.fixture
def mock_command() -> StubChildNode:
    """Create a stub ChildNode (not a RootNode)."""
    return StubChildNode(name="test_command")


@pytest.fixture
def mock_group() -> Mock:
    """Create a mock Group (ChildNode)."""
    grp = Mock(spec=Group)
    grp.name = "test_group"
    grp.__class__ = Group  # type: ignore[assignment]
    return grp


@pytest.fixture
def mock_global_node() -> Mock:
    """Create a mock GlobalNode."""
    gnode = Mock(spec=GlobalNode)
    gnode.name = "test_global"
    gnode.__class__ = GlobalNode  # type: ignore[assignment]
    return gnode


@pytest.fixture
def basic_context(mock_root_node: Any, mock_click_context: Any) -> Context:
    """Create a basic Context with minimal setup."""
    return Context(
        root=mock_root_node,
        current=None,
        parent=None,
        click_context=mock_click_context,
        nodes={},
        parents={},
        tags={},
        children={},
        globals={},
        data={},
        debug=False,
    )


@pytest.fixture
def full_context(
    mock_root_node: Any,
    mock_click_context: Any,
    mock_argument: Any,
    mock_option: Any,
    mock_env: Any,
    mock_tag: Any,
    mock_command: Any,
    mock_global_node: Any,
) -> Context:
    """Create a fully populated Context for testing."""
    return Context(
        root=mock_root_node,
        current=mock_command,
        parent=mock_option,
        click_context=mock_click_context,
        nodes={
            "root": mock_root_node,
            "test_arg": mock_argument,
            "test_opt": mock_option,
            "test_env": mock_env,
            "test_tag": mock_tag,
            "test_command": mock_command,
            "test_global": mock_global_node,
        },
        parents={
            "test_arg": mock_argument,
            "test_opt": mock_option,
            "test_env": mock_env,
        },
        tags={"test_tag": mock_tag},
        children={"test_command": mock_command},
        globals={"test_global": mock_global_node},
        data={"key": "value"},
        debug=False,
    )


def _replace_current(context: Context, current: Any) -> Context:
    """Helper to create a new Context with a different current node."""
    return Context(
        root=context.root,
        current=current,
        parent=context.parent,
        click_context=context.click_context,
        nodes=context.nodes,
        parents=context.parents,
        tags=context.tags,
        children=context.children,
        globals=context.globals,
        data=context.data,
        debug=context.debug,
    )


class TestContextCheckMethods:
    """Test is_* methods for node type checking."""

    def test_is_root_with_root_node(
        self, basic_context: Context, mock_root_node: Any
    ) -> None:
        """Test is_root() returns True when current is RootNode."""
        context = _replace_current(basic_context, mock_root_node)
        assert context.is_root() is True

    def test_is_root_with_non_root_node(
        self, basic_context: Context, mock_command: Any
    ) -> None:
        """Test is_root() returns False when current is not RootNode."""
        context = _replace_current(basic_context, mock_command)
        assert context.is_root() is False

    def test_is_root_with_none(self, basic_context: Context) -> None:
        """Test is_root() returns False when current is None."""
        assert basic_context.is_root() is False

    def test_is_parent_with_parent_node(
        self, basic_context: Context, mock_option: Any
    ) -> None:
        """Test is_parent() returns True when current is ParentNode."""
        context = _replace_current(basic_context, mock_option)
        assert context.is_parent() is True

    def test_is_parent_with_non_parent_node(
        self, basic_context: Context, mock_command: Any
    ) -> None:
        """Test is_parent() returns False when current is not ParentNode."""
        context = _replace_current(basic_context, mock_command)
        assert context.is_parent() is False

    def test_is_global_with_global_node(
        self, basic_context: Context, mock_global_node: Any
    ) -> None:
        """Test is_global() returns True when current is GlobalNode."""
        context = _replace_current(basic_context, mock_global_node)
        assert context.is_global() is True

    def test_is_global_with_non_global_node(
        self, basic_context: Context, mock_command: Any
    ) -> None:
        """Test is_global() returns False when current is not GlobalNode."""
        context = _replace_current(basic_context, mock_command)
        assert context.is_global() is False

    def test_is_tag_with_tag_parent(
        self, basic_context: Context, mock_tag: Any, mock_command: Any
    ) -> None:
        """Test is_tag() returns True when parent is Tag."""
        context = _replace_current(basic_context, mock_command)
        context = Context(
            root=context.root,
            parent=mock_tag,
            current=context.current,
            click_context=context.click_context,
            nodes=context.nodes,
            parents=context.parents,
            tags=context.tags,
            children=context.children,
            globals=context.globals,
            data=context.data,
            debug=context.debug,
        )
        assert context.is_tag() is True

    def test_is_tag_with_non_tag_parent(
        self, basic_context: Context, mock_option: Any, mock_command: Any
    ) -> None:
        """Test is_tag() returns False when parent is not Tag."""
        context = _replace_current(basic_context, mock_command)
        context = Context(
            root=context.root,
            parent=mock_option,
            current=context.current,
            click_context=context.click_context,
            nodes=context.nodes,
            parents=context.parents,
            tags=context.tags,
            children=context.children,
            globals=context.globals,
            data=context.data,
            debug=context.debug,
        )
        assert context.is_tag() is False

    def test_is_child_with_child_node(
        self, basic_context: Context, mock_command: Any
    ) -> None:
        """Test is_child() returns True when current is ChildNode."""
        context = _replace_current(basic_context, mock_command)
        assert context.is_child() is True

    def test_is_child_with_non_child_node(
        self, basic_context: Context, mock_option: Any
    ) -> None:
        """Test is_child() returns False when current is not ChildNode."""
        context = _replace_current(basic_context, mock_option)
        assert context.is_child() is False

    def test_is_argument_with_argument_node(
        self, basic_context: Context, mock_argument: Any
    ) -> None:
        """Test is_argument() returns True when current is Argument."""
        context = _replace_current(basic_context, mock_argument)
        assert context.is_argument() is True

    def test_is_argument_with_non_argument_node(
        self, basic_context: Context, mock_option: Any
    ) -> None:
        """Test is_argument() returns False when current is not Argument."""
        context = _replace_current(basic_context, mock_option)
        assert context.is_argument() is False

    def test_is_option_with_option_node(
        self, basic_context: Context, mock_option: Any
    ) -> None:
        """Test is_option() returns True when current is Option."""
        context = _replace_current(basic_context, mock_option)
        assert context.is_option() is True

    def test_is_option_with_non_option_node(
        self, basic_context: Context, mock_argument: Any
    ) -> None:
        """Test is_option() returns False when current is not Option."""
        context = _replace_current(basic_context, mock_argument)
        assert context.is_option() is False

    def test_is_env_with_env_node(
        self, basic_context: Context, mock_env: Any
    ) -> None:
        """Test is_env() returns True when current is Env."""
        context = _replace_current(basic_context, mock_env)
        assert context.is_env() is True

    def test_is_env_with_non_env_node(
        self, basic_context: Context, mock_option: Any
    ) -> None:
        """Test is_env() returns False when current is not Env."""
        context = _replace_current(basic_context, mock_option)
        assert context.is_env() is False

    def test_is_tagged_with_tagged_parent_node(
        self, basic_context: Context, mock_option: Any
    ) -> None:
        """Test is_tagged() returns True when current has tags."""
        mock_option.tags = ["tag1", "tag2"]
        context = _replace_current(basic_context, mock_option)
        assert context.is_tagged() is True

    def test_is_tagged_with_untagged_parent_node(
        self, basic_context: Context, mock_option: Any
    ) -> None:
        """Test is_tagged() returns False when current has no tags."""
        mock_option.tags = []
        context = _replace_current(basic_context, mock_option)
        assert context.is_tagged() is False

    def test_is_tagged_with_non_parent_node(
        self, basic_context: Context, mock_command: Any
    ) -> None:
        """Test is_tagged() returns False when current is not ParentNode."""
        context = _replace_current(basic_context, mock_command)
        assert context.is_tagged() is False


class TestContextGetters:
    """Test get_* methods for retrieving nodes."""

    pass


class TestContextChildren:
    """Test get_children() and get_siblings() methods."""

    pass


class TestContextProvided:
    """Test get_provided_* methods."""

    pass


class TestContextMissing:
    """Test get_missing_* methods."""

    pass


class TestContextCurrent:
    """Test current node related methods."""

    pass


class TestContextTagged:
    """Test get_tagged() method."""

    pass


class TestContextEdgeCases:
    """Test edge cases and error conditions."""

    pass
