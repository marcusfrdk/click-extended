"""Tests for the Context class and its methods."""

from typing import Any
from unittest.mock import MagicMock, Mock

import click
import pytest

from click_extended.core.decorators.argument import Argument
from click_extended.core.decorators.env import Env
from click_extended.core.decorators.group import Group
from click_extended.core.decorators.option import Option
from click_extended.core.decorators.tag import Tag
from click_extended.core.nodes._root_node import RootNode
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.nodes.node import Node
from click_extended.core.other.context import Context


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
        },
        parents={
            "test_arg": mock_argument,
            "test_opt": mock_option,
            "test_env": mock_env,
        },
        tags={"test_tag": mock_tag},
        children={"test_command": mock_command},
        data={"key": "value"},
        debug=False,
    )


class TestContextGetters:
    """Test get_* methods for retrieving nodes."""

    def test_get_root(self, full_context: Context, mock_root_node: Any) -> None:
        """Test get_root() returns the root node."""
        assert full_context.get_root() == mock_root_node

    def test_get_parent_existing(
        self, full_context: Context, mock_option: Any
    ) -> None:
        """Test get_parent() with existing parent."""
        result = full_context.get_parent("test_opt")
        assert result == mock_option

    def test_get_parent_nonexistent(self, full_context: Context) -> None:
        """Test get_parent() with non-existent parent."""
        result = full_context.get_parent("nonexistent")
        assert result is None

    def test_get_node_existing(
        self, full_context: Context, mock_command: Any
    ) -> None:
        """Test get_node() with existing node."""
        result = full_context.get_node("test_command")
        assert result == mock_command

    def test_get_node_nonexistent(self, full_context: Context) -> None:
        """Test get_node() with non-existent node."""
        result = full_context.get_node("nonexistent")
        assert result is None

    def test_get_tag_existing(
        self, full_context: Context, mock_tag: Any
    ) -> None:
        """Test get_tag() with existing tag."""
        result = full_context.get_tag("test_tag")
        assert result == mock_tag

    def test_get_tag_nonexistent(self, full_context: Context) -> None:
        """Test get_tag() with non-existent tag."""
        result = full_context.get_tag("nonexistent")
        assert result is None


class TestContextChildren:
    """Test get_children() and get_siblings() methods."""

    def test_get_children_from_current_parent(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_children() from current parent."""

        child1 = StubChildNode(name="child1")
        child2 = StubChildNode(name="child2")

        mock_option.children = {"child1": child1, "child2": child2}

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_option,
            current=child1,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        children = context.get_children()
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_get_children_by_parent_name(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_children() with specific parent name."""
        child1 = StubChildNode(name="child1")
        mock_option.children = {"child1": child1}

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        children = context.get_children("test_opt")
        assert len(children) == 1
        assert child1 in children

    def test_get_children_nonexistent_parent(
        self, basic_context: Context
    ) -> None:
        """Test get_children() with non-existent parent returns empty list."""
        children = basic_context.get_children("nonexistent")
        assert children == []

    def test_get_children_no_parent(self, mock_click_context: Any) -> None:
        """Test get_children() when parent is not ParentNode."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=Mock(),  # Not a ParentNode
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        children = context.get_children()
        assert children == []

    def test_get_children_parent_no_children(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_children() when parent has no children."""
        mock_option.children = {}

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_option,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        children = context.get_children()
        assert children == []

    def test_get_siblings(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_siblings() returns siblings excluding current."""
        child1 = StubChildNode(name="child1")
        child2 = StubChildNode(name="child2")
        child3 = StubChildNode(name="child3")

        mock_option.children = {
            "child1": child1,
            "child2": child2,
            "child3": child3,
        }

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_option,
            current=child2,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        siblings = context.get_siblings()
        assert len(siblings) == 2
        assert child1 in siblings
        assert child3 in siblings
        assert child2 not in siblings

    def test_get_siblings_current_not_child(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_siblings() when current is not ChildNode."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_option,
            current=mock_option,  # ParentNode, not ChildNode
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        siblings = context.get_siblings()
        assert siblings == []


class TestContextProvided:
    """Test get_provided_* methods."""

    def test_get_provided_arguments(
        self, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_provided_arguments() returns provided arguments."""
        mock_argument.was_provided = True

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_arg": mock_argument},
            tags={},
            children={},
            data={},
        )

        provided = context.get_provided_arguments()
        assert len(provided) == 1
        assert mock_argument in provided

    def test_get_provided_options(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_provided_options() returns provided options."""
        mock_option.was_provided = True

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        provided = context.get_provided_options()
        assert len(provided) == 1
        assert mock_option in provided

    def test_get_provided_envs(
        self, mock_env: Any, mock_click_context: Any
    ) -> None:
        """Test get_provided_envs() returns provided environment variables."""
        mock_env.was_provided = True

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_env": mock_env},
            tags={},
            children={},
            data={},
        )

        provided = context.get_provided_envs()
        assert len(provided) == 1
        assert mock_env in provided

    def test_get_provided_value_exists(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_provided_value() with existing provided parent."""
        mock_option.was_provided = True
        mock_option.cached_value = "test_value"

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        value = context.get_provided_value("test_opt")
        assert value == "test_value"

    def test_get_provided_value_not_provided(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_provided_value() when parent wasn't provided."""
        mock_option.was_provided = False

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        value = context.get_provided_value("test_opt")
        assert value is None

    def test_get_provided_value_nonexistent(
        self, basic_context: Context
    ) -> None:
        """Test get_provided_value() with non-existent parent."""
        value = basic_context.get_provided_value("nonexistent")
        assert value is None

    def test_get_provided_values_all_provided(
        self,
        mock_option: Any,
        mock_argument: Any,
        mock_env: Any,
        mock_click_context: Any,
    ) -> None:
        """Test get_provided_values() returns all provided parent values."""
        mock_option.was_provided = True
        mock_option.get_value = Mock(return_value="opt_value")
        mock_argument.was_provided = True
        mock_argument.get_value = Mock(return_value="arg_value")
        mock_env.was_provided = True
        mock_env.get_value = Mock(return_value="env_value")

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={
                "test_opt": mock_option,
                "test_arg": mock_argument,
                "test_env": mock_env,
            },
            tags={},
            children={},
            data={},
        )

        values = context.get_provided_values()
        assert len(values) == 3
        assert values["test_opt"] == "opt_value"
        assert values["test_arg"] == "arg_value"
        assert values["test_env"] == "env_value"
        mock_option.get_value.assert_called_once()
        mock_argument.get_value.assert_called_once()
        mock_env.get_value.assert_called_once()

    def test_get_provided_values_some_provided(
        self, mock_option: Any, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_provided_values() filters out unprovided parents."""
        mock_option.was_provided = True
        mock_option.get_value = Mock(return_value="opt_value")
        mock_argument.was_provided = False
        mock_argument.get_value = Mock(return_value="arg_value")

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option, "test_arg": mock_argument},
            tags={},
            children={},
            data={},
        )

        values = context.get_provided_values()
        assert len(values) == 1
        assert values["test_opt"] == "opt_value"
        assert "test_arg" not in values
        mock_option.get_value.assert_called_once()
        mock_argument.get_value.assert_not_called()

    def test_get_provided_values_none_provided(
        self, mock_option: Any, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_provided_values() returns empty dict when nothing provided."""
        mock_option.was_provided = False
        mock_argument.was_provided = False

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option, "test_arg": mock_argument},
            tags={},
            children={},
            data={},
        )

        values = context.get_provided_values()
        assert values == {}

    def test_get_provided_values_empty_parents(
        self, basic_context: Context
    ) -> None:
        """Test get_provided_values() with no parents."""
        values = basic_context.get_provided_values()
        assert values == {}


class TestContextMissing:
    """Test get_missing_* methods."""

    def test_get_missing_arguments(
        self, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_missing_arguments() returns unprovided arguments."""
        mock_argument.was_provided = False

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_arg": mock_argument},
            tags={},
            children={},
            data={},
        )

        missing = context.get_missing_arguments()
        assert len(missing) == 1
        assert mock_argument in missing

    def test_get_missing_options(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_missing_options() returns unprovided options."""
        mock_option.was_provided = False

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        missing = context.get_missing_options()
        assert len(missing) == 1
        assert mock_option in missing

    def test_get_missing_envs(
        self, mock_env: Any, mock_click_context: Any
    ) -> None:
        """Test get_missing_envs() returns unprovided envs."""
        mock_env.was_provided = False

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_env": mock_env},
            tags={},
            children={},
            data={},
        )

        missing = context.get_missing_envs()
        assert len(missing) == 1
        assert mock_env in missing

    def test_get_missing_filters_provided(
        self, mock_argument: Any, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_missing_* methods filter out provided parents."""
        mock_argument.was_provided = True
        mock_option.was_provided = False

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_arg": mock_argument, "test_opt": mock_option},
            tags={},
            children={},
            data={},
        )

        missing_args = context.get_missing_arguments()
        missing_opts = context.get_missing_options()

        assert len(missing_args) == 0
        assert len(missing_opts) == 1
        assert mock_option in missing_opts


class TestContextCurrent:
    """Test current node related methods."""

    def test_get_current_tags_from_parent_node(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_tags() returns tags from current ParentNode."""
        mock_option.tags = ["tag1", "tag2"]

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=mock_option,
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        tags = context.get_current_tags()
        assert len(tags) == 2
        assert "tag1" in tags
        assert "tag2" in tags

    def test_get_current_tags_not_parent_node(
        self, mock_click_context: Any
    ) -> None:
        """Test get_current_tags() returns empty list for non-ParentNode."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        tags = context.get_current_tags()
        assert tags == []

    def test_get_current_tags_no_current(self, basic_context: Context) -> None:
        """Test get_current_tags() when current is None."""
        tags = basic_context.get_current_tags()
        assert tags == []

    def test_get_values(
        self, mock_option: Any, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_values() returns all parent values."""
        mock_option.get_value = Mock(return_value="opt_value")
        mock_argument.get_value = Mock(return_value="arg_value")

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option, "test_arg": mock_argument},
            tags={},
            children={},
            data={},
        )

        values = context.get_values()
        assert len(values) == 2
        assert values["test_opt"] == "opt_value"
        assert values["test_arg"] == "arg_value"
        mock_option.get_value.assert_called_once()
        mock_argument.get_value.assert_called_once()

    def test_get_values_empty(self, basic_context: Context) -> None:
        """Test get_values() with no parents."""
        values = basic_context.get_values()
        assert values == {}


class TestContextTagged:
    """Test get_tagged() method."""

    def test_get_tagged_with_tags(
        self, mock_option: Any, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_tagged() groups parents by tags."""
        mock_option.tags = ["tag1", "tag2"]
        mock_argument.tags = ["tag1"]

        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=None,
            click_context=mock_click_context,
            nodes={},
            parents={"test_opt": mock_option, "test_arg": mock_argument},
            tags={},
            children={},
            data={},
        )

        tagged = context.get_tagged()
        assert "tag1" in tagged
        assert "tag2" in tagged
        assert len(tagged["tag1"]) == 2
        assert len(tagged["tag2"]) == 1
        assert mock_option in tagged["tag1"]
        assert mock_argument in tagged["tag1"]
        assert mock_option in tagged["tag2"]

    def test_get_tagged_no_tags(self, basic_context: Context) -> None:
        """Test get_tagged() with no tagged parents."""
        tagged = basic_context.get_tagged()
        assert tagged == {}


class TestContextCurrentParentTyped:
    """Test get_current_parent_as_parent() and get_current_parent_as_tag()."""

    def test_get_current_parent_as_parent_with_option(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_parent() with Option parent."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_option,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        parent = context.get_current_parent_as_parent()
        assert parent == mock_option

    def test_get_current_parent_as_parent_with_argument(
        self, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_parent() with Argument parent."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_argument,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        parent = context.get_current_parent_as_parent()
        assert parent == mock_argument

    def test_get_current_parent_as_parent_with_env(
        self, mock_env: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_parent() with Env parent."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_env,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        parent = context.get_current_parent_as_parent()
        assert parent == mock_env

    def test_get_current_parent_as_parent_with_tag_raises(
        self, mock_tag: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_parent() raises when parent is Tag."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_tag,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(
            RuntimeError, match="Parent node is not a ParentNode instance"
        ):
            context.get_current_parent_as_parent()

    def test_get_current_parent_as_parent_no_parent_raises(
        self, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_parent() raises when no parent."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(
            RuntimeError, match="No parent node in current context"
        ):
            context.get_current_parent_as_parent()

    def test_get_current_parent_as_tag_success(
        self, mock_tag: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_tag() with Tag parent."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_tag,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        tag = context.get_current_parent_as_tag()
        assert tag == mock_tag

    def test_get_current_parent_as_tag_with_option_raises(
        self, mock_option: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_tag() raises when parent is Option."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_option,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(
            RuntimeError, match="Parent node is not a Tag instance"
        ):
            context.get_current_parent_as_tag()

    def test_get_current_parent_as_tag_with_argument_raises(
        self, mock_argument: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_tag() raises when parent is Argument."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_argument,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(
            RuntimeError, match="Parent node is not a Tag instance"
        ):
            context.get_current_parent_as_tag()

    def test_get_current_parent_as_tag_with_env_raises(
        self, mock_env: Any, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_tag() raises when parent is Env."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=mock_env,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(
            RuntimeError, match="Parent node is not a Tag instance"
        ):
            context.get_current_parent_as_tag()

    def test_get_current_parent_as_tag_no_parent_raises(
        self, mock_click_context: Any
    ) -> None:
        """Test get_current_parent_as_tag() raises when no parent."""
        context = Context(
            root=Mock(),  # type: ignore[arg-type]
            parent=None,
            current=StubChildNode(name="child"),
            click_context=mock_click_context,
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        with pytest.raises(
            RuntimeError, match="No parent node in current context"
        ):
            context.get_current_parent_as_tag()


class TestContextEdgeCases:
    """Test edge cases and error conditions."""

    pass
