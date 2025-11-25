"""Tests for the base Node class."""

from click_extended.core.node import Node


class ConcreteNode(Node):
    """Concrete implementation of Node for testing."""


class TestNode:
    """Test the base Node class."""

    def test_node_initialization_with_name(self) -> None:
        """Test Node initialization with just a name."""
        node = ConcreteNode(name="test_node")

        assert node.name == "test_node"
        assert node.children == {}
        assert len(node) == 0

    def test_node_initialization_with_children(self) -> None:
        """Test Node initialization with children."""
        child1 = ConcreteNode(name="child1")
        child2 = ConcreteNode(name="child2")
        children: dict[str | int, Node] = {"a": child1, "b": child2}

        node = ConcreteNode(name="parent", children=children)

        assert node.name == "parent"
        assert len(node.children) == 2
        assert node["a"] == child1
        assert node["b"] == child2

    def test_node_children_getter(self) -> None:
        """Test getting children property."""
        child = ConcreteNode(name="child")
        node = ConcreteNode(name="parent", children={"key": child})

        assert node.children == {"key": child}

    def test_node_children_setter_with_dict(self) -> None:
        """Test setting children with a dictionary."""
        node = ConcreteNode(name="parent")
        child = ConcreteNode(name="child")

        node.children = {"key": child}

        assert len(node) == 1
        assert node["key"] == child

    def test_node_children_setter_with_none(self) -> None:
        """Test setting children to None creates empty dict."""
        child = ConcreteNode(name="child")
        node = ConcreteNode(name="parent", children={"key": child})

        # Should have one child initially
        assert len(node) == 1

        # Setting to None should clear children
        node.children = None  # type: ignore[assignment]

        assert node.children == {}
        assert len(node) == 0

    def test_node_getitem(self) -> None:
        """Test accessing children via __getitem__."""
        child = ConcreteNode(name="child")
        node = ConcreteNode(name="parent", children={"key": child})

        assert node["key"] == child

    def test_node_setitem(self) -> None:
        """Test setting children via __setitem__."""
        node = ConcreteNode(name="parent")
        child = ConcreteNode(name="child")

        node["key"] = child

        assert node["key"] == child
        assert len(node) == 1

    def test_node_len(self) -> None:
        """Test __len__ returns number of children."""
        node = ConcreteNode(name="parent")

        assert len(node) == 0

        node["a"] = ConcreteNode(name="child1")
        assert len(node) == 1

        node["b"] = ConcreteNode(name="child2")
        assert len(node) == 2

    def test_node_repr(self) -> None:
        """Test __repr__ returns proper representation."""
        node = ConcreteNode(name="test_node")

        repr_str = repr(node)

        assert repr_str == "<ConcreteNode name='test_node'>"
        assert "ConcreteNode" in repr_str
        assert "test_node" in repr_str

    def test_node_str(self) -> None:
        """Test __str__ delegates to __repr__."""
        node = ConcreteNode(name="test_node")

        str_repr = str(node)
        repr_str = repr(node)

        assert str_repr == repr_str
        assert str_repr == "<ConcreteNode name='test_node'>"
