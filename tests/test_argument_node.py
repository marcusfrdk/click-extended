"""Comprehensive tests for ArgumentNode functionality."""

from typing import Any

import click
import pytest

from click_extended.core.decorators.argument import Argument, argument
from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.nodes.argument_node import ArgumentNode
from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other._tree import Tree
from click_extended.core.other.context import Context


class ConcreteArgumentNode(ArgumentNode):
    """Concrete implementation of ArgumentNode for testing."""

    def load(
        self,
        value: str | int | float | bool | None,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Simple load implementation that returns the value."""
        return value


class TestArgumentNodeInit:
    """Test ArgumentNode initialization with various configurations."""

    def test_init_with_only_name(self) -> None:
        """Test initialization with only required name parameter."""
        node = ConcreteArgumentNode(name="test_arg")

        assert node.name == "test_arg"
        assert node.param == "test_arg"
        assert node.help is None
        assert node.required is True
        assert node.default is None
        assert node.tags == []
        assert node.nargs == 1
        assert node.type is None
        assert node.was_provided is False
        assert node.cached_value is None
        assert node._value_computed is False  # type: ignore
        assert node.decorator_kwargs == {}
        assert node.children == {}

    def test_init_with_explicit_param(self) -> None:
        """Test that param parameter is used when provided."""
        node = ConcreteArgumentNode(name="test_arg", param="custom_param")

        assert node.name == "custom_param"
        assert node.param == "custom_param"

    def test_init_param_defaults_to_name(self) -> None:
        """Test that param defaults to name when not provided."""
        node = ConcreteArgumentNode(name="my_argument")

        assert node.param == "my_argument"

    def test_init_with_help_text(self) -> None:
        """Test initialization with help text."""
        help_text = "This is an argument"
        node = ConcreteArgumentNode(name="test_arg", help=help_text)

        assert node.help == help_text

    def test_init_with_required_true(self) -> None:
        """Test initialization with required=True (default for arguments)."""
        node = ConcreteArgumentNode(name="test_arg", required=True)

        assert node.required is True

    def test_init_with_required_false(self) -> None:
        """Test initialization with required=False (optional argument)."""
        node = ConcreteArgumentNode(name="test_arg", required=False)

        assert node.required is False

    def test_init_with_default_value(self) -> None:
        """Test initialization with default value."""
        node = ConcreteArgumentNode(name="test_arg", default="default_value")

        assert node.default == "default_value"

    def test_init_with_tags_single_string(self) -> None:
        """Test initialization with single tag as string."""
        node = ConcreteArgumentNode(name="test_arg", tags="input")

        assert node.tags == ["input"]

    def test_init_with_tags_list(self) -> None:
        """Test initialization with list of tags."""
        node = ConcreteArgumentNode(name="test_arg", tags=["input", "file"])

        assert node.tags == ["input", "file"]

    def test_init_with_nargs_single(self) -> None:
        """Test initialization with nargs=1 (default)."""
        node = ConcreteArgumentNode(name="test_arg", nargs=1)

        assert node.nargs == 1

    def test_init_with_nargs_multiple(self) -> None:
        """Test initialization with nargs=3 for multiple values."""
        node = ConcreteArgumentNode(name="test_arg", nargs=3)

        assert node.nargs == 3

    def test_init_with_nargs_unlimited(self) -> None:
        """Test initialization with nargs=-1 for unlimited."""
        node = ConcreteArgumentNode(name="test_arg", nargs=-1)

        assert node.nargs == -1

    def test_init_with_type_str(self) -> None:
        """Test initialization with string type."""
        node = ConcreteArgumentNode(name="test_arg", type=str)

        assert node.type is str

    def test_init_with_type_int(self) -> None:
        """Test initialization with integer type."""
        node = ConcreteArgumentNode(name="test_arg", type=int)

        assert node.type is int

    def test_init_with_type_float(self) -> None:
        """Test initialization with float type."""
        node = ConcreteArgumentNode(name="test_arg", type=float)

        assert node.type is float

    def test_init_with_type_bool(self) -> None:
        """Test initialization with bool type."""
        node = ConcreteArgumentNode(name="test_arg", type=bool)

        assert node.type is bool

    def test_init_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        node = ConcreteArgumentNode(
            name="full_arg",
            param="injection_name",
            nargs=3,
            type=int,
            help="Detailed help",
            required=False,
            default=42,
            tags=["tag1", "tag2"],
        )

        assert node.name == "injection_name"
        assert node.param == "injection_name"
        assert node.nargs == 3
        assert node.type is int
        assert node.help == "Detailed help"
        assert node.required is False
        assert node.default == 42
        assert node.tags == ["tag1", "tag2"]


class TestArgumentNodeMethods:
    """Test ArgumentNode-specific methods and inheritance."""

    def test_load_is_abstract_in_base_class(self) -> None:
        """Test that ArgumentNode.load is abstract."""
        with pytest.raises(TypeError):
            ArgumentNode(name="test")  # type: ignore

    def test_concrete_load_implementation(self) -> None:
        """Test that concrete subclass can implement load."""

        node = ConcreteArgumentNode(name="test_arg")

        @command()
        def dummy() -> None:  # type: ignore
            pass

        Tree._pending_nodes.clear()  # type: ignore

        result = node.load("test_value", None)  # type: ignore
        assert result == "test_value"

    def test_get_value_returns_cached_value(self) -> None:
        """Test that get_value returns cached_value."""
        node = ConcreteArgumentNode(name="test_arg")
        node.cached_value = "cached"

        assert node.get_value() == "cached"

    def test_repr_format(self) -> None:
        """Test string representation format."""
        node = ConcreteArgumentNode(name="test_arg")

        repr_str = repr(node)
        assert "ConcreteArgumentNode" in repr_str
        assert "test_arg" in repr_str

    def test_argument_node_extends_parent_node(self) -> None:
        """Test that ArgumentNode properly extends ParentNode."""

        assert issubclass(ArgumentNode, ParentNode)

    def test_argument_node_has_nargs_attribute(self) -> None:
        """Test that ArgumentNode has nargs attribute."""
        node = ConcreteArgumentNode(name="test_arg", nargs=5)

        assert hasattr(node, "nargs")
        assert node.nargs == 5

    def test_argument_node_has_type_attribute(self) -> None:
        """Test that ArgumentNode has type attribute."""
        node = ConcreteArgumentNode(name="test_arg", type=int)

        assert hasattr(node, "type")
        assert node.type is int

    def test_nargs_default_is_one(self) -> None:
        """Test that nargs defaults to 1."""
        node = ConcreteArgumentNode(name="test_arg")

        assert node.nargs == 1

    def test_type_can_be_none(self) -> None:
        """Test that type can be None (Click will use default)."""
        node = ConcreteArgumentNode(name="test_arg", type=None)

        assert node.type is None


class TestArgumentDecorator:
    """Test the @argument() decorator and Argument class functionality."""

    def test_decorator_can_be_applied_to_function(self) -> None:
        """Test that @argument decorator can be applied to a function."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("filename")
        def process_file(filename: str) -> None:  # type: ignore
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        assert pending[0][0] == "parent"

    def test_decorator_preserves_function_name(self) -> None:
        """Test that decorator preserves function name."""

        @argument("filename")
        def my_function(filename: str) -> None:
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"

    def test_decorator_preserves_function_docstring(self) -> None:
        """Test that decorator preserves function docstring."""

        @argument("filename")
        def my_function(filename: str) -> None:
            """My docstring."""
            pass

        assert my_function.__doc__ == "My docstring."

    def test_decorator_queues_in_tree(self) -> None:
        """Test that decorator registers in Tree."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("filename")
        def process_file(filename: str) -> None:  # type: ignore
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        node_type, node = pending[0]
        assert node_type == "parent"
        assert node.name == "filename"

    def test_decorator_creates_argument_instance(self) -> None:
        """Test that decorator creates Argument instance."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("filename")
        def process_file(filename: str) -> None:  # type: ignore
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]
        assert isinstance(node, Argument)

    def test_argument_name_snake_case(self) -> None:
        """Test argument with snake_case name."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("input_file")
        def process(input_file: str) -> None:  # type: ignore
            pass

        node = Tree.get_pending_nodes()[0][1]
        assert isinstance(node, ArgumentNode)
        assert node.param == "input_file"

    def test_argument_name_kebab_case_converts(self) -> None:
        """Test that kebab-case name converts to snake_case."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("input-file")
        def process(input_file: str) -> None:  # type: ignore
            pass

        node = Tree.get_pending_nodes()[0][1]
        assert isinstance(node, ArgumentNode)
        assert node.param == "input_file"

    def test_argument_name_screaming_snake_case_converts(self) -> None:
        """Test that SCREAMING_SNAKE_CASE converts to snake_case."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("INPUT_FILE")
        def process(input_file: str) -> None:  # type: ignore
            pass

        node = Tree.get_pending_nodes()[0][1]
        assert isinstance(node, ArgumentNode)
        assert node.param == "input_file"

    def test_param_override_with_custom_name(self) -> None:
        """Test that param parameter overrides default naming."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("input_file", param="custom_name")
        def process(custom_name: str) -> None:  # type: ignore
            pass

        node = Tree.get_pending_nodes()[0][1]
        assert isinstance(node, ArgumentNode)
        assert node.param == "custom_name"

    def test_decorator_kwargs_stored(self) -> None:
        """Test that all configuration is stored in decorator_kwargs."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument(
            "filename",
            nargs=3,
            type=int,
            help="Input files",
            required=False,
            default=None,
            tags=["input"],
        )
        def process(filename: str) -> None:  # type: ignore
            pass

        node = Tree.get_pending_nodes()[0][1]
        assert isinstance(node, ArgumentNode)
        assert node.decorator_kwargs["name"] == "filename"
        assert node.decorator_kwargs["nargs"] == 3
        assert node.decorator_kwargs["type"] == int
        assert node.decorator_kwargs["help"] == "Input files"
        assert node.decorator_kwargs["tags"] == ["input"]

    def test_multiple_arguments_queue_in_order(self) -> None:
        """Test that multiple @argument decorators queue in order."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("first")
        @argument("second")
        def process(first: str, second: str) -> None:  # type: ignore
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 2
        node1 = pending[0][1]
        node2 = pending[1][1]
        assert isinstance(node1, ArgumentNode)
        assert isinstance(node2, ArgumentNode)
        assert node1.param == "second"
        assert node2.param == "first"

    def test_type_inference_from_default_value(self) -> None:
        """Test that type is inferred from default value."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("port", default=8080)
        def serve(port: int) -> None:  # type: ignore
            pass

        node = Tree.get_pending_nodes()[0][1]
        assert isinstance(node, ArgumentNode)
        assert node.type == int  # Inferred from default value

    def test_default_makes_argument_optional(self) -> None:
        """Test that providing default makes argument optional."""

        Tree._pending_nodes.clear()  # type: ignore

        @argument("filename", default="input.txt")
        def process(filename: str) -> None:  # type: ignore
            pass

        node = Tree.get_pending_nodes()[0][1]
        assert isinstance(node, ArgumentNode)
        assert node.required is False  # Auto-set to optional


class TestArgumentCommandIntegration:
    """Test ArgumentNode integration with commands in real CLI scenarios."""

    def test_single_argument_required(self, cli_runner: Any) -> None:
        """Test that required argument must be provided."""

        @command()
        @argument("filename")
        def process(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(process, [])
        assert result.exit_code != 0

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 0
        assert "File: test.txt" in result.output

    def test_single_argument_optional_with_default(
        self, cli_runner: Any
    ) -> None:
        """Test optional argument with default value."""

        @command()
        @argument("filename", default="default.txt")
        def process(filename: str) -> None:
            click.echo(f"File: {filename}")

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0
        assert "File: default.txt" in result.output

        result = cli_runner.invoke(process, ["custom.txt"])
        assert result.exit_code == 0
        assert "File: custom.txt" in result.output

    def test_single_argument_receives_value(self, cli_runner: Any) -> None:
        """Test that argument value is injected correctly."""

        @command()
        @argument("name")
        def greet(name: str) -> None:
            click.echo(f"Hello {name}!")

        result = cli_runner.invoke(greet, ["Alice"])
        assert result.exit_code == 0
        assert "Hello Alice!" in result.output

    def test_multiple_arguments_in_order(self, cli_runner: Any) -> None:
        """Test that multiple arguments are parsed in order."""

        @command()
        @argument("third")
        @argument("second")
        @argument("first")
        def combine(first: str, second: str, third: str) -> None:
            click.echo(f"{first}-{second}-{third}")

        result = cli_runner.invoke(combine, ["A", "B", "C"])
        assert result.exit_code == 0
        assert "A-B-C" in result.output

    def test_mix_arguments_and_options(self, cli_runner: Any) -> None:
        """Test mixing argument and option nodes."""

        @command()
        @argument("filename")
        @option("--verbose", is_flag=True, default=False)
        def process(filename: str, verbose: bool) -> None:
            if verbose:
                click.echo(f"Processing file: {filename}")
            else:
                click.echo(filename)

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 0
        assert result.output.strip() == "test.txt"

        result = cli_runner.invoke(process, ["test.txt", "--verbose"])
        assert result.exit_code == 0
        assert "Processing file: test.txt" in result.output

    def test_argument_nargs_single(self, cli_runner: Any) -> None:
        """Test argument with nargs=1 (single value)."""

        @command()
        @argument("value", nargs=1)
        def show(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(show, ["single"])
        assert result.exit_code == 0
        assert "Value: single" in result.output

    def test_argument_nargs_multiple_fixed(self, cli_runner: Any) -> None:
        """Test argument with nargs=3 (tuple of 3 values)."""

        @command()
        @argument("coords", nargs=3, type=int)
        def plot(coords: tuple[int, int, int]) -> None:
            x, y, z = coords
            click.echo(f"Plotting at ({x}, {y}, {z})")

        result = cli_runner.invoke(plot, ["10", "20", "30"])
        assert result.exit_code == 0
        assert "Plotting at (10, 20, 30)" in result.output

    def test_argument_nargs_unlimited(self, cli_runner: Any) -> None:
        """Test argument with nargs=-1 (list of all values)."""

        @command()
        @argument("files", nargs=-1)
        def process_files(files: tuple[str, ...]) -> None:
            for f in files:
                click.echo(f"Processing: {f}")

        result = cli_runner.invoke(process_files, ["a.txt", "b.txt", "c.txt"])
        assert result.exit_code == 0
        assert "Processing: a.txt" in result.output
        assert "Processing: b.txt" in result.output
        assert "Processing: c.txt" in result.output

    def test_argument_type_int(self, cli_runner: Any) -> None:
        """Test argument with type conversion to int."""

        @command()
        @argument("count", type=int)
        def repeat(count: int) -> None:
            click.echo(f"Count: {count} (type: {type(count).__name__})")

        result = cli_runner.invoke(repeat, ["42"])
        assert result.exit_code == 0
        assert "Count: 42" in result.output
        assert "type: int" in result.output

    def test_argument_type_float(self, cli_runner: Any) -> None:
        """Test argument with type conversion to float."""

        @command()
        @argument("value", type=float)
        def calculate(value: float) -> None:
            click.echo(f"Value: {value:.2f}")

        result = cli_runner.invoke(calculate, ["3.14"])
        assert result.exit_code == 0
        assert "Value: 3.14" in result.output

    def test_argument_invalid_type_raises_error(self, cli_runner: Any) -> None:
        """Test that invalid type conversion fails gracefully."""

        @command()
        @argument("number", type=int)
        def show(number: int) -> None:
            click.echo(f"Number: {number}")

        result = cli_runner.invoke(show, ["not-a-number"])
        assert result.exit_code != 0

    def test_argument_was_provided_flag(self, cli_runner: Any) -> None:
        """Test that was_provided flag is set correctly."""

        @command()
        @argument("value", default="default")
        def check(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(check, ["custom"])
        assert result.exit_code == 0
        assert "Value: custom" in result.output

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 0
        assert "Value: default" in result.output

    def test_argument_cached_value_is_set(self, cli_runner: Any) -> None:
        """Test that cached_value is set after processing."""

        @command()
        @argument("value")
        def check(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(check, ["test"])
        assert result.exit_code == 0
        assert "Value: test" in result.output

    def test_argument_param_injection_name(self, cli_runner: Any) -> None:
        """Test that param determines injection name."""

        @command()
        @argument("input_file", param="filename")
        def process(filename: str) -> None:
            click.echo(f"Filename: {filename}")

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 0
        assert "Filename: test.txt" in result.output


class TestArgumentNodeWithChildren:
    """Test ArgumentNode with child validators/transformers."""

    def test_argument_with_single_child_validator(
        self, cli_runner: Any
    ) -> None:
        """Test argument with one child validator."""

        class MinLength(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                if len(value) < 3:
                    raise ValueError("Must be at least 3 characters")
                return value

        @command()
        @argument("name")
        @MinLength.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello {name}")

        result = cli_runner.invoke(greet, ["Alice"])
        assert result.exit_code == 0
        assert "Hello Alice" in result.output

        result = cli_runner.invoke(greet, ["Al"])
        assert result.exit_code != 0

    def test_argument_with_single_child_transformer(
        self, cli_runner: Any
    ) -> None:
        """Test argument with one child transformer."""

        class Uppercase(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @argument("name")
        @Uppercase.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello {name}")

        result = cli_runner.invoke(greet, ["alice"])
        assert result.exit_code == 0
        assert "Hello ALICE" in result.output

    def test_argument_with_multiple_children_chain(
        self, cli_runner: Any
    ) -> None:
        """Test argument with multiple child nodes chained."""

        class StripWhitespace(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.strip()

        class Uppercase(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @argument("name")
        @StripWhitespace.as_decorator()
        @Uppercase.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello {name}")

        result = cli_runner.invoke(greet, ["  alice  "])
        assert result.exit_code == 0
        assert "Hello ALICE" in result.output

    def test_argument_with_child_sync(self, cli_runner: Any) -> None:
        """Test argument with sync child handler."""

        class Double(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

        @command()
        @argument("num", type=int)
        @Double.as_decorator()
        def calculate(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(calculate, ["5"])
        assert result.exit_code == 0
        assert "Result: 10" in result.output

    def test_argument_with_child_async(self, cli_runner: Any) -> None:
        """Test argument with async child handler."""

        class AsyncUpper(ChildNode):
            async def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

        @command()
        @argument("name")
        @AsyncUpper.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello {name}")

        result = cli_runner.invoke(greet, ["alice"])
        assert result.exit_code == 0
        assert "Hello ALICE" in result.output

    def test_argument_child_receives_correct_value(
        self, cli_runner: Any
    ) -> None:
        """Test that child receives the argument value."""

        class AddPrefix(ChildNode):
            def handle_str(self, value: str, context: Context) -> str:
                return f"prefix_{value}"

        @command()
        @argument("name")
        @AddPrefix.as_decorator()
        def process(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(process, ["test"])
        assert result.exit_code == 0
        assert "Name: prefix_test" in result.output

    def test_argument_processed_value_cached(self, cli_runner: Any) -> None:
        """Test that final value after children is what gets injected."""

        class Multiply(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 3

        @command()
        @argument("num", type=int)
        @Multiply.as_decorator()
        def show(num: int) -> None:
            click.echo(f"Final: {num}")

        result = cli_runner.invoke(show, ["7"])
        assert result.exit_code == 0
        assert "Final: 21" in result.output

    def test_argument_child_validation_error_propagates(
        self, cli_runner: Any
    ) -> None:
        """Test that validation errors from children are handled."""

        class PositiveOnly(ChildNode):
            def handle_int(self, value: int, context: Context) -> int:
                if value <= 0:
                    raise ValueError("Must be positive")
                return value

        @command()
        @argument("num", type=int)
        @PositiveOnly.as_decorator()
        def process(num: int) -> None:
            click.echo(f"Number: {num}")

        result = cli_runner.invoke(process, ["5"])
        assert result.exit_code == 0

        result = cli_runner.invoke(process, ["-5"])
        assert result.exit_code != 0

    def test_argument_nargs_unlimited_with_children(
        self, cli_runner: Any
    ) -> None:
        """Test nargs=-1 argument receives values correctly."""

        @command()
        @argument("names", nargs=-1)
        def greet(names: tuple[str, ...]) -> None:
            assert isinstance(names, tuple)
            for name in names:
                click.echo(f"Hello {name.upper()}")

        result = cli_runner.invoke(greet, ["alice", "bob", "charlie"])
        assert result.exit_code == 0
        assert "Hello ALICE" in result.output
        assert "Hello BOB" in result.output
        assert "Hello CHARLIE" in result.output


class TestArgumentNodeEdgeCases:
    """Test edge cases and error scenarios."""

    def test_argument_with_none_value_optional(self, cli_runner: Any) -> None:
        """Test handling None for optional argument."""

        @command()
        @argument("value", required=False, default=None)
        def show(value: str | None) -> None:
            if value is None:
                click.echo("No value")
            else:
                click.echo(f"Value: {value}")

        result = cli_runner.invoke(show, [])
        assert result.exit_code == 0
        assert "No value" in result.output

    def test_empty_string_argument(self, cli_runner: Any) -> None:
        """Test that empty string is a valid argument value."""

        @command()
        @argument("value")
        def show(value: str) -> None:
            click.echo(f"Length: {len(value)}")

        result = cli_runner.invoke(show, [""])
        assert result.exit_code == 0
        assert "Length: 0" in result.output

    def test_argument_name_with_underscores(self, cli_runner: Any) -> None:
        """Test argument name normalization with underscores."""

        @command()
        @argument("input_file_name")
        def process(input_file_name: str) -> None:
            click.echo(f"File: {input_file_name}")

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 0
        assert "File: test.txt" in result.output

    def test_argument_name_with_numbers(self, cli_runner: Any) -> None:
        """Test argument names with numbers at the end."""

        @command()
        @argument("file_v2")
        def run(file_v2: str) -> None:
            click.echo(f"Processing: {file_v2}")

        result = cli_runner.invoke(run, ["data.csv"])
        assert result.exit_code == 0
        assert "Processing: data.csv" in result.output

    def test_variadic_arguments_empty_list(self, cli_runner: Any) -> None:
        """Test nargs=-1 with no values provided."""

        @command()
        @argument("files", nargs=-1, required=False)
        def process(files: tuple[str, ...]) -> None:
            if not files:
                click.echo("No files")
            else:
                click.echo(f"Files: {len(files)}")

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0
        assert "No files" in result.output

    def test_argument_with_special_characters(self, cli_runner: Any) -> None:
        """Test arguments with special characters in values."""

        @command()
        @argument("path")
        def show(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(show, ["/path/to/file-name_v2.0.txt"])
        assert result.exit_code == 0
        assert "Path: /path/to/file-name_v2.0.txt" in result.output
