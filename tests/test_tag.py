"""Comprehensive tests for Tag functionality."""

from typing import Any

import pytest

from click_extended.core.decorators.tag import Tag, tag
from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other._tree import Tree


class ConcreteParentNode(ParentNode):
    """Concrete implementation of ParentNode for testing."""

    def load(self, context: Any, *args: Any, **kwargs: Any) -> Any:
        """Simple load implementation that returns the default value."""
        return self.default


class TestTagInit:
    """Test Tag initialization and setup."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_tag_initialization_with_name(self) -> None:
        """Test Tag initializes correctly with name."""
        tag_node = Tag(name="validation")

        assert tag_node.name == "validation"

    def test_tag_children_dict_initialized(self) -> None:
        """Test that children dict is initialized empty."""
        tag_node = Tag(name="test_tag")

        assert tag_node.children == {}
        assert isinstance(tag_node.children, dict)

    def test_tag_parent_nodes_list_initialized(self) -> None:
        """Test that parent_nodes list is initialized empty."""
        tag_node = Tag(name="test_tag")

        assert tag_node.parent_nodes == []
        assert isinstance(tag_node.parent_nodes, list)

    def test_tag_extends_node_class(self) -> None:
        """Test that Tag inherits from Node."""
        from click_extended.core.nodes.node import Node

        tag_node = Tag(name="test_tag")

        assert isinstance(tag_node, Node)

    def test_tag_name_stored_correctly(self) -> None:
        """Test that name attribute is set correctly."""
        tag_node = Tag(name="my_custom_tag")

        assert tag_node.name == "my_custom_tag"
        assert hasattr(tag_node, "name")

    def test_tag_repr_format(self) -> None:
        """Test Tag string representation format."""
        tag_node = Tag(name="api_config")

        repr_str = repr(tag_node)
        assert "Tag" in repr_str
        assert "api_config" in repr_str
        assert repr_str == "<Tag name='api_config'>"


class TestTagParentNodeManagement:
    """Test parent_nodes list management."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_parent_nodes_list_empty_on_init(self) -> None:
        """Test parent_nodes list starts empty."""
        tag_node = Tag(name="test_tag")

        assert len(tag_node.parent_nodes) == 0
        assert tag_node.parent_nodes == []

    def test_parent_nodes_can_be_added(self) -> None:
        """Test that ParentNode can be added to list."""
        tag_node = Tag(name="test_tag")
        parent = ConcreteParentNode(name="option1")

        tag_node.parent_nodes.append(parent)

        assert len(tag_node.parent_nodes) == 1
        assert tag_node.parent_nodes[0] is parent

    def test_multiple_parent_nodes_stored(self) -> None:
        """Test multiple parent nodes can be stored."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="option1")
        parent2 = ConcreteParentNode(name="option2")
        parent3 = ConcreteParentNode(name="option3")

        tag_node.parent_nodes.append(parent1)
        tag_node.parent_nodes.append(parent2)
        tag_node.parent_nodes.append(parent3)

        assert len(tag_node.parent_nodes) == 3
        assert tag_node.parent_nodes[0] is parent1
        assert tag_node.parent_nodes[1] is parent2
        assert tag_node.parent_nodes[2] is parent3

    def test_parent_nodes_reference_preserved(self) -> None:
        """Test that parent node references are preserved."""
        tag_node = Tag(name="test_tag")
        parent = ConcreteParentNode(name="option1")

        tag_node.parent_nodes.append(parent)

        assert tag_node.parent_nodes[0] is parent
        assert id(tag_node.parent_nodes[0]) == id(parent)

    def test_parent_nodes_order_preserved(self) -> None:
        """Test that order of parent nodes is maintained."""
        tag_node = Tag(name="test_tag")
        parents = [ConcreteParentNode(name=f"opt{i}") for i in range(5)]

        for parent in parents:
            tag_node.parent_nodes.append(parent)

        for i, parent in enumerate(parents):
            assert tag_node.parent_nodes[i] is parent

    def test_get_provided_values_empty_when_none_provided(self) -> None:
        """Test get_provided_values returns empty list when none provided."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="option1")
        parent2 = ConcreteParentNode(name="option2")

        parent1.was_provided = False
        parent2.was_provided = False

        tag_node.parent_nodes.append(parent1)
        tag_node.parent_nodes.append(parent2)

        provided = tag_node.get_provided_values()
        assert provided == []

    def test_get_provided_values_returns_provided_names(self) -> None:
        """Test get_provided_values returns names of provided params."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="option1")
        parent2 = ConcreteParentNode(name="option2")
        parent3 = ConcreteParentNode(name="option3")

        parent1.was_provided = True
        parent2.was_provided = False
        parent3.was_provided = True

        tag_node.parent_nodes.append(parent1)
        tag_node.parent_nodes.append(parent2)
        tag_node.parent_nodes.append(parent3)

        provided = tag_node.get_provided_values()
        assert provided == ["option1", "option3"]


class TestTagGetValue:
    """Test Tag.get_value() method."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_get_value_returns_empty_dict_no_parents(self) -> None:
        """Test get_value returns empty dict when no parent nodes."""
        tag_node = Tag(name="test_tag")

        value = tag_node.get_value()

        assert value == {}
        assert isinstance(value, dict)

    def test_get_value_returns_dict_with_parent_values(self) -> None:
        """Test get_value returns dict with parent values."""
        tag_node = Tag(name="test_tag")
        parent = ConcreteParentNode(name="option1", default="test_value")
        parent.cached_value = "test_value"

        tag_node.parent_nodes.append(parent)

        value = tag_node.get_value()

        assert isinstance(value, dict)
        assert "option1" in value
        assert value["option1"] == "test_value"

    def test_get_value_dict_keys_are_parent_names(self) -> None:
        """Test get_value dict keys are parent node names."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="api_key")
        parent2 = ConcreteParentNode(name="api_url")

        parent1.cached_value = "key123"
        parent2.cached_value = "https://api.example.com"

        tag_node.parent_nodes.append(parent1)
        tag_node.parent_nodes.append(parent2)

        value = tag_node.get_value()

        assert set(value.keys()) == {"api_key", "api_url"}

    def test_get_value_includes_none_for_unprovided(self) -> None:
        """Test get_value includes None for unprovided params."""
        tag_node = Tag(name="test_tag")
        parent = ConcreteParentNode(name="option1")
        parent.cached_value = None

        tag_node.parent_nodes.append(parent)

        value = tag_node.get_value()

        assert "option1" in value
        assert value["option1"] is None

    def test_get_value_with_multiple_parents(self) -> None:
        """Test get_value with multiple parent nodes."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="username")
        parent2 = ConcreteParentNode(name="email")
        parent3 = ConcreteParentNode(name="age")

        parent1.cached_value = "john"
        parent2.cached_value = "john@example.com"
        parent3.cached_value = 25

        tag_node.parent_nodes.append(parent1)
        tag_node.parent_nodes.append(parent2)
        tag_node.parent_nodes.append(parent3)

        value = tag_node.get_value()

        assert len(value) == 3
        assert value["username"] == "john"
        assert value["email"] == "john@example.com"
        assert value["age"] == 25

    def test_get_value_with_provided_and_unprovided(self) -> None:
        """Test get_value with mix of provided and unprovided params."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="provided_opt")
        parent2 = ConcreteParentNode(name="default_opt")

        parent1.cached_value = "user_value"
        parent1.was_provided = True
        parent2.cached_value = "default_value"
        parent2.was_provided = False

        tag_node.parent_nodes.append(parent1)
        tag_node.parent_nodes.append(parent2)

        value = tag_node.get_value()

        assert value["provided_opt"] == "user_value"
        assert value["default_opt"] == "default_value"


class TestTagGetProvidedValues:
    """Test Tag.get_provided_values() method."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_get_provided_values_empty_list_no_parents(self) -> None:
        """Test get_provided_values returns empty list with no parents."""
        tag_node = Tag(name="test_tag")

        provided = tag_node.get_provided_values()

        assert provided == []
        assert isinstance(provided, list)

    def test_get_provided_values_only_provided_parents(self) -> None:
        """Test get_provided_values only includes provided param names."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="option1")
        parent2 = ConcreteParentNode(name="option2")
        parent3 = ConcreteParentNode(name="option3")

        parent1.was_provided = True
        parent2.was_provided = True
        parent3.was_provided = True

        tag_node.parent_nodes.extend([parent1, parent2, parent3])

        provided = tag_node.get_provided_values()

        assert len(provided) == 3
        assert "option1" in provided
        assert "option2" in provided
        assert "option3" in provided

    def test_get_provided_values_excludes_unprovided(self) -> None:
        """Test get_provided_values excludes unprovided params."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="provided1")
        parent2 = ConcreteParentNode(name="unprovided")
        parent3 = ConcreteParentNode(name="provided2")

        parent1.was_provided = True
        parent2.was_provided = False
        parent3.was_provided = True

        tag_node.parent_nodes.extend([parent1, parent2, parent3])

        provided = tag_node.get_provided_values()

        assert len(provided) == 2
        assert "provided1" in provided
        assert "provided2" in provided
        assert "unprovided" not in provided

    def test_get_provided_values_with_multiple_provided(self) -> None:
        """Test get_provided_values with multiple provided params."""
        tag_node = Tag(name="test_tag")
        parents = [ConcreteParentNode(name=f"opt{i}") for i in range(5)]

        # Mark first, third, and fifth as provided
        for i, parent in enumerate(parents):
            parent.was_provided = i % 2 == 0
            tag_node.parent_nodes.append(parent)

        provided = tag_node.get_provided_values()

        assert len(provided) == 3
        assert "opt0" in provided
        assert "opt2" in provided
        assert "opt4" in provided

    def test_get_provided_values_order_matches_parent_nodes(self) -> None:
        """Test get_provided_values preserves parent_nodes order."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="first")
        parent2 = ConcreteParentNode(name="second")
        parent3 = ConcreteParentNode(name="third")

        parent1.was_provided = True
        parent2.was_provided = True
        parent3.was_provided = True

        tag_node.parent_nodes.extend([parent1, parent2, parent3])

        provided = tag_node.get_provided_values()

        assert provided == ["first", "second", "third"]

    def test_get_provided_values_dynamic_updates(self) -> None:
        """Test get_provided_values updates when was_provided changes."""
        tag_node = Tag(name="test_tag")
        parent = ConcreteParentNode(name="option1")
        parent.was_provided = False

        tag_node.parent_nodes.append(parent)

        # Initially not provided
        provided = tag_node.get_provided_values()
        assert provided == []

        # Change to provided
        parent.was_provided = True
        provided = tag_node.get_provided_values()
        assert provided == ["option1"]


class TestTagAsDecorator:
    """Test Tag.as_decorator() class method."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_as_decorator_returns_callable(self) -> None:
        """Test as_decorator returns a callable decorator."""
        decorator = Tag.as_decorator(name="test_tag")

        assert callable(decorator)

    def test_as_decorator_creates_tag_instance(self) -> None:
        """Test as_decorator creates Tag instance."""

        @Tag.as_decorator(name="validation")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        assert pending[0][0] == "tag"
        assert isinstance(pending[0][1], Tag)
        assert pending[0][1].name == "validation"

    def test_as_decorator_queues_in_tree(self) -> None:
        """Test as_decorator queues tag in Tree._pending_nodes."""

        @Tag.as_decorator(name="test_tag")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        assert pending[0][0] == "tag"

    def test_as_decorator_preserves_function(self) -> None:
        """Test decorated function remains callable."""

        @Tag.as_decorator(name="test_tag")
        def test_func() -> str:
            return "result"

        assert callable(test_func)
        assert test_func() == "result"

    def test_as_decorator_preserves_function_name(self) -> None:
        """Test decorator preserves function __name__."""

        @Tag.as_decorator(name="test_tag")
        def my_function() -> None:
            pass

        assert my_function.__name__ == "my_function"

    def test_as_decorator_preserves_function_docstring(self) -> None:
        """Test decorator preserves function __doc__."""

        @Tag.as_decorator(name="test_tag")
        def documented() -> None:
            """This is a documented function."""
            pass

        assert documented.__doc__ is not None
        assert "documented function" in documented.__doc__

    def test_multiple_tags_with_decorator(self) -> None:
        """Test multiple tags can be created with decorator."""

        @Tag.as_decorator(name="tag1")
        def func1() -> None:
            pass

        @Tag.as_decorator(name="tag2")
        def func2() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 2
        assert pending[0][1].name == "tag1"
        assert pending[1][1].name == "tag2"


class TestTagDecoratorFunction:
    """Test tag() decorator function."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_tag_function_creates_tag(self) -> None:
        """Test tag() function creates Tag instance."""

        @tag(name="validation")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        assert isinstance(pending[0][1], Tag)
        assert pending[0][1].name == "validation"

    def test_tag_function_queues_in_tree(self) -> None:
        """Test tag() queues tag in Tree._pending_nodes."""

        @tag(name="test_tag")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        assert pending[0][0] == "tag"

    def test_tag_function_with_name(self) -> None:
        """Test tag() function with name parameter."""

        @tag(name="custom_tag")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert pending[0][1].name == "custom_tag"

    def test_tag_decorator_on_command(self, cli_runner: Any) -> None:
        """Test tag() decorator works with @command."""
        import click

        from click_extended.core.decorators.command import command

        @command()
        @tag(name="test_tag")
        def cmd() -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_tag_decorator_on_group(self, cli_runner: Any) -> None:
        """Test tag() decorator works with @group."""
        from click_extended.core.decorators.group import group

        @group()
        @tag(name="test_tag")
        def cli() -> None:
            """Test CLI."""
            pass

        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_multiple_tag_decorators_on_function(self) -> None:
        """Test multiple tag() decorators on same function."""

        @tag(name="tag1")
        @tag(name="tag2")
        @tag(name="tag3")
        def test_func() -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 3
        names = [node[1].name for node in pending]
        assert "tag1" in names
        assert "tag2" in names
        assert "tag3" in names


class TestTagIntegrationWithChildren:
    """Test Tag integration with ChildNode."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_child_handle_tag_receives_tag(self, cli_runner: Any) -> None:
        """Test ChildNode.handle_tag() receives tag values."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode

        tag_values_received = {}

        class TestChild(ChildNode):
            def handle_tag(
                self, value: Any, context: Any, **kwargs: Any
            ) -> None:
                tag_values_received.update(value)

        @command()
        @option("--opt", tags=["validation"])
        @tag(name="validation")
        @TestChild.as_decorator(name="test_child")
        def cmd(opt: str) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt=value"])
        assert result.exit_code == 0
        assert "opt" in tag_values_received

    def test_child_validates_tag_values(self, cli_runner: Any) -> None:
        """Test ChildNode can validate via handle_tag()."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode

        class ValidatingChild(ChildNode):
            def handle_tag(
                self, value: Any, context: Any, **kwargs: Any
            ) -> None:
                # Check if any values were provided
                provided_count = sum(1 for v in value.values() if v is not None)
                if provided_count == 0:
                    raise click.UsageError("At least one option required")

        @command()
        @option("--opt1", tags=["required"])
        @option("--opt2", tags=["required"])
        @tag(name="required")
        @ValidatingChild.as_decorator(name="validator")
        def cmd(opt1: str, opt2: str) -> None:
            click.echo("Success")

        # No options should fail
        result = cli_runner.invoke(cmd, [])
        assert result.exit_code != 0
        assert "At least one option required" in result.output

        # With option should succeed
        result = cli_runner.invoke(cmd, ["--opt1=value"])
        assert result.exit_code == 0

    def test_child_access_tag_get_value(self, cli_runner: Any) -> None:
        """Test ChildNode can access tag values via handle_tag()."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode

        captured_values: dict[str, Any] = {}

        class CapturingChild(ChildNode):
            def handle_tag(
                self, value: Any, context: Any, **kwargs: Any
            ) -> None:
                captured_values.update(value)

        @command()
        @option("--opt1", tags=["capture"], default="default1")
        @option("--opt2", tags=["capture"], default="default2")
        @tag(name="capture")
        @CapturingChild.as_decorator(name="capturer")
        def cmd(opt1: str, opt2: str) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt1=user1"])
        assert result.exit_code == 0
        assert captured_values["opt1"] == "user1"
        assert captured_values["opt2"] == "default2"

    def test_multiple_children_with_same_tag(self, cli_runner: Any) -> None:
        """Test multiple ChildNodes can handle same tag."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode

        child1_called: list[str] = []
        child2_called: list[str] = []

        class Child1(ChildNode):
            def handle_tag(
                self, value: Any, context: Any, **kwargs: Any
            ) -> None:
                child1_called.append("called")

        class Child2(ChildNode):
            def handle_tag(
                self, value: Any, context: Any, **kwargs: Any
            ) -> None:
                child2_called.append("called")

        @command()
        @option("--opt", tags=["shared"])
        @tag(name="shared")
        @Child1.as_decorator(name="child1")
        @Child2.as_decorator(name="child2")
        def cmd(opt: str) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt=value"])
        assert result.exit_code == 0
        assert "called" in child1_called
        assert "called" in child2_called


class TestTagEdgeCases:
    """Test Tag edge cases and error conditions."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        Tree._pending_nodes.clear()  # type: ignore[attr-defined]

    def test_tag_with_empty_parent_nodes(self) -> None:
        """Test tag with no parent nodes."""
        tag_node = Tag(name="empty_tag")

        assert tag_node.parent_nodes == []
        assert tag_node.get_value() == {}
        assert tag_node.get_provided_values() == []

    def test_tag_name_with_special_characters(self) -> None:
        """Test tag names with special characters."""
        tag1 = Tag(name="tag-with-dashes")
        tag2 = Tag(name="tag_with_underscores")
        tag3 = Tag(name="tag.with.dots")

        assert tag1.name == "tag-with-dashes"
        assert tag2.name == "tag_with_underscores"
        assert tag3.name == "tag.with.dots"

    def test_tag_with_same_parent_multiple_times(self) -> None:
        """Test adding same parent to tag multiple times."""
        tag_node = Tag(name="test_tag")
        parent = ConcreteParentNode(name="parent1")

        tag_node.parent_nodes.append(parent)
        tag_node.parent_nodes.append(parent)

        # Should have duplicate references
        assert len(tag_node.parent_nodes) == 2
        assert tag_node.parent_nodes[0] is parent
        assert tag_node.parent_nodes[1] is parent

    def test_tag_get_value_with_none_values(self) -> None:
        """Test tag.get_value() includes all parents even when values are None."""
        tag_node = Tag(name="test_tag")
        parent1 = ConcreteParentNode(name="opt1")
        parent2 = ConcreteParentNode(name="opt2")

        tag_node.parent_nodes.extend([parent1, parent2])

        value = tag_node.get_value()

        # Both should be in the dict even though their values are None
        assert "opt1" in value
        assert "opt2" in value
        assert value["opt1"] is None
        assert value["opt2"] is None

    def test_tag_decorator_preserves_attributes(self) -> None:
        """Test tag decorator preserves function attributes."""

        @Tag.as_decorator(name="test_tag")
        def my_func() -> str:
            """My docstring."""
            return "result"

        my_func.custom_attr = "custom_value"  # type: ignore[attr-defined]

        assert my_func.__name__ == "my_func"
        assert "My docstring" in my_func.__doc__  # type: ignore[operator]
        assert my_func.custom_attr == "custom_value"  # type: ignore[attr-defined]
        assert my_func() == "result"

    def test_tag_with_mixed_parent_types(self, cli_runner: Any) -> None:
        """Test tag works with options, arguments, and env mixed."""
        import click

        from click_extended.core.decorators.argument import argument
        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.env import env
        from click_extended.core.decorators.option import option

        @command()
        @option("--opt", tags=["mixed"])
        @argument("arg", tags=["mixed"])
        @env("HOME", tags=["mixed"])
        @tag(name="mixed")
        def cmd(opt: str, arg: str, home: str) -> None:
            click.echo(f"{opt}-{arg}-{len(home)}")

        result = cli_runner.invoke(cmd, ["--opt=optval", "argval"])
        assert result.exit_code == 0
