"""Comprehensive tests for OptionNode functionality."""

from typing import Any

import pytest

from click_extended.core.nodes.option_node import OptionNode
from click_extended.core.other.context import Context


class ConcreteOptionNode(OptionNode):
    """Concrete implementation of OptionNode for testing."""

    def load(
        self,
        value: str | int | float | bool | None,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Simple load implementation that returns the value."""
        return value


class TestOptionNodeInit:
    """Test OptionNode initialization with various configurations."""

    def test_init_with_only_name(self) -> None:
        """Test initialization with only required name parameter."""
        node = ConcreteOptionNode(name="test_opt")

        assert node.name == "test_opt"
        assert node.param == "test_opt"  # defaults to name
        assert node.help is None
        assert node.required is False  # Options default to optional
        assert node.default is None
        assert node.tags == []
        assert node.short_flags == []
        assert node.long_flags == ["--test-opt"]  # auto-generated kebab-case
        assert node.is_flag is False
        assert node.type is None
        assert node.nargs == 1
        assert node.multiple is False
        assert node.was_provided is False
        assert node.cached_value is None
        assert node._value_computed is False
        assert node.decorator_kwargs == {}
        assert node.children == {}

    def test_init_with_explicit_param(self) -> None:
        """Test that param parameter is used when provided."""
        node = ConcreteOptionNode(name="test_opt", param="custom_param")

        assert node.name == "custom_param"
        assert node.param == "custom_param"

    def test_init_with_short_flag(self) -> None:
        """Test initialization with short flag."""
        node = ConcreteOptionNode(name="verbose", short_flags=["-v"])

        assert node.short_flags == ["-v"]
        assert node.long_flags == ["--verbose"]

    def test_init_with_long_flag(self) -> None:
        """Test initialization with explicit long flag."""
        node = ConcreteOptionNode(name="config", long_flags=["--cfg"])

        assert node.long_flags == ["--cfg"]
        assert node.short_flags == []

    def test_init_with_both_flags(self) -> None:
        """Test initialization with both short and long flags."""
        node = ConcreteOptionNode(
            name="port", short_flags=["-p"], long_flags=["--port-num"]
        )

        assert node.short_flags == ["-p"]
        assert node.long_flags == ["--port-num"]

    def test_init_as_boolean_flag(self) -> None:
        """Test initialization as a boolean flag."""
        node = ConcreteOptionNode(name="verbose", is_flag=True)

        assert node.is_flag is True
        assert node.long_flags == ["--verbose"]

    def test_init_with_type(self) -> None:
        """Test initialization with explicit type."""
        node = ConcreteOptionNode(name="port", type=int)

        assert node.type == int

    def test_init_with_nargs(self) -> None:
        """Test initialization with nargs for multiple values."""
        node = ConcreteOptionNode(name="coords", nargs=3, type=float)

        assert node.nargs == 3
        assert node.type == float

    def test_init_with_multiple(self) -> None:
        """Test initialization with multiple flag for repeated options."""
        node = ConcreteOptionNode(name="tag", multiple=True)

        assert node.multiple is True

    def test_init_with_help_text(self) -> None:
        """Test initialization with help text."""
        help_text = "Port number for the server"
        node = ConcreteOptionNode(name="port", help=help_text)

        assert node.help == help_text

    def test_init_with_required(self) -> None:
        """Test initialization with required flag."""
        node = ConcreteOptionNode(name="config", required=True)

        assert node.required is True

    def test_init_with_default_value(self) -> None:
        """Test initialization with default value."""
        node = ConcreteOptionNode(name="port", default=8080)

        assert node.default == 8080

    def test_init_with_single_tag(self) -> None:
        """Test initialization with single tag string."""
        node = ConcreteOptionNode(name="port", tags="network")

        assert node.tags == ["network"]

    def test_init_with_multiple_tags(self) -> None:
        """Test initialization with list of tags."""
        node = ConcreteOptionNode(name="port", tags=["network", "server"])

        assert node.tags == ["network", "server"]

    def test_init_with_all_parameters(self) -> None:
        """Test initialization with all parameters specified."""
        node = ConcreteOptionNode(
            name="port",
            param="port_num",
            short_flags=["-p"],
            long_flags=["--port-number"],
            is_flag=False,
            type=int,
            nargs=1,
            multiple=False,
            help="Server port",
            required=True,
            default=8080,
            tags=["network", "config"],
        )

        assert node.name == "port_num"
        assert node.param == "port_num"
        assert node.short_flags == ["-p"]
        assert node.long_flags == ["--port-number"]
        assert node.is_flag is False
        assert node.type == int
        assert node.nargs == 1
        assert node.multiple is False
        assert node.help == "Server port"
        assert node.required is True
        assert node.default == 8080
        assert node.tags == ["network", "config"]

    def test_init_auto_generates_long_flag(self) -> None:
        """Test that long flag is auto-generated as kebab-case."""
        node = ConcreteOptionNode(name="config_file")

        assert node.long_flags == ["--config-file"]

    def test_init_flag_without_explicit_default(self) -> None:
        """Test that flags get default value automatically."""
        # Note: The base OptionNode doesn't set default for is_flag,
        # that's done in the Option concrete class
        node = ConcreteOptionNode(name="verbose", is_flag=True)

        # Base OptionNode doesn't auto-set default for flags
        assert node.is_flag is True
        assert node.default is None

    def test_init_preserves_none_default(self) -> None:
        """Test that None default is preserved."""
        node = ConcreteOptionNode(name="optional", default=None)

        assert node.default is None

    def test_init_with_zero_default(self) -> None:
        """Test initialization with zero as default value."""
        node = ConcreteOptionNode(name="retries", type=int, default=0)

        assert node.default == 0
        assert node.type == int

    def test_init_with_empty_string_default(self) -> None:
        """Test initialization with empty string as default."""
        node = ConcreteOptionNode(name="prefix", default="")

        assert node.default == ""

    def test_init_nargs_multiple_combination(self) -> None:
        """Test initialization with both nargs and multiple."""
        # This is valid: each occurrence takes nargs values
        node = ConcreteOptionNode(name="pairs", nargs=2, multiple=True)

        assert node.nargs == 2
        assert node.multiple is True


class TestOptionNodeMethods:
    """Test OptionNode methods and behavior."""

    def test_load_method_signature(self) -> None:
        """Test that load method has correct signature."""
        from unittest.mock import MagicMock

        node = ConcreteOptionNode(name="test")
        context = Context(
            root=MagicMock(),
            current=None,
            parent=None,
            click_context=MagicMock(),
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        # Should accept value, context, and optional args/kwargs
        result = node.load("test_value", context)
        assert result == "test_value"

    def test_load_with_different_types(self) -> None:
        """Test load method with different value types."""
        from unittest.mock import MagicMock

        node = ConcreteOptionNode(name="test")
        context = Context(
            root=MagicMock(),
            current=None,
            parent=None,
            click_context=MagicMock(),
            nodes={},
            parents={},
            tags={},
            children={},
            data={},
        )

        assert node.load("string", context) == "string"
        assert node.load(42, context) == 42
        assert node.load(3.14, context) == 3.14
        assert node.load(True, context) is True
        assert node.load(None, context) is None

    def test_as_decorator_returns_callable(self) -> None:
        """Test that as_decorator returns a callable decorator."""
        decorator = ConcreteOptionNode.as_decorator(name="test")

        assert callable(decorator)

    def test_inherits_from_parent_node(self) -> None:
        """Test that OptionNode inherits from ParentNode."""
        from click_extended.core.nodes.parent_node import ParentNode

        node = ConcreteOptionNode(name="test")
        assert isinstance(node, ParentNode)

    def test_value_caching_behavior(self) -> None:
        """Test that value caching works correctly."""
        node = ConcreteOptionNode(name="test")

        assert node.was_provided is False
        assert node.cached_value is None
        assert node._value_computed is False

    def test_children_dict_is_initialized(self) -> None:
        """Test that children dictionary is initialized."""
        node = ConcreteOptionNode(name="test")

        assert isinstance(node.children, dict)
        assert len(node.children) == 0

    def test_tags_normalized_to_list(self) -> None:
        """Test that tags are normalized to list."""
        node1 = ConcreteOptionNode(name="test1", tags="single")
        node2 = ConcreteOptionNode(name="test2", tags=["multi", "tags"])
        node3 = ConcreteOptionNode(name="test3")

        assert isinstance(node1.tags, list)
        assert isinstance(node2.tags, list)
        assert isinstance(node3.tags, list)
        assert node1.tags == ["single"]
        assert node2.tags == ["multi", "tags"]
        assert node3.tags == []


class TestOptionNaming:
    """Test Option class naming and flag validation/derivation."""

    def test_snake_case_name(self) -> None:
        """Test option with snake_case name."""
        from click_extended.core.decorators.option import Option

        opt = Option(name="config_file")

        assert opt.param == "config_file"
        assert opt.long_flags == ["--config-file"]

    def test_kebab_case_name(self) -> None:
        """Test option with kebab-case name."""
        from click_extended.core.decorators.option import Option

        opt = Option(name="config-file")

        assert opt.param == "config_file"  # converted to snake_case for param
        assert opt.long_flags == ["--config-file"]

    def test_screaming_snake_case_name(self) -> None:
        """Test option with SCREAMING_SNAKE_CASE name."""
        from click_extended.core.decorators.option import Option

        opt = Option(name="CONFIG_FILE")

        assert opt.param == "config_file"  # converted to snake_case for param
        assert opt.long_flags == ["--config-file"]

    def test_long_flag_as_name(self) -> None:
        """Test providing long flag directly as name."""
        from click_extended.core.decorators.option import Option

        opt = Option(name="--verbose")

        assert opt.param == "verbose"
        assert opt.long_flags == ["--verbose"]

    def test_long_flag_override(self) -> None:
        """Test explicit long flag override."""
        from click_extended.core.decorators.option import Option

        opt = Option("configuration", "--cfg")

        assert opt.param == "configuration"
        assert opt.long_flags == ["--cfg"]

    def test_param_override(self) -> None:
        """Test custom parameter name."""
        from click_extended.core.decorators.option import Option

        opt = Option(name="configuration_file", param="cfg")

        assert opt.param == "cfg"
        assert opt.long_flags == ["--configuration-file"]

    def test_short_flag_valid(self) -> None:
        """Test valid short flag."""
        from click_extended.core.decorators.option import Option

        opt = Option("port", "-p")

        assert opt.short_flags == ["-p"]
        assert opt.long_flags == ["--port"]

    def test_short_flag_invalid_format(self) -> None:
        """Test invalid short flag format raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid flag"):
            Option("port", "p")  # missing dash

    def test_short_flag_invalid_multiple_chars(self) -> None:
        """Test short flag with multiple characters raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid short flag"):
            Option("port", "-port")

    def test_long_flag_invalid_format(self) -> None:
        """Test invalid long flag format raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid short flag"):
            Option("port", "-port")  # single dash but multiple chars

    def test_long_flag_invalid_uppercase(self) -> None:
        """Test long flag with uppercase raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid long flag"):
            Option("port", "--Port")

    def test_name_validation_empty(self) -> None:
        """Test empty name raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError):
            Option(name="")

    def test_name_validation_spaces(self) -> None:
        """Test name with spaces raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError):
            Option(name="my option")

    def test_auto_kebab_case_conversion(self) -> None:
        """Test that snake_case names auto-convert to kebab-case for long flag."""
        from click_extended.core.decorators.option import Option

        opt = Option(name="my_long_option_name")

        assert opt.long_flags == ["--my-long-option-name"]
        assert opt.param == "my_long_option_name"

    def test_long_flag_with_name_and_explicit_override(self) -> None:
        """Test long flag as name with explicit long override."""
        from click_extended.core.decorators.option import Option

        opt = Option("--verbose", "--debug")

        assert opt.param == "verbose"
        assert opt.long_flags == ["--debug"]

    def test_both_flags_specified(self) -> None:
        """Test specifying both short and long flags."""
        from click_extended.core.decorators.option import Option

        opt = Option("port", "-p", "--port-number")

        assert opt.short_flags == ["-p"]
        assert opt.long_flags == ["--port-number"]
        assert opt.param == "port"

    def test_param_validation(self) -> None:
        """Test that param name is validated."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError):
            Option(name="test", param="invalid name")


class TestOptionDecorator:
    """Test Option decorator functionality."""

    def test_basic_decorator_application(self) -> None:
        """Test basic option decorator on a function."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("port", type=int)
        def serve(port: int) -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        assert pending[0][0] == "parent"

    def test_multiple_options_on_same_function(self) -> None:
        """Test multiple option decorators on same function."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("port", type=int)
        @option("host")
        def serve(host: str, port: int) -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 2

    def test_decorator_stacking_order(self) -> None:
        """Test that decorators are queued in correct order."""
        from click_extended.core.decorators.option import Option, option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("first")
        @option("second")
        def process(first: str, second: str) -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 2
        # Decorators apply bottom-to-top, so second is queued first
        node1 = pending[0][1]
        node2 = pending[1][1]
        assert isinstance(node1, Option)
        assert isinstance(node2, Option)
        assert node1.param == "second"
        assert node2.param == "first"

    def test_type_inference_from_default_value(self) -> None:
        """Test that type is inferred from default value."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("port", default=8080)
        def serve(port: int) -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1
        node = pending[0][1]
        from click_extended.core.decorators.option import Option

        assert isinstance(node, Option)
        assert node.type == int

    def test_decorator_with_all_params(self) -> None:
        """Test decorator with all parameters."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option(
            "port",
            "-p",
            "--port-num",
            type=int,
            help="Port number",
            default=8080,
            tags="network",
        )
        def serve(port: int) -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]
        from click_extended.core.decorators.option import Option

        assert isinstance(node, Option)
        assert node.short_flags == ["-p"]
        assert node.long_flags == ["--port-num"]
        assert node.type == int
        assert node.help == "Port number"
        assert node.default == 8080
        assert node.tags == ["network"]

    def test_flag_decorator(self) -> None:
        """Test boolean flag decorator."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("verbose", is_flag=True)
        def run(verbose: bool) -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]
        from click_extended.core.decorators.option import Option

        assert isinstance(node, Option)
        assert node.is_flag is True
        assert node.default is False  # Option class sets this

    def test_decorator_with_tags_list(self) -> None:
        """Test decorator with list of tags."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("port", tags=["network", "config"])
        def serve(port: int) -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]
        from click_extended.core.decorators.option import Option

        assert isinstance(node, Option)
        assert node.tags == ["network", "config"]

    def test_decorator_function_remains_callable(self) -> None:
        """Test that decorated function remains callable."""
        from click_extended.core.decorators.option import option

        @option("port", type=int)
        def serve(port: int) -> str:
            return f"Serving on port {port}"

        assert callable(serve)

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test that decorator preserves function name and docstring."""
        from click_extended.core.decorators.option import option

        @option("port")
        def serve(port: int) -> None:
            """Start the server."""
            pass

        assert serve.__name__ == "serve"
        assert serve.__doc__ == "Start the server."

    def test_option_class_as_decorator(self) -> None:
        """Test using Option.as_decorator() directly."""
        from click_extended.core.decorators.option import Option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @Option.as_decorator(name="port", type=int)
        def serve(port: int) -> None:
            pass

        pending = Tree.get_pending_nodes()
        assert len(pending) == 1

    def test_multiple_option_with_decorator(self) -> None:
        """Test multiple flag with decorator."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("tag", multiple=True)
        def build(tag: list[str]) -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]
        from click_extended.core.decorators.option import Option

        assert isinstance(node, Option)
        assert node.multiple is True

    def test_nargs_with_decorator(self) -> None:
        """Test nargs parameter with decorator."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("coords", nargs=3, type=float)
        def plot(coords: tuple[float, float, float]) -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]
        from click_extended.core.decorators.option import Option

        assert isinstance(node, Option)
        assert node.nargs == 3

    def test_required_option_decorator(self) -> None:
        """Test required option with decorator."""
        from click_extended.core.decorators.option import option
        from click_extended.core.other._tree import Tree

        Tree._pending_nodes.clear()

        @option("config", required=True)
        def run(config: str) -> None:
            pass

        pending = Tree.get_pending_nodes()
        node = pending[0][1]
        from click_extended.core.decorators.option import Option

        assert isinstance(node, Option)
        assert node.required is True


class TestOptionCommandIntegration:
    """Test Option integration with Click commands."""

    def test_basic_option_value(self, cli_runner: Any) -> None:
        """Test basic option with value."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("name")
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "World"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

    def test_short_flag(self, cli_runner: Any) -> None:
        """Test short flag usage."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("port", "-p", type=int)
        def serve(port: int) -> None:
            click.echo(f"Port: {port}")

        result = cli_runner.invoke(serve, ["-p", "8080"])
        assert result.exit_code == 0
        assert "Port: 8080" in result.output

    def test_boolean_flag(self, cli_runner: Any) -> None:
        """Test boolean flag without value."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("verbose", is_flag=True)
        def run(verbose: bool) -> None:
            if verbose:
                click.echo("Verbose mode enabled")
            else:
                click.echo("Quiet mode")

        result = cli_runner.invoke(run, ["--verbose"])
        assert result.exit_code == 0
        assert "Verbose mode enabled" in result.output

        result = cli_runner.invoke(run, [])
        assert result.exit_code == 0
        assert "Quiet mode" in result.output

    def test_option_type_conversion_int(self, cli_runner: Any) -> None:
        """Test type conversion to int."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("count", type=int, default=1)
        def repeat(count: int) -> None:
            click.echo(f"Count: {count * 2}")

        result = cli_runner.invoke(repeat, ["--count", "5"])
        assert result.exit_code == 0
        assert "Count: 10" in result.output

    def test_option_type_conversion_float(self, cli_runner: Any) -> None:
        """Test type conversion to float."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("price", type=float)
        def show(price: float) -> None:
            click.echo(f"Price: ${price:.2f}")

        result = cli_runner.invoke(show, ["--price", "19.99"])
        assert result.exit_code == 0
        assert "Price: $19.99" in result.output

    def test_option_default_value(self, cli_runner: Any) -> None:
        """Test option with default value when not provided."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("port", type=int, default=8080)
        def serve(port: int) -> None:
            click.echo(f"Port: {port}")

        result = cli_runner.invoke(serve, [])
        assert result.exit_code == 0
        assert "Port: 8080" in result.output

    def test_required_option_missing(self, cli_runner: Any) -> None:
        """Test that missing required option raises error."""
        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("config", required=True)
        def run(config: str) -> None:
            pass

        result = cli_runner.invoke(run, [])
        assert result.exit_code != 0
        assert (
            "required" in result.output.lower()
            or "missing" in result.output.lower()
        )

    def test_required_option_provided(self, cli_runner: Any) -> None:
        """Test required option when provided."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("config", required=True)
        def run(config: str) -> None:
            click.echo(f"Config: {config}")

        result = cli_runner.invoke(run, ["--config", "app.yaml"])
        assert result.exit_code == 0
        assert "Config: app.yaml" in result.output

    def test_multiple_option(self, cli_runner: Any) -> None:
        """Test option with multiple flag."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("tag", multiple=True)
        def build(tag: tuple[str, ...]) -> None:
            for t in tag:
                click.echo(f"Tag: {t}")

        result = cli_runner.invoke(build, ["--tag", "v1.0", "--tag", "latest"])
        assert result.exit_code == 0
        assert "Tag: v1.0" in result.output
        assert "Tag: latest" in result.output

    def test_option_nargs_fixed(self, cli_runner: Any) -> None:
        """Test option with fixed nargs."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("coords", nargs=3, type=int)
        def plot(coords: tuple[int, int, int]) -> None:
            x, y, z = coords
            click.echo(f"Plotting at ({x}, {y}, {z})")

        result = cli_runner.invoke(plot, ["--coords", "10", "20", "30"])
        assert result.exit_code == 0
        assert "Plotting at (10, 20, 30)" in result.output

    def test_multiple_options_same_command(self, cli_runner: Any) -> None:
        """Test multiple different options on same command."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("host", default="localhost")
        @option("port", type=int, default=8080)
        def serve(host: str, port: int) -> None:
            click.echo(f"Serving on {host}:{port}")

        result = cli_runner.invoke(
            serve, ["--host", "0.0.0.0", "--port", "3000"]
        )
        assert result.exit_code == 0
        assert "Serving on 0.0.0.0:3000" in result.output

    def test_option_with_help_text(self, cli_runner: Any) -> None:
        """Test that help text appears in --help output."""
        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("port", type=int, help="Port number for server")
        def serve(port: int) -> None:
            pass

        result = cli_runner.invoke(serve, ["--help"])
        assert result.exit_code == 0
        assert "Port number for server" in result.output

    def test_option_invalid_type_conversion(self, cli_runner: Any) -> None:
        """Test invalid type conversion raises error."""
        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("port", type=int)
        def serve(port: int) -> None:
            pass

        result = cli_runner.invoke(serve, ["--port", "invalid"])
        assert result.exit_code != 0

    def test_option_with_both_short_and_long(self, cli_runner: Any) -> None:
        """Test using both short and long flags."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("verbose", "-v", is_flag=True)
        def run(verbose: bool) -> None:
            if verbose:
                click.echo("Verbose")

        result1 = cli_runner.invoke(run, ["-v"])
        assert result1.exit_code == 0
        assert "Verbose" in result1.output

        result2 = cli_runner.invoke(run, ["--verbose"])
        assert result2.exit_code == 0
        assert "Verbose" in result2.output

    def test_option_override_with_explicit_value(self, cli_runner: Any) -> None:
        """Test that provided value overrides default."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("retries", type=int, default=3)
        def run(retries: int) -> None:
            click.echo(f"Retries: {retries}")

        result = cli_runner.invoke(run, ["--retries", "10"])
        assert result.exit_code == 0
        assert "Retries: 10" in result.output

    def test_flag_default_false(self, cli_runner: Any) -> None:
        """Test that boolean flags default to False."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("debug", is_flag=True)
        def run(debug: bool) -> None:
            click.echo(f"Debug: {debug}")

        result = cli_runner.invoke(run, [])
        assert result.exit_code == 0
        assert "Debug: False" in result.output

    def test_option_with_empty_string_default(self, cli_runner: Any) -> None:
        """Test option with empty string as default."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("prefix", default="")
        def run(prefix: str) -> None:
            click.echo(f"Prefix: '{prefix}'")

        result = cli_runner.invoke(run, [])
        assert result.exit_code == 0
        assert "Prefix: ''" in result.output

    def test_option_with_zero_default(self, cli_runner: Any) -> None:
        """Test option with zero as default value."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("offset", type=int, default=0)
        def run(offset: int) -> None:
            click.echo(f"Offset: {offset}")

        result = cli_runner.invoke(run, [])
        assert result.exit_code == 0
        assert "Offset: 0" in result.output

    def test_option_type_inference_from_default(self, cli_runner: Any) -> None:
        """Test that type is inferred from default value."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option

        @command()
        @option("count", default=5)
        def run(count: int) -> None:
            click.echo(f"Count: {count * 2}")

        result = cli_runner.invoke(run, ["--count", "7"])
        assert result.exit_code == 0
        assert "Count: 14" in result.output


class TestOptionNodeWithChildren:
    """Test OptionNode with child nodes."""

    def test_option_with_single_child(self, cli_runner: Any) -> None:
        """Test option with a single child node."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Uppercase(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.upper()

        @command()
        @option("name")
        @Uppercase.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "world"])
        assert result.exit_code == 0
        assert "Hello, WORLD!" in result.output

    def test_option_with_multiple_children(self, cli_runner: Any) -> None:
        """Test option with multiple child nodes."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Strip(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.strip()

        class Uppercase(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.upper()

        @command()
        @option("name")
        @Strip.as_decorator()
        @Uppercase.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "  world  "])
        assert result.exit_code == 0
        assert "Hello, WORLD!" in result.output

    def test_option_flag_with_child(self, cli_runner: Any) -> None:
        """Test boolean flag with child node."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Negate(ChildNode):
            def handle_bool(
                self, value: bool, context: Context, *args: Any, **kwargs: Any
            ) -> bool:
                return not value

        @command()
        @option("verbose", is_flag=True)
        @Negate.as_decorator()
        def run(verbose: bool) -> None:
            click.echo(f"Quiet: {verbose}")

        result = cli_runner.invoke(run, ["--verbose"])
        assert result.exit_code == 0
        assert "Quiet: False" in result.output

    def test_option_child_execution_order(self, cli_runner: Any) -> None:
        """Test that children execute in correct order."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class AddPrefix(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return f"[{value}]"

        class AddSuffix(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return f"{value}!"

        @command()
        @option("name")
        @AddPrefix.as_decorator()
        @AddSuffix.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Result: {name}")

        result = cli_runner.invoke(greet, ["--name", "test"])
        assert result.exit_code == 0
        # Children execute top-to-bottom: AddPrefix first, then AddSuffix
        assert "Result: [test]!" in result.output

    def test_option_with_child_context_access(self, cli_runner: Any) -> None:
        """Test that children can access context."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class ContextAware(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                # Children should receive context
                assert context is not None
                return value

        @command()
        @option("name")
        @ContextAware.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}")

        result = cli_runner.invoke(greet, ["--name", "test"])
        assert result.exit_code == 0

    def test_option_default_with_child(self, cli_runner: Any) -> None:
        """Test that child processes default values."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Uppercase(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.upper()

        @command()
        @option("name", default="world")
        @Uppercase.as_decorator()
        def greet(name: str) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, [])
        assert result.exit_code == 0
        assert "Hello, WORLD!" in result.output

    def test_option_required_with_child(self, cli_runner: Any) -> None:
        """Test required option with child transformation."""
        import click

        from click_extended.core.decorators.command import command
        from click_extended.core.decorators.option import option
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.other.context import Context

        class Uppercase(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.upper()

        @command()
        @option("config", required=True)
        @Uppercase.as_decorator()
        def run(config: str) -> None:
            click.echo(f"Config: {config}")

        result = cli_runner.invoke(run, ["--config", "app.yaml"])
        assert result.exit_code == 0
        assert "Config: APP.YAML" in result.output


class TestOptionNodeEdgeCases:
    """Test Option edge cases and error handling."""

    def test_is_flag_with_type_int_raises_error(self) -> None:
        """Test that is_flag=True with type=int raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Cannot specify both is_flag"):
            Option(name="count", is_flag=True, type=int)

    def test_is_flag_with_type_str_raises_error(self) -> None:
        """Test that is_flag=True with non-bool type raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Cannot specify both is_flag"):
            Option(name="verbose", is_flag=True, type=str)

    def test_is_flag_with_type_bool_is_valid(self) -> None:
        """Test that is_flag=True with type=bool is allowed."""
        from click_extended.core.decorators.option import Option

        # This should not raise
        opt = Option(name="verbose", is_flag=True, type=bool)
        assert opt.is_flag is True
        assert opt.type == bool

    def test_invalid_long_flag_no_dashes(self) -> None:
        """Test that long flag without dashes raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid flag"):
            Option("port", "port")

    def test_invalid_long_flag_single_dash(self) -> None:
        """Test that long flag with single dash raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid short flag"):
            Option("port", "-port")

    def test_invalid_short_flag_no_dash(self) -> None:
        """Test that short flag without dash raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid flag"):
            Option("port", "p")

    def test_invalid_short_flag_multiple_chars(self) -> None:
        """Test that short flag with multiple chars raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError, match="Invalid short flag"):
            Option("port", "-port")

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError):
            Option(name="")

    def test_name_with_spaces_raises_error(self) -> None:
        """Test that name with spaces raises error."""
        from click_extended.core.decorators.option import Option

        with pytest.raises(ValueError):
            Option(name="my option")

    def test_option_none_vs_empty_string_default(self) -> None:
        """Test distinction between None and empty string default."""
        from click_extended.core.decorators.option import Option

        opt1 = Option(name="test1", default=None)
        opt2 = Option(name="test2", default="")

        assert opt1.default is None
        assert opt2.default == ""

    def test_option_zero_vs_none_default(self) -> None:
        """Test distinction between 0 and None default."""
        from click_extended.core.decorators.option import Option

        opt1 = Option(name="test1", default=0, type=int)
        opt2 = Option(name="test2", default=None)

        assert opt1.default == 0
        assert opt2.default is None
