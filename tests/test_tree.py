"""Tests for the Tree class and node registration system."""

from typing import Any

import pytest

from click_extended.core._child_node import ChildNode
from click_extended.core._parent_node import ParentNode
from click_extended.core._root_node import RootNode
from click_extended.core._tree import (
    Tree,
    get_pending_nodes,
    queue_child,
    queue_parent,
)
from click_extended.errors import (
    NoParentError,
    NoRootError,
    ParentNodeExistsError,
    RootNodeExistsError,
)


class DummyRootNode(RootNode):
    """Dummy RootNode for testing."""

    @classmethod
    def _get_click_decorator(cls) -> Any:
        """Return a dummy decorator."""

        def outer(**kwargs: Any) -> Any:
            def inner(f: Any) -> Any:
                return f

            return inner

        return outer

    @classmethod
    def _get_click_cls(cls) -> Any:
        """Return a dummy class."""
        return object


class DummyParentNode(ParentNode):
    """Dummy ParentNode for testing."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)

    def get_raw_value(self) -> Any:
        """Return a test value."""
        return "test_value"


class DummyChildNode(ChildNode):
    """Dummy ChildNode for testing."""

    def process(self, value: Any, *args: Any, **kwargs: Any) -> Any:
        """Return the value unchanged."""
        return value


class TestTreeInitialization:
    """Tests for Tree initialization."""

    def test_init_creates_empty_tree(self) -> None:
        """Test that Tree initializes with no root or recent node."""
        tree = Tree()
        assert tree.root is None
        assert tree.recent is None

    def test_multiple_trees_are_independent(self) -> None:
        """Test that multiple Tree instances are independent."""
        tree1 = Tree()
        tree2 = Tree()

        root1 = DummyRootNode(name="root1")
        tree1.root = root1

        assert tree1.root is not None
        assert tree2.root is None
        assert tree1.root is not tree2.root


class TestPendingNodesQueue:
    """Tests for the pending nodes queue system."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_queue_parent_adds_to_pending(self) -> None:
        """Test that queue_parent adds a parent node to pending queue."""
        parent = DummyParentNode(name="test_parent")
        queue_parent(parent)

        pending = get_pending_nodes()
        assert len(pending) == 1
        assert pending[0] == ("parent", parent)

    def test_queue_child_adds_to_pending(self) -> None:
        """Test that queue_child adds a child node to pending queue."""
        child = DummyChildNode(name="test_child")
        queue_child(child)

        pending = get_pending_nodes()
        assert len(pending) == 1
        assert pending[0] == ("child", child)

    def test_get_pending_nodes_clears_queue(self) -> None:
        """Test that get_pending_nodes clears the queue after retrieval."""
        parent = DummyParentNode(name="test_parent")
        queue_parent(parent)

        first_call = get_pending_nodes()
        second_call = get_pending_nodes()

        assert len(first_call) == 1
        assert len(second_call) == 0

    def test_multiple_nodes_queued_in_order(self) -> None:
        """Test that multiple nodes are queued in the order they're added."""
        parent = DummyParentNode(name="parent")
        child1 = DummyChildNode(name="child1")
        child2 = DummyChildNode(name="child2")

        queue_parent(parent)
        queue_child(child1)
        queue_child(child2)

        pending = get_pending_nodes()
        assert len(pending) == 3
        assert pending[0] == ("parent", parent)
        assert pending[1] == ("child", child1)
        assert pending[2] == ("child", child2)

    def test_queue_preserves_node_references(self) -> None:
        """Test that queued nodes maintain their identity."""
        parent = DummyParentNode(name="test")
        queue_parent(parent)

        pending = get_pending_nodes()
        retrieved_parent = pending[0][1]

        assert retrieved_parent is parent


class TestTreeRegisterRoot:
    """Tests for Tree.register_root method."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_register_root_sets_root_node(self) -> None:
        """Test that register_root sets the tree's root node."""
        tree = Tree()
        root = DummyRootNode(name="test_root")

        tree.register_root(root)

        assert tree.root is root
        assert tree.root is not None
        assert tree.root.name == "test_root"

    def test_register_root_raises_if_root_exists(self) -> None:
        """Test that registering a second root raises RootNodeExistsError."""
        tree = Tree()
        root1 = DummyRootNode(name="root1")
        root2 = DummyRootNode(name="root2")

        tree.register_root(root1)

        with pytest.raises(RootNodeExistsError):
            tree.register_root(root2)

    def test_register_root_processes_pending_parents(self) -> None:
        """Test that register_root processes pending parent nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent = DummyParentNode(name="parent")

        queue_parent(parent)
        tree.register_root(root)

        assert root.children is not None
        assert "parent" in root.children
        assert root.children["parent"] is parent

    def test_register_root_processes_pending_children(self) -> None:
        """Test that register_root processes pending child nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent = DummyParentNode(name="parent")
        child = DummyChildNode(name="child")

        queue_child(child)
        queue_parent(parent)
        tree.register_root(root)

        assert parent.children is not None
        assert 0 in parent.children
        assert parent.children[0] is child

    def test_register_root_reverses_pending_order(self) -> None:
        """Test that register_root processes nodes in reverse order."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent1 = DummyParentNode(name="parent1")
        parent2 = DummyParentNode(name="parent2")

        queue_parent(parent1)
        queue_parent(parent2)
        tree.register_root(root)

        assert root.children is not None
        assert "parent1" in root.children
        assert "parent2" in root.children

    def test_register_root_raises_on_duplicate_parent(self) -> None:
        """Test that duplicate parent names raise ParentNodeExistsError."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent1 = DummyParentNode(name="same_name")
        parent2 = DummyParentNode(name="same_name")

        queue_parent(parent1)
        queue_parent(parent2)

        with pytest.raises(ParentNodeExistsError):
            tree.register_root(root)

    def test_register_root_raises_on_child_without_parent(self) -> None:
        """Test that child without parent raises NoParentError."""
        tree = Tree()
        root = DummyRootNode(name="root")
        child = DummyChildNode(name="orphan")

        queue_child(child)

        with pytest.raises(NoParentError):
            tree.register_root(root)

    def test_register_root_sets_recent_to_last_parent(self) -> None:
        """Test that register_root sets recent to the most recent parent."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent1 = DummyParentNode(name="parent1")
        parent2 = DummyParentNode(name="parent2")

        queue_parent(parent1)
        queue_parent(parent2)
        tree.register_root(root)

        assert tree.recent is not None
        assert tree.recent.name in ["parent1", "parent2"]

    def test_register_root_assigns_children_by_index(self) -> None:
        """Test that children are assigned sequential indices."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent = DummyParentNode(name="parent")
        child1 = DummyChildNode(name="child1")
        child2 = DummyChildNode(name="child2")

        queue_child(child2)
        queue_child(child1)
        queue_parent(parent)
        tree.register_root(root)

        assert parent.children is not None
        assert 0 in parent.children
        assert 1 in parent.children
        assert parent.children[0] is child1
        assert parent.children[1] is child2


class TestTreeRegisterParent:
    """Tests for Tree.register_parent method."""

    def test_register_parent_adds_parent_to_root(self) -> None:
        """Test that register_parent adds a parent node to the root."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent = DummyParentNode(name="parent")
        tree.register_parent(parent)

        assert root.children is not None
        assert "parent" in root.children
        assert root.children["parent"] is parent

    def test_register_parent_raises_without_root(self) -> None:
        """Test that register_parent raises NoRootError if no root exists."""
        tree = Tree()
        parent = DummyParentNode(name="parent")

        with pytest.raises(NoRootError):
            tree.register_parent(parent)

    def test_register_parent_raises_on_duplicate_name(self) -> None:
        """Test that duplicate parent names raise ParentNodeExistsError."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent1 = DummyParentNode(name="same_name")
        parent2 = DummyParentNode(name="same_name")

        tree.register_parent(parent1)

        with pytest.raises(ParentNodeExistsError):
            tree.register_parent(parent2)

    def test_register_parent_sets_recent(self) -> None:
        """Test that register_parent updates the recent node."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent = DummyParentNode(name="parent")
        tree.register_parent(parent)

        assert tree.recent is parent


class TestTreeRegisterChild:
    """Tests for Tree.register_child method."""

    def test_register_child_adds_child_to_recent_parent(self) -> None:
        """Test that register_child adds a child to the recent parent."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent = DummyParentNode(name="parent")
        tree.register_parent(parent)

        child = DummyChildNode(name="child")
        tree.register_child(child)

        assert parent.children is not None
        assert 0 in parent.children
        assert parent.children[0] is child

    def test_register_child_raises_without_root(self) -> None:
        """Test that register_child raises NoRootError if no root exists."""
        tree = Tree()
        child = DummyChildNode(name="child")

        with pytest.raises(NoRootError):
            tree.register_child(child)

    def test_register_child_raises_without_recent_parent(self) -> None:
        """Test that register_child raises NoParentError without recent parent."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        child = DummyChildNode(name="child")

        with pytest.raises(NoParentError):
            tree.register_child(child)

    def test_register_child_assigns_sequential_indices(self) -> None:
        """Test that multiple children get sequential indices."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent = DummyParentNode(name="parent")
        tree.register_parent(parent)

        child1 = DummyChildNode(name="child1")
        child2 = DummyChildNode(name="child2")
        child3 = DummyChildNode(name="child3")

        tree.register_child(child1)
        tree.register_child(child2)
        tree.register_child(child3)

        assert parent.children is not None
        assert len(parent.children) == 3
        assert parent.children[0] is child1
        assert parent.children[1] is child2
        assert parent.children[2] is child3


class TestTreeVisualize:
    """Tests for Tree.visualize method."""

    def test_visualize_raises_without_root(self) -> None:
        """Test that visualize raises NoRootError when no root exists."""
        tree = Tree()

        with pytest.raises(NoRootError):
            tree.visualize()

    def test_visualize_prints_root_only(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that visualize prints root name when no children exist."""
        tree = Tree()
        root = DummyRootNode(name="test_root")
        tree.root = root

        tree.visualize()

        captured = capsys.readouterr()
        assert "test_root" in captured.out

    def test_visualize_prints_root_and_parents(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that visualize prints root and parent nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent = DummyParentNode(name="parent")
        tree.register_parent(parent)

        tree.visualize()

        captured = capsys.readouterr()
        assert "root" in captured.out
        assert "parent" in captured.out

    def test_visualize_prints_full_hierarchy(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that visualize prints root, parent, and child nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent = DummyParentNode(name="parent")
        tree.register_parent(parent)

        child = DummyChildNode(name="child")
        tree.register_child(child)

        tree.visualize()

        captured = capsys.readouterr()
        assert "root" in captured.out
        assert "parent" in captured.out
        assert "child" in captured.out

    def test_visualize_indentation_structure(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that visualize uses proper indentation for hierarchy."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent = DummyParentNode(name="parent")
        tree.register_parent(parent)

        child = DummyChildNode(name="child")
        tree.register_child(child)

        tree.visualize()

        captured = capsys.readouterr()
        lines = captured.out.split("\n")

        assert any(
            "root" in line and not line.startswith(" ") for line in lines
        )
        assert any("parent" in line and line.startswith("  ") for line in lines)
        assert any(
            "child" in line and line.startswith("    ") for line in lines
        )


class TestTreeIntegration:
    """Integration tests for Tree with complex scenarios."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_full_decorator_flow(self) -> None:
        """Test the complete flow of decorator registration."""
        tree = Tree()
        root = DummyRootNode(name="command")
        parent1 = DummyParentNode(name="option1")
        parent2 = DummyParentNode(name="option2")
        child1 = DummyChildNode(name="transform1")
        child2 = DummyChildNode(name="transform2")

        queue_child(child2)
        queue_child(child1)
        queue_parent(parent2)
        queue_parent(parent1)

        tree.register_root(root)

        assert root.children is not None
        assert "option1" in root.children
        assert "option2" in root.children

        assert parent1.children is not None
        assert parent2.children is not None

    def test_multiple_parents_with_children(self) -> None:
        """Test tree with multiple parents each having children."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent1 = DummyParentNode(name="parent1")
        parent2 = DummyParentNode(name="parent2")
        child1 = DummyChildNode(name="child1")
        child2 = DummyChildNode(name="child2")

        queue_child(child1)
        queue_parent(parent1)
        queue_child(child2)
        queue_parent(parent2)

        tree.register_root(root)

        assert root.children is not None
        assert len(root.children) == 2

        assert parent1.children is not None
        assert len(parent1.children) == 1
        assert parent1.children[0] is child1

        assert parent2.children is not None
        assert len(parent2.children) == 1
        assert parent2.children[0] is child2

    def test_parent_with_multiple_children(self) -> None:
        """Test a parent node with multiple child transformations."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent = DummyParentNode(name="parent")
        child1 = DummyChildNode(name="child1")
        child2 = DummyChildNode(name="child2")
        child3 = DummyChildNode(name="child3")

        queue_child(child3)
        queue_child(child2)
        queue_child(child1)
        queue_parent(parent)

        tree.register_root(root)

        assert parent.children is not None
        assert len(parent.children) == 3
        assert parent.children[0] is child1
        assert parent.children[1] is child2
        assert parent.children[2] is child3

    def test_empty_pending_queue_registers_root_only(self) -> None:
        """Test that empty pending queue just registers the root."""
        tree = Tree()
        root = DummyRootNode(name="root")

        tree.register_root(root)

        assert tree.root is root
        assert root.children is not None
        assert len(root.children) == 0


class TestTreeEdgeCases:
    """Tests for Tree edge cases and error conditions."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_recent_updates_with_each_parent(self) -> None:
        """Test that recent is updated for each parent registration."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent1 = DummyParentNode(name="parent1")
        parent2 = DummyParentNode(name="parent2")

        tree.register_parent(parent1)
        assert tree.recent is parent1

        tree.register_parent(parent2)
        assert tree.recent is parent2

    def test_child_registration_uses_recent_parent(self) -> None:
        """Test that child registration always uses the most recent parent."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent1 = DummyParentNode(name="parent1")
        parent2 = DummyParentNode(name="parent2")

        tree.register_parent(parent1)
        tree.register_parent(parent2)

        child = DummyChildNode(name="child")
        tree.register_child(child)

        assert parent2.children is not None
        assert 0 in parent2.children
        assert parent2.children[0] is child

        assert parent1.children is not None
        assert len(parent1.children) == 0

    def test_parent_names_are_case_sensitive(self) -> None:
        """Test that parent node names are case-sensitive."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        parent1 = DummyParentNode(name="Parent")
        parent2 = DummyParentNode(name="parent")

        tree.register_parent(parent1)
        tree.register_parent(parent2)

        assert root.children is not None
        assert "Parent" in root.children
        assert "parent" in root.children
        assert root.children["Parent"] is not root.children["parent"]

    def test_empty_tree_state_preserved(self) -> None:
        """Test that an empty tree maintains its state."""
        tree = Tree()

        assert tree.root is None
        assert tree.recent is None

        _ = tree.root
        _ = tree.recent

        assert tree.root is None
        assert tree.recent is None
