"""Tests for the GlobalNode class and global node registration."""

from typing import Any

import pytest

from click_extended.core._global_node import GlobalNode
from click_extended.core._parent_node import ParentNode
from click_extended.core._root_node import RootNode
from click_extended.core._tree import Tree, get_pending_nodes, queue_global
from click_extended.core.tag import Tag


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


class ConcreteGlobalNode(GlobalNode):
    """Concrete GlobalNode implementation for testing."""

    def __init__(
        self, name: str | None = None, delay: bool = False, **kwargs: Any
    ) -> None:
        """Initialize with optional return value."""
        super().__init__(name=name, delay=delay)
        self.return_value = kwargs.get("return_value", None)
        self.call_count = 0
        self.last_call_args: dict[str, Any] = {}

    def process(
        self,
        tree: Tree,
        root: RootNode,
        parents: list[ParentNode],
        tags: dict[str, Tag],
        globals: list[GlobalNode],
        call_args: tuple[Any, ...],
        call_kwargs: dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Record the call and return configured value."""
        self.call_count += 1
        self.last_call_args = {
            "tree": tree,
            "root": root,
            "parents": parents,
            "tags": tags,
            "globals": globals,
            "call_args": call_args,
            "call_kwargs": call_kwargs,
            "args": args,
            "kwargs": kwargs,
        }
        return self.return_value


class TestGlobalNodeInitialization:
    """Tests for GlobalNode initialization."""

    def test_init_with_name(self) -> None:
        """Test GlobalNode initialization with injection name."""
        node = ConcreteGlobalNode(name="test_var")

        assert node.inject_name == "test_var"
        assert node.delay is False
        assert node.call_count == 0

    def test_init_without_name(self) -> None:
        """Test GlobalNode initialization in observer mode."""
        node = ConcreteGlobalNode()

        assert node.inject_name is None
        assert node.delay is False

    def test_init_with_delay(self) -> None:
        """Test GlobalNode initialization with delay parameter."""
        node = ConcreteGlobalNode(delay=True)

        assert node.inject_name is None
        assert node.delay is True

    def test_init_with_name_and_delay(self) -> None:
        """Test GlobalNode initialization with both name and delay."""
        node = ConcreteGlobalNode(name="var", delay=True)

        assert node.inject_name == "var"
        assert node.delay is True

    def test_init_creates_unique_internal_name(self) -> None:
        """Test that GlobalNode creates unique internal names."""
        node1 = ConcreteGlobalNode()
        node2 = ConcreteGlobalNode()

        assert node1.name != node2.name
        assert "_global_" in node1.name
        assert "_global_" in node2.name

    def test_init_uses_inject_name_as_internal_name(self) -> None:
        """Test that inject_name is used as internal name when provided."""
        node = ConcreteGlobalNode(name="test_var")

        assert node.name == "test_var"
        assert node.inject_name == "test_var"

    def test_init_stores_process_kwargs(self) -> None:
        """Test that initialization stores process_kwargs."""
        node = ConcreteGlobalNode(return_value="test")

        assert node.process_kwargs == {}
        assert node.return_value == "test"


class TestGlobalNodeProcess:
    """Tests for GlobalNode.process method."""

    def test_process_is_abstract(self) -> None:
        """Test that GlobalNode.process is abstract."""

        with pytest.raises(TypeError):
            GlobalNode()  # type: ignore

    def test_process_receives_tree(self) -> None:
        """Test that process receives the tree structure."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tree.root = root

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), {})

        assert node.last_call_args["tree"] is tree

    def test_process_receives_root(self) -> None:
        """Test that process receives the root node."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), {})

        assert node.last_call_args["root"] is root

    def test_process_receives_parents(self) -> None:
        """Test that process receives parent nodes list."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent1 = DummyParentNode(name="parent1")
        parent2 = DummyParentNode(name="parent2")

        node = ConcreteGlobalNode()
        node.process(tree, root, [parent1, parent2], {}, [], (), {})

        assert len(node.last_call_args["parents"]) == 2
        assert node.last_call_args["parents"][0] is parent1
        assert node.last_call_args["parents"][1] is parent2

    def test_process_receives_tags(self) -> None:
        """Test that process receives tags dictionary."""
        tree = Tree()
        root = DummyRootNode(name="root")
        tag = Tag(name="test_tag")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {"test_tag": tag}, [], (), {})

        assert "test_tag" in node.last_call_args["tags"]
        assert node.last_call_args["tags"]["test_tag"] is tag

    def test_process_receives_globals_list(self) -> None:
        """Test that process receives globals list including itself."""
        tree = Tree()
        root = DummyRootNode(name="root")
        node1 = ConcreteGlobalNode(name="node1")
        node2 = ConcreteGlobalNode(name="node2")

        node1.process(tree, root, [], {}, [node1, node2], (), {})

        assert len(node1.last_call_args["globals"]) == 2

    def test_process_receives_call_args(self) -> None:
        """Test that process receives call arguments."""
        tree = Tree()
        root = DummyRootNode(name="root")
        call_args = ("arg1", "arg2")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], call_args, {})

        assert node.last_call_args["call_args"] == call_args

    def test_process_receives_call_kwargs(self) -> None:
        """Test that process receives call keyword arguments."""
        tree = Tree()
        root = DummyRootNode(name="root")
        call_kwargs = {"key1": "value1", "key2": "value2"}

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), call_kwargs)

        assert node.last_call_args["call_kwargs"] == call_kwargs

    def test_process_receives_additional_args(self) -> None:
        """Test that process receives additional positional arguments."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), {}, "extra1", "extra2")

        assert node.last_call_args["args"] == ("extra1", "extra2")

    def test_process_receives_additional_kwargs(self) -> None:
        """Test that process receives additional keyword arguments."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), {}, extra_key="extra_value")

        assert node.last_call_args["kwargs"]["extra_key"] == "extra_value"

    def test_process_return_value(self) -> None:
        """Test that process returns configured value."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode(return_value={"test": "data"})
        result = node.process(tree, root, [], {}, [], (), {})

        assert result == {"test": "data"}

    def test_process_increments_call_count(self) -> None:
        """Test that process increments call count."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode()

        assert node.call_count == 0
        node.process(tree, root, [], {}, [], (), {})
        assert node.call_count == 1
        node.process(tree, root, [], {}, [], (), {})
        assert node.call_count == 2


class TestGlobalNodeAsDecorator:
    """Tests for GlobalNode.as_decorator class method."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_as_decorator_returns_callable(self) -> None:
        """Test that as_decorator returns a callable."""
        decorator = ConcreteGlobalNode.as_decorator()

        assert callable(decorator)

    def test_as_decorator_with_name(self) -> None:
        """Test as_decorator with injection name."""
        decorator = ConcreteGlobalNode.as_decorator("test_var")

        def test_func() -> None:
            pass

        result = decorator(test_func)
        assert callable(result)

    def test_as_decorator_without_name(self) -> None:
        """Test as_decorator in observer mode."""
        decorator = ConcreteGlobalNode.as_decorator()

        def test_func() -> None:
            pass

        result = decorator(test_func)
        assert callable(result)

    def test_as_decorator_with_delay(self) -> None:
        """Test as_decorator with delay parameter."""
        decorator = ConcreteGlobalNode.as_decorator(delay=True)

        def test_func() -> None:
            pass

        result = decorator(test_func)
        assert callable(result)

    def test_as_decorator_with_name_and_delay(self) -> None:
        """Test as_decorator with both name and delay."""
        decorator = ConcreteGlobalNode.as_decorator("var", delay=True)

        def test_func() -> None:
            pass

        result = decorator(test_func)
        assert callable(result)

    def test_as_decorator_queues_node(self) -> None:
        """Test that as_decorator queues the global node."""
        decorator = ConcreteGlobalNode.as_decorator("test")

        def test_func() -> None:
            pass

        decorator(test_func)
        pending = get_pending_nodes()

        assert len(pending) == 1
        assert pending[0][0] == "global"
        assert isinstance(pending[0][1], ConcreteGlobalNode)

    def test_as_decorator_stores_kwargs(self) -> None:
        """Test that as_decorator stores additional kwargs."""
        decorator = ConcreteGlobalNode.as_decorator(
            "test", custom_param="value"
        )

        def test_func() -> None:
            pass

        decorator(test_func)
        pending = get_pending_nodes()

        node = pending[0][1]
        assert isinstance(node, ConcreteGlobalNode)
        assert node.process_kwargs["custom_param"] == "value"

    def test_as_decorator_preserves_function(self) -> None:
        """Test that decorated function remains callable."""

        @ConcreteGlobalNode.as_decorator("test")
        def test_func(x: int) -> int:
            return x * 2

        assert test_func(5) == 10

    def test_as_decorator_preserves_function_metadata(self) -> None:
        """Test that decorator preserves function metadata."""

        @ConcreteGlobalNode.as_decorator("test")
        def test_func() -> None:
            """Test function docstring."""
            pass

        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."


class TestQueueGlobal:
    """Tests for queue_global function."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_queue_global_adds_to_pending(self) -> None:
        """Test that queue_global adds a global node to pending queue."""
        node = ConcreteGlobalNode(name="test")
        queue_global(node)

        pending = get_pending_nodes()
        assert len(pending) == 1
        assert pending[0] == ("global", node)

    def test_queue_global_preserves_node_reference(self) -> None:
        """Test that queued global node maintains its identity."""
        node = ConcreteGlobalNode(name="test")
        queue_global(node)

        pending = get_pending_nodes()
        retrieved_node = pending[0][1]

        assert retrieved_node is node

    def test_queue_global_multiple_nodes(self) -> None:
        """Test that multiple global nodes can be queued."""
        node1 = ConcreteGlobalNode(name="node1")
        node2 = ConcreteGlobalNode(name="node2")

        queue_global(node1)
        queue_global(node2)

        pending = get_pending_nodes()
        assert len(pending) == 2
        assert pending[0][1] is node1
        assert pending[1][1] is node2


class TestTreeGlobalsList:
    """Tests for Tree.globals list."""

    def test_tree_has_globals_list(self) -> None:
        """Test that Tree initializes with globals list."""
        tree = Tree()

        assert hasattr(tree, "globals")
        assert isinstance(tree.globals, list)
        assert len(tree.globals) == 0

    def test_tree_globals_list_is_mutable(self) -> None:
        """Test that Tree.globals list can be modified."""
        tree = Tree()
        node = ConcreteGlobalNode(name="test")

        tree.globals.append(node)

        assert len(tree.globals) == 1
        assert tree.globals[0] is node


class TestTreeRegisterRootWithGlobals:
    """Tests for Tree.register_root with global nodes."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_register_root_processes_global_nodes(self) -> None:
        """Test that register_root processes pending global nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        node = ConcreteGlobalNode(name="test")

        queue_global(node)
        tree.register_root(root)

        assert len(tree.globals) == 1
        assert tree.globals[0] is node

    def test_register_root_multiple_globals(self) -> None:
        """Test that register_root processes multiple global nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        node1 = ConcreteGlobalNode(name="node1")
        node2 = ConcreteGlobalNode(name="node2")
        node3 = ConcreteGlobalNode(name="node3")

        queue_global(node1)
        queue_global(node2)
        queue_global(node3)
        tree.register_root(root)

        assert len(tree.globals) == 3
        assert tree.globals[0] is node1
        assert tree.globals[1] is node2
        assert tree.globals[2] is node3

    def test_register_root_with_mixed_node_types(self) -> None:
        """Test register_root with global and parent nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parent = DummyParentNode(name="parent")
        global_node = ConcreteGlobalNode(name="global")

        from click_extended.core._tree import queue_parent

        queue_global(global_node)
        queue_parent(parent)
        tree.register_root(root)

        assert tree.root is root
        assert len(tree.globals) == 1
        assert tree.globals[0] is global_node
        assert root.children is not None
        assert "parent" in root.children

    def test_register_root_globals_order_preserved(self) -> None:
        """Test that global nodes maintain decorator order."""
        tree = Tree()
        root = DummyRootNode(name="root")

        nodes = [ConcreteGlobalNode(name=f"node{i}") for i in range(5)]
        for node in nodes:
            queue_global(node)

        tree.register_root(root)

        for i, node in enumerate(nodes):
            assert tree.globals[i] is node


class TestGlobalNodeObserverMode:
    """Tests for GlobalNode observer mode (name=None)."""

    def test_observer_mode_inject_name_is_none(self) -> None:
        """Test that observer mode has inject_name=None."""
        node = ConcreteGlobalNode()

        assert node.inject_name is None

    def test_observer_mode_can_return_value(self) -> None:
        """Test that observer mode can return values."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode(return_value="observed")
        result = node.process(tree, root, [], {}, [], (), {})

        assert result == "observed"

    def test_observer_mode_return_value_ignored(self) -> None:
        """Test that observer mode return value is not injected."""
        node = ConcreteGlobalNode(return_value="data")

        assert node.inject_name is None
        assert node.return_value == "data"


class TestGlobalNodeInjectionMode:
    """Tests for GlobalNode injection mode (name="var")."""

    def test_injection_mode_has_inject_name(self) -> None:
        """Test that injection mode stores inject_name."""
        node = ConcreteGlobalNode(name="my_var")

        assert node.inject_name == "my_var"

    def test_injection_mode_with_delay(self) -> None:
        """Test injection mode with delayed execution."""
        node = ConcreteGlobalNode(name="my_var", delay=True)

        assert node.inject_name == "my_var"
        assert node.delay is True

    def test_injection_mode_return_value_available(self) -> None:
        """Test that injection mode return value is available."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode(name="data_var", return_value={"key": "val"})
        result = node.process(tree, root, [], {}, [], (), {})

        assert result == {"key": "val"}
        assert node.inject_name == "data_var"


class TestGlobalNodeDelayParameter:
    """Tests for GlobalNode delay parameter."""

    def test_delay_false_by_default(self) -> None:
        """Test that delay defaults to False."""
        node = ConcreteGlobalNode()

        assert node.delay is False

    def test_delay_true_when_specified(self) -> None:
        """Test that delay can be set to True."""
        node = ConcreteGlobalNode(delay=True)

        assert node.delay is True

    def test_delay_with_name(self) -> None:
        """Test delay parameter with injection name."""
        node = ConcreteGlobalNode(name="var", delay=True)

        assert node.inject_name == "var"
        assert node.delay is True

    def test_delay_affects_timing(self) -> None:
        """Test that delay value is accessible for timing logic."""
        early_node = ConcreteGlobalNode(delay=False)
        late_node = ConcreteGlobalNode(delay=True)

        assert early_node.delay is False
        assert late_node.delay is True


class TestGlobalNodeEdgeCases:
    """Tests for GlobalNode edge cases."""

    def test_empty_parents_list(self) -> None:
        """Test process with empty parents list."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), {})

        assert node.last_call_args["parents"] == []

    def test_empty_tags_dict(self) -> None:
        """Test process with empty tags dictionary."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), {})

        assert node.last_call_args["tags"] == {}

    def test_empty_globals_list(self) -> None:
        """Test process with empty globals list."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode()
        node.process(tree, root, [], {}, [], (), {})

        assert node.last_call_args["globals"] == []

    def test_none_return_value(self) -> None:
        """Test that None can be returned from process."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode(return_value=None)
        result = node.process(tree, root, [], {}, [], (), {})

        assert result is None

    def test_complex_return_value(self) -> None:
        """Test that complex objects can be returned."""
        tree = Tree()
        root = DummyRootNode(name="root")

        complex_data: dict[str, Any] = {
            "tree": tree,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }
        node = ConcreteGlobalNode(return_value=complex_data)
        result = node.process(tree, root, [], {}, [], (), {})

        assert result is complex_data
        assert result["tree"] is tree

    def test_multiple_process_calls(self) -> None:
        """Test that process can be called multiple times."""
        tree = Tree()
        root = DummyRootNode(name="root")

        node = ConcreteGlobalNode(return_value=1)

        result1 = node.process(tree, root, [], {}, [], (), {})
        assert result1 == 1
        assert node.call_count == 1

        node.return_value = 2
        result2 = node.process(tree, root, [], {}, [], (), {})
        assert result2 == 2
        assert node.call_count == 2

    def test_inject_name_special_characters(self) -> None:
        """Test inject_name with underscores and numbers."""
        node = ConcreteGlobalNode(name="_test_var_123")

        assert node.inject_name == "_test_var_123"
        assert node.name == "_test_var_123"

    def test_process_with_large_parents_list(self) -> None:
        """Test process with many parent nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")
        parents: list[ParentNode] = [
            DummyParentNode(name=f"p{i}") for i in range(100)
        ]

        node = ConcreteGlobalNode()
        node.process(tree, root, parents, {}, [], (), {})

        assert len(node.last_call_args["parents"]) == 100


class TestGlobalNodeIntegration:
    """Integration tests for GlobalNode with Tree."""

    def setup_method(self) -> None:
        """Clear pending nodes before each test."""
        get_pending_nodes()

    def test_full_registration_flow(self) -> None:
        """Test complete flow of global node registration."""
        tree = Tree()
        root = DummyRootNode(name="root")

        @ConcreteGlobalNode.as_decorator("test_var")
        def dummy_func() -> None:  # type: ignore
            pass

        tree.register_root(root)

        assert len(tree.globals) == 1
        assert isinstance(tree.globals[0], ConcreteGlobalNode)
        assert tree.globals[0].inject_name == "test_var"

    def test_multiple_globals_registration(self) -> None:
        """Test registration of multiple global nodes."""
        tree = Tree()
        root = DummyRootNode(name="root")

        @ConcreteGlobalNode.as_decorator("var1")
        @ConcreteGlobalNode.as_decorator("var2", delay=True)
        @ConcreteGlobalNode.as_decorator()
        def dummy_func() -> None:  # type: ignore
            pass

        tree.register_root(root)

        assert len(tree.globals) == 3
        assert tree.globals[0].inject_name is None
        assert tree.globals[1].inject_name == "var2"
        assert tree.globals[2].inject_name == "var1"

    def test_globals_with_parents(self) -> None:
        """Test global nodes registered alongside parent nodes."""
        from click_extended.core._tree import queue_parent

        tree = Tree()
        root = DummyRootNode(name="root")
        parent = DummyParentNode(name="option")

        queue_global(ConcreteGlobalNode(name="global1"))
        queue_parent(parent)
        queue_global(ConcreteGlobalNode(name="global2"))

        tree.register_root(root)

        assert len(tree.globals) == 2
        assert "option" in root.children
