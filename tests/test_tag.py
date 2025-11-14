"""Tests for the Tag class and tag decorator."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from click_extended.core._child_node import ChildNode
from click_extended.core._node import Node
from click_extended.core._parent_node import ParentNode
from click_extended.core.tag import Tag, tag


class DummyParentNode(ParentNode):
    """Dummy ParentNode for testing."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)

    def get_raw_value(self) -> Any:
        """Return a test value."""
        return "test_value"


class ValidationChild(ChildNode):
    """ChildNode that validates but doesn't transform."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: dict[str, Tag],
        **kwargs: Any,
    ) -> Any:
        """Validate and return the same value."""
        return value


class TransformChild(ChildNode):
    """ChildNode that transforms values."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: dict[str, Tag],
        **kwargs: Any,
    ) -> Any:
        """Transform value to uppercase."""
        if value is None:
            return value
        return str(value).upper()


class RequiresOneChild(ChildNode):
    """ChildNode that validates at least one tagged param is provided."""

    def process(
        self,
        value: Any,
        *args: Any,
        siblings: list[str],
        tags: dict[str, Tag],
        **kwargs: Any,
    ) -> Any:
        """Validate that at least one parameter was provided."""
        for tag_name, tag in tags.items():
            provided = [p for p in tag.parent_nodes if p.was_provided()]
            if len(provided) == 0:
                raise ValueError(
                    f"At least one parameter in tag '{tag_name}' required"
                )
        return value


class TestTagInitialization:
    """Test Tag class initialization."""

    def test_init_with_name(self) -> None:
        """Test initializing Tag with name."""
        tag_inst = Tag(name="api-config")
        assert tag_inst.name == "api-config"
        assert tag_inst.children == {}
        assert isinstance(tag_inst.children, dict)

    def test_init_creates_empty_children_dict(self) -> None:
        """Test that children dict is initialized empty."""
        tag_inst = Tag(name="test-tag")
        assert tag_inst.children is not None
        assert len(tag_inst.children) == 0

    def test_init_with_different_names(self) -> None:
        """Test initializing with various name formats."""
        tag1 = Tag(name="api-config")
        tag2 = Tag(name="dev-mode")
        tag3 = Tag(name="validation")

        assert tag1.name == "api-config"
        assert tag2.name == "dev-mode"
        assert tag3.name == "validation"

    def test_init_with_hyphenated_name(self) -> None:
        """Test tag with hyphenated name."""
        tag_inst = Tag(name="api-config-settings")
        assert tag_inst.name == "api-config-settings"

    def test_init_with_underscore_name(self) -> None:
        """Test tag with underscore name."""
        tag_inst = Tag(name="user_settings")
        assert tag_inst.name == "user_settings"


class TestTagInheritance:
    """Test Tag class inheritance."""

    def test_tag_is_node_subclass(self) -> None:
        """Test that Tag is a Node subclass."""
        assert issubclass(Tag, Node)

    def test_tag_is_not_parent_node_subclass(self) -> None:
        """Test that Tag is NOT a ParentNode subclass."""
        assert not issubclass(Tag, ParentNode)

    def test_tag_instance_is_node_instance(self) -> None:
        """Test that Tag instance is a Node instance."""
        tag_inst = Tag(name="test")
        assert isinstance(tag_inst, Node)
        assert isinstance(tag_inst, Tag)

    def test_tag_has_node_attributes(self) -> None:
        """Test that Tag has Node attributes."""
        tag_inst = Tag(name="test")
        assert hasattr(tag_inst, "name")
        assert hasattr(tag_inst, "children")

    def test_tag_has_children_dict(self) -> None:
        """Test that Tag has children dict."""
        tag_inst = Tag(name="test")
        assert hasattr(tag_inst, "children")
        assert isinstance(tag_inst.children, dict)


class TestTagAsDecorator:
    """Test Tag.as_decorator() classmethod."""

    @patch("click_extended.core.tag.queue_tag")
    def test_as_decorator_returns_decorator(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator returns a decorator function."""
        decorator = Tag.as_decorator(name="api-config")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)

    @patch("click_extended.core.tag.queue_tag")
    def test_as_decorator_creates_tag_instance(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator creates Tag instance."""
        decorator = Tag.as_decorator(name="api-config")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        assert isinstance(args[0], Tag)
        assert args[0].name == "api-config"

    @patch("click_extended.core.tag.queue_tag")
    def test_as_decorator_queues_tag(self, mock_queue: MagicMock) -> None:
        """Test as_decorator queues tag node."""
        decorator = Tag.as_decorator(name="test-tag")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core.tag.queue_tag")
    def test_as_decorator_preserves_function(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator preserves function behavior."""
        decorator = Tag.as_decorator(name="test-tag")

        def test_func(a: int, b: int) -> int:
            return a + b

        result = decorator(test_func)
        assert callable(result)
        assert result(2, 3) == 5

    @patch("click_extended.core.tag.queue_tag")
    def test_as_decorator_with_kwargs(self, mock_queue: MagicMock) -> None:
        """Test as_decorator with keyword arguments."""
        decorator = Tag.as_decorator(name="test-tag")

        def test_func(name: str = "default") -> str:
            return name

        result = decorator(test_func)
        assert result() == "default"
        assert result(name="custom") == "custom"

    @patch("click_extended.core.tag.queue_tag")
    def test_as_decorator_preserves_function_name(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator preserves function name."""
        decorator = Tag.as_decorator(name="test-tag")

        def my_function() -> str:
            return "test"

        result = decorator(my_function)
        assert result.__name__ == "my_function"


class TestTagDecoratorFunction:
    """Test the tag() decorator function."""

    @patch("click_extended.core.tag.queue_tag")
    def test_tag_decorator_with_name(self, mock_queue: MagicMock) -> None:
        """Test tag decorator with name."""

        @tag("api-config")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core.tag.queue_tag")
    def test_tag_decorator_creates_tag_instance(
        self, mock_queue: MagicMock
    ) -> None:
        """Test tag decorator creates Tag instance."""

        @tag("dev-mode")
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        assert isinstance(args[0], Tag)
        assert args[0].name == "dev-mode"

    @patch("click_extended.core.tag.queue_tag")
    def test_tag_decorator_returns_callable(
        self, mock_queue: MagicMock
    ) -> None:
        """Test tag decorator returns callable."""

        @tag("test-tag")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        assert test_func() == "test"

    @patch("click_extended.core.tag.queue_tag")
    def test_tag_decorator_preserves_function_behavior(
        self, mock_queue: MagicMock
    ) -> None:
        """Test tag decorator preserves original function behavior."""

        @tag("test-tag")
        def add(a: int, b: int) -> int:
            return a + b

        assert add(5, 3) == 8
        assert add(10, 20) == 30

    @patch("click_extended.core.tag.queue_tag")
    def test_multiple_tag_decorators(self, mock_queue: MagicMock) -> None:
        """Test multiple tag decorators on same function."""

        @tag("tag1")
        @tag("tag2")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        assert mock_queue.call_count == 2

    @patch("click_extended.core.tag.queue_tag")
    def test_tag_decorator_with_various_names(
        self, mock_queue: MagicMock
    ) -> None:
        """Test tag decorator with various name formats."""

        @tag("api-config")
        def func1() -> None:  # type: ignore
            pass

        @tag("dev_mode")
        def func2() -> None:  # type: ignore
            pass

        @tag("settings123")
        def func3() -> None:  # type: ignore
            pass

        assert mock_queue.call_count == 3


class TestTagChildren:
    """Test Tag with child nodes."""

    def test_tag_can_store_children(self) -> None:
        """Test that tags can store child nodes."""
        tag_inst = Tag(name="test-tag")
        child = ValidationChild(name="validator")

        assert tag_inst.children is not None
        tag_inst[0] = child
        assert len(tag_inst.children) == 1
        assert tag_inst.children[0] is child

    def test_tag_can_store_multiple_children(self) -> None:
        """Test that tags can store multiple children."""
        tag_inst = Tag(name="test-tag")
        child1 = ValidationChild(name="validator1")
        child2 = ValidationChild(name="validator2")

        assert tag_inst.children is not None
        tag_inst[0] = child1
        tag_inst[1] = child2

        assert len(tag_inst.children) == 2
        assert tag_inst.children[0] is child1
        assert tag_inst.children[1] is child2

    def test_tag_length_with_children(self) -> None:
        """Test tag length reflects number of children."""
        tag_inst = Tag(name="test-tag")
        assert len(tag_inst) == 0

        assert tag_inst.children is not None
        tag_inst[0] = ValidationChild(name="child1")
        assert len(tag_inst) == 1

        tag_inst[1] = ValidationChild(name="child2")
        assert len(tag_inst) == 2


class TestTagValidationOnly:
    """Test that tags only accept validation-only children."""

    def test_validation_child_returns_same_value(self) -> None:
        """Test that validation child returns the same value."""
        child = ValidationChild(name="validator")
        sentinel = object()

        result = child.process(
            sentinel,
            siblings=[],
            tags={},
        )

        assert result is sentinel

    def test_transform_child_returns_different_value(self) -> None:
        """Test that transform child returns different value."""
        child = TransformChild(name="transformer")
        original = "hello"

        result = child.process(
            original,
            siblings=[],
            tags={},
        )

        assert result != original
        assert result == "HELLO"

    def test_transform_child_fails_identity_check(self) -> None:
        """Test that transform child fails identity check."""
        child = TransformChild(name="transformer")
        sentinel = object()

        result = child.process(
            sentinel,
            siblings=[],
            tags={},
        )

        assert result is not sentinel


class TestTagWithParentNodes:
    """Test Tag interactions with ParentNodes."""

    def test_parent_nodes_can_have_tags_parameter(self) -> None:
        """Test that ParentNodes accept tags parameter."""
        parent = DummyParentNode(name="test", tags="api-config")
        assert parent.tags == ["api-config"]

    def test_parent_nodes_tags_can_be_list(self) -> None:
        """Test that ParentNodes can have multiple tags."""
        parent = DummyParentNode(name="test", tags=["tag1", "tag2"])
        assert parent.tags == ["tag1", "tag2"]

    def test_parent_nodes_with_single_string_tag(self) -> None:
        """Test ParentNode with single string tag."""
        parent = DummyParentNode(name="test", tags="single-tag")
        assert isinstance(parent.tags, list)
        assert len(parent.tags) == 1
        assert parent.tags[0] == "single-tag"

    def test_parent_nodes_with_no_tags(self) -> None:
        """Test ParentNode with no tags."""
        parent = DummyParentNode(name="test")
        assert parent.tags == []


class TestTagEdgeCases:
    """Test edge cases and special scenarios."""

    def test_tag_with_empty_string_name(self) -> None:
        """Test tag with empty string name."""
        tag_inst = Tag(name="")
        assert tag_inst.name == ""

    def test_tag_with_special_characters_name(self) -> None:
        """Test tag with special characters in name."""
        tag_inst = Tag(name="api-config-v2")
        assert tag_inst.name == "api-config-v2"

    @patch("click_extended.core.tag.queue_tag")
    def test_decorator_can_be_reused(self, mock_queue: MagicMock) -> None:
        """Test that tag decorator can be reused."""
        decorator = tag("test-tag")

        def func1() -> str:
            return "test1"

        def func2() -> str:
            return "test2"

        result1 = decorator(func1)
        result2 = decorator(func2)

        assert callable(result1)
        assert callable(result2)
        assert mock_queue.call_count == 2

    def test_tag_children_initially_empty(self) -> None:
        """Test that Tag children dict is initially empty."""
        tag_inst = Tag(name="test-tag")
        assert tag_inst.children == {}
        assert tag_inst.children is not None
        assert len(tag_inst.children) == 0

    @patch("click_extended.core.tag.queue_tag")
    def test_tag_with_async_function(self, mock_queue: MagicMock) -> None:
        """Test tag decorator with async function."""

        @tag("test-tag")
        async def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()


class TestTagIntegration:
    """Test Tag integration scenarios."""

    @patch("click_extended.core.tag.queue_tag")
    def test_tag_in_decorator_chain(self, mock_queue: MagicMock) -> None:
        """Test tag as part of decorator chain."""

        @tag("config")
        def my_command() -> str:
            return "result"

        assert callable(my_command)
        assert my_command() == "result"
        mock_queue.assert_called_once()

    def test_requires_one_child_with_tags_dict(self) -> None:
        """Test RequiresOneChild with tags dictionary."""
        child = RequiresOneChild(name="requires_one")

        parent1: ParentNode = DummyParentNode(name="key")
        parent1.set_raw_value("value", True)

        parent2: ParentNode = DummyParentNode(name="url")
        parent2.set_raw_value(None, False)

        api_config_tag = Tag(name="api-config")
        api_config_tag.parent_nodes = [parent1, parent2]
        tags_dict: dict[str, Tag] = {"api-config": api_config_tag}

        result = child.process(
            None,
            siblings=[],
            tags=tags_dict,
        )
        assert result is None

    def test_requires_one_child_fails_when_none_provided(self) -> None:
        """Test RequiresOneChild fails when no params provided."""
        child = RequiresOneChild(name="requires_one")

        parent1: ParentNode = DummyParentNode(name="key")
        parent1.set_raw_value(None, False)

        parent2: ParentNode = DummyParentNode(name="url")
        parent2.set_raw_value(None, False)

        api_config_tag = Tag(name="api-config")
        api_config_tag.parent_nodes = [parent1, parent2]
        tags_dict: dict[str, Tag] = {"api-config": api_config_tag}

        with pytest.raises(ValueError) as exc_info:
            child.process(
                None,
                siblings=[],
                tags=tags_dict,
            )
        assert "At least one parameter" in str(exc_info.value)

    def test_validation_child_with_empty_tags_dict(self) -> None:
        """Test validation child with empty tags dict."""
        child = ValidationChild(name="validator")

        result = child.process(
            "test_value",
            siblings=[],
            tags={},
        )

        assert result == "test_value"

    def test_validation_child_with_none_value(self) -> None:
        """Test validation child with None value."""
        child = ValidationChild(name="validator")

        result = child.process(
            None,
            siblings=[],
            tags={},
        )

        assert result is None


class TestTagDocumentation:
    """Test that tag decorator has proper documentation."""

    def test_tag_function_has_docstring(self) -> None:
        """Test that tag function has docstring."""
        assert tag.__doc__ is not None
        assert len(tag.__doc__) > 0

    def test_tag_class_has_docstring(self) -> None:
        """Test that Tag class has docstring."""
        assert Tag.__doc__ is not None
        assert len(Tag.__doc__) > 0

    def test_tag_as_decorator_has_docstring(self) -> None:
        """Test that Tag.as_decorator has docstring."""
        assert Tag.as_decorator.__doc__ is not None
        assert len(Tag.as_decorator.__doc__) > 0


class TestTagNaming:
    """Test tag naming conventions."""

    def test_tag_accepts_kebab_case(self) -> None:
        """Test tag accepts kebab-case names."""
        tag_inst = Tag(name="api-config")
        assert tag_inst.name == "api-config"

    def test_tag_accepts_snake_case(self) -> None:
        """Test tag accepts snake_case names."""
        tag_inst = Tag(name="api_config")
        assert tag_inst.name == "api_config"

    def test_tag_accepts_alphanumeric(self) -> None:
        """Test tag accepts alphanumeric names."""
        tag_inst = Tag(name="config123")
        assert tag_inst.name == "config123"

    def test_tag_accepts_single_word(self) -> None:
        """Test tag accepts single word names."""
        tag_inst = Tag(name="config")
        assert tag_inst.name == "config"
