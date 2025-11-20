"""Tests for the Argument class and argument decorator."""

from unittest.mock import MagicMock, patch

from click_extended.core._parent_node import ParentNode
from click_extended.core.argument import Argument, argument
from click_extended.core.command import command


class TestArgumentInitialization:
    """Tests for Argument initialization."""

    def test_init_with_name_only(self) -> None:
        """Test initialization with just a name."""
        arg = Argument(name="filename")
        assert arg.name == "filename"
        assert arg.nargs == 1
        assert arg.type == str
        assert arg.help is None
        assert arg.required is True
        assert arg.default is None
        assert arg.extra_kwargs == {}

    def test_init_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        arg = Argument(
            name="port",
            nargs=1,
            type=int,
            help="Port number",
            required=False,
            default=8080,
        )
        assert arg.name == "port"
        assert arg.nargs == 1
        assert arg.type is int
        assert arg.help == "Port number"
        assert arg.required is False
        assert arg.default == 8080

    def test_init_with_nargs_multiple(self) -> None:
        """Test initialization with multiple arguments."""
        arg = Argument(name="files", nargs=-1)
        assert arg.name == "files"
        assert arg.nargs == -1

    def test_init_with_nargs_specific_count(self) -> None:
        """Test initialization with specific nargs count."""
        arg = Argument(name="coords", nargs=3)
        assert arg.name == "coords"
        assert arg.nargs == 3

    def test_init_with_type_int(self) -> None:
        """Test initialization with int type."""
        arg = Argument(name="count", type=int)
        assert arg.type is int

    def test_init_with_type_float(self) -> None:
        """Test initialization with float type."""
        arg = Argument(name="value", type=float)
        assert arg.type is float

    def test_init_with_extra_kwargs(self) -> None:
        """Test initialization with extra kwargs."""
        arg = Argument(name="file", custom_param="value", another="param")
        assert arg.extra_kwargs == {"custom_param": "value", "another": "param"}

    def test_init_converts_name_to_snake_case(self) -> None:
        """Test that name is converted to snake_case."""
        arg = Argument(name="file-name")
        assert arg.name == "file_name"

    def test_init_preserves_snake_case_name(self) -> None:
        """Test that snake_case names are preserved."""
        arg = Argument(name="file_name")
        assert arg.name == "file_name"

    def test_init_converts_kebab_to_snake(self) -> None:
        """Test kebab-case to snake_case conversion."""
        arg = Argument(name="output-file")
        assert arg.name == "output_file"

    def test_init_default_required_is_true(self) -> None:
        """Test that required defaults to True for arguments."""
        arg = Argument(name="required_arg")
        assert arg.required is True

    def test_init_with_required_false(self) -> None:
        """Test initialization with required=False."""
        arg = Argument(name="optional_arg", required=False)
        assert arg.required is False

    def test_init_with_default_value(self) -> None:
        """Test initialization with default value."""
        arg = Argument(name="arg", default="default_value")
        assert arg.default == "default_value"


class TestArgumentInheritance:
    """Tests for Argument inheritance."""

    def test_argument_is_parent_node_subclass(self) -> None:
        """Test that Argument is a subclass of ParentNode."""
        assert issubclass(Argument, ParentNode)

    def test_argument_instance_is_parent_node_instance(self) -> None:
        """Test that Argument instances are ParentNode instances."""
        arg = Argument(name="test")
        assert isinstance(arg, ParentNode)

    def test_argument_has_parent_node_attributes(self) -> None:
        """Test that Argument has ParentNode attributes."""
        arg = Argument(name="test")
        assert hasattr(arg, "name")
        assert hasattr(arg, "children")
        assert hasattr(arg, "help")
        assert hasattr(arg, "required")
        assert hasattr(arg, "default")

    def test_argument_has_children_dict(self) -> None:
        """Test that Argument initializes with children dict."""
        arg = Argument(name="test")
        assert arg.children is not None
        assert isinstance(arg.children, dict)
        assert len(arg.children) == 0


class TestArgumentAsDecorator:
    """Tests for Argument.as_decorator method."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_returns_decorator(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that as_decorator returns a decorator function."""
        decorator = Argument.as_decorator(name="test")
        assert callable(decorator)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_creates_argument_instance(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that as_decorator creates an Argument instance."""
        decorator = Argument.as_decorator(name="test")

        def dummy() -> None:
            pass

        decorator(dummy)

        mock_queue.assert_called_once()
        call_args = mock_queue.call_args
        assert call_args is not None
        instance = call_args[0][0]
        assert isinstance(instance, Argument)
        assert instance.name == "test"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_with_all_params(self, mock_queue: MagicMock) -> None:
        """Test as_decorator with all parameters."""
        decorator = Argument.as_decorator(
            name="port",
            nargs=1,
            type=int,
            help="Port number",
            required=False,
            default=8080,
        )

        def dummy() -> None:
            pass

        decorator(dummy)

        instance = mock_queue.call_args[0][0]  # type: ignore
        assert instance.name == "port"
        assert instance.nargs == 1
        assert instance.type is int
        assert instance.help == "Port number"
        assert instance.required is False
        assert instance.default == 8080

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_queues_parent(self, mock_queue: MagicMock) -> None:
        """Test that as_decorator queues the parent node."""
        decorator = Argument.as_decorator(name="test")

        def dummy() -> None:
            pass

        decorator(dummy)

        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_preserves_function(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that as_decorator preserves the wrapped function."""
        decorator = Argument.as_decorator(name="test")

        def dummy() -> str:
            return "result"

        result = decorator(dummy)
        assert callable(result)
        assert result() == "result"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_with_async_function(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator with async function."""
        decorator = Argument.as_decorator(name="test")

        async def dummy() -> str:
            return "async_result"

        result = decorator(dummy)
        assert callable(result)


class TestArgumentDecoratorFunction:
    """Tests for the argument() decorator function."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_argument_decorator_with_name_only(
        self, mock_queue: MagicMock
    ) -> None:
        """Test argument decorator with just name."""

        @argument("filename")
        def test_func(filename: str) -> str:
            return filename

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_argument_decorator_with_all_params(
        self, mock_queue: MagicMock
    ) -> None:
        """Test argument decorator with all parameters."""

        @argument(
            "port",
            nargs=1,
            type=int,
            help="Port number",
            required=False,
            default=8080,
        )
        def test_func(port: int) -> int:  # type: ignore
            return port

        instance = mock_queue.call_args[0][0]  # type: ignore
        assert instance.name == "port"
        assert instance.nargs == 1
        assert instance.type is int
        assert instance.help == "Port number"
        assert instance.required is False
        assert instance.default == 8080

    @patch("click_extended.core._parent_node.queue_parent")
    def test_argument_decorator_with_nargs_unlimited(
        self, mock_queue: MagicMock
    ) -> None:
        """Test argument decorator with unlimited nargs."""

        @argument("files", nargs=-1)
        def test_func(files: list[str]) -> list[str]:  # type: ignore
            return files

        instance = mock_queue.call_args[0][0]  # type: ignore
        assert instance.nargs == -1

    @patch("click_extended.core._parent_node.queue_parent")
    def test_argument_decorator_with_type_int(
        self, mock_queue: MagicMock
    ) -> None:
        """Test argument decorator with int type."""

        @argument("count", type=int)
        def test_func(count: int) -> int:  # type: ignore
            return count

        instance = mock_queue.call_args[0][0]  # type: ignore
        assert instance.type is int

    @patch("click_extended.core._parent_node.queue_parent")
    def test_argument_decorator_with_help(self, mock_queue: MagicMock) -> None:
        """Test argument decorator with help text."""

        @argument("file", help="Input file path")
        def test_func(file: str) -> str:  # type: ignore
            return file

        instance = mock_queue.call_args[0][0]  # type: ignore
        assert instance.help == "Input file path"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_argument_decorator_with_extra_kwargs(
        self, mock_queue: MagicMock
    ) -> None:
        """Test argument decorator with extra kwargs."""

        @argument("file", custom="value")
        def test_func(file: str) -> str:  # type: ignore
            return file

        instance = mock_queue.call_args[0][0]  # type: ignore
        assert instance.extra_kwargs == {"custom": "value"}

    @patch("click_extended.core._parent_node.queue_parent")
    def test_argument_decorator_returns_callable(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that argument decorator returns a callable."""

        @argument("test")
        def test_func() -> str:
            return "result"

        assert callable(test_func)
        assert test_func() == "result"


class TestArgumentNameTransformation:
    """Tests for argument name transformation."""

    def test_kebab_case_to_snake_case(self) -> None:
        """Test kebab-case name conversion."""
        arg = Argument(name="input-file")
        assert arg.name == "input_file"

    def test_multiple_hyphens(self) -> None:
        """Test name with multiple hyphens."""
        arg = Argument(name="my-input-file-name")
        assert arg.name == "my_input_file_name"

    def test_already_snake_case(self) -> None:
        """Test that snake_case is preserved."""
        arg = Argument(name="input_file")
        assert arg.name == "input_file"

    def test_single_word(self) -> None:
        """Test single word name."""
        arg = Argument(name="file")
        assert arg.name == "file"

    def test_uppercase_converted(self) -> None:
        """Test uppercase name conversion."""
        arg = Argument(name="FILE")
        assert arg.name == "file"

    def test_mixed_case_converted(self) -> None:
        """Test mixed case name conversion."""
        arg = Argument(name="InputFile")
        assert arg.name == "input_file"


class TestArgumentNargs:
    """Tests for nargs parameter."""

    def test_nargs_default_is_one(self) -> None:
        """Test that nargs defaults to 1."""
        arg = Argument(name="test")
        assert arg.nargs == 1

    def test_nargs_can_be_zero(self) -> None:
        """Test that nargs can be 0."""
        arg = Argument(name="test", nargs=0)
        assert arg.nargs == 0

    def test_nargs_can_be_multiple(self) -> None:
        """Test that nargs can be multiple values."""
        arg = Argument(name="test", nargs=3)
        assert arg.nargs == 3

    def test_nargs_unlimited(self) -> None:
        """Test that nargs can be -1 for unlimited."""
        arg = Argument(name="test", nargs=-1)
        assert arg.nargs == -1

    def test_nargs_large_number(self) -> None:
        """Test that nargs can be a large number."""
        arg = Argument(name="test", nargs=100)
        assert arg.nargs == 100


class TestArgumentType:
    """Tests for type parameter."""

    def test_type_defaults_to_str(self) -> None:
        """Test that type defaults to str when no default provided."""
        arg = Argument(name="test")
        assert arg.type == str

    def test_type_inferred_from_default(self) -> None:
        """Test that type is inferred from default value."""
        arg_int = Argument(name="test", default=42)
        assert arg_int.type == int

        arg_float = Argument(name="test", default=3.14)
        assert arg_float.type == float

        arg_str = Argument(name="test", default="hello")
        assert arg_str.type == str

    def test_type_can_be_int(self) -> None:
        """Test that type can be int."""
        arg = Argument(name="test", type=int)
        assert arg.type is int

    def test_type_can_be_str(self) -> None:
        """Test that type can be str."""
        arg = Argument(name="test", type=str)
        assert arg.type is str

    def test_type_can_be_float(self) -> None:
        """Test that type can be float."""
        arg = Argument(name="test", type=float)
        assert arg.type is float

    def test_type_can_be_bool(self) -> None:
        """Test that type can be bool."""
        arg = Argument(name="test", type=bool)
        assert arg.type is bool

    def test_type_can_be_custom_class(self) -> None:
        """Test that type can be a custom class."""

        class CustomType:
            pass

        arg = Argument(name="test", type=CustomType)
        assert arg.type is CustomType


class TestArgumentTypeInference:
    """Tests for argument type inference from default values."""

    def test_type_defaults_to_str_when_no_type_or_default(self) -> None:
        """Test that type defaults to str when neither type nor default provided."""
        arg = Argument(name="filename")
        assert arg.type == str

    def test_type_inferred_as_int_from_int_default(self) -> None:
        """Test that type is inferred as int from int default."""
        arg = Argument(name="port", default=8080)
        assert arg.type == int

    def test_type_inferred_as_float_from_float_default(self) -> None:
        """Test that type is inferred as float from float default."""
        arg = Argument(name="ratio", default=2.5)
        assert arg.type == float

    def test_type_inferred_as_str_from_str_default(self) -> None:
        """Test that type is inferred as str from str default."""
        arg = Argument(name="name", default="default")
        assert arg.type == str

    def test_type_inferred_as_bool_from_bool_default(self) -> None:
        """Test that type is inferred as bool from bool default."""
        arg = Argument(name="flag", default=False)
        assert arg.type == bool

    def test_type_inferred_as_list_from_list_default(self) -> None:
        """Test that type is inferred as list from list default."""
        arg = Argument(name="items", default=[1, 2, 3])
        assert arg.type == list

    def test_type_inferred_as_tuple_from_tuple_default(self) -> None:
        """Test that type is inferred as tuple from tuple default."""
        arg = Argument(name="coords", default=(0, 0))
        assert arg.type == tuple

    def test_explicit_type_overrides_inference(self) -> None:
        """Test that explicit type overrides type inference from default."""
        arg = Argument(name="value", type=str, default=42)
        assert arg.type == str
        assert arg.default == 42

    def test_explicit_float_type_with_int_default(self) -> None:
        """Test explicit float type with int default."""
        arg = Argument(name="ratio", type=float, default=5)
        assert arg.type == float
        assert arg.default == 5

    def test_type_inference_with_none_default(self) -> None:
        """Test that type defaults to str when default is None."""
        arg = Argument(name="value", default=None)
        assert arg.type == str

    def test_type_inference_with_zero_default(self) -> None:
        """Test that type is inferred correctly from zero values."""
        arg_int = Argument(name="count", default=0)
        assert arg_int.type == int

        arg_float = Argument(name="ratio", default=0.0)
        assert arg_float.type == float

    def test_type_inference_with_empty_string_default(self) -> None:
        """Test that type is inferred as str from empty string default."""
        arg = Argument(name="name", default="")
        assert arg.type == str

    def test_type_inference_with_nargs(self) -> None:
        """Test that type inference works with nargs parameter."""
        arg = Argument(name="ports", nargs=-1, default=8080)
        assert arg.type == int
        assert arg.nargs == -1

    def test_type_inference_preserved_with_other_params(self) -> None:
        """Test that type inference works with other parameters."""
        arg = Argument(
            name="port", default=3000, help="Server port", required=False
        )
        assert arg.type == int
        assert arg.default == 3000
        assert arg.required is False


class TestArgumentRequired:
    """Tests for required parameter."""

    def test_required_defaults_to_true(self) -> None:
        """Test that required defaults to True."""
        arg = Argument(name="test")
        assert arg.required is True

    def test_required_can_be_false(self) -> None:
        """Test that required can be False."""
        arg = Argument(name="test", required=False)
        assert arg.required is False

    def test_required_can_be_explicitly_true(self) -> None:
        """Test that required can be explicitly True."""
        arg = Argument(name="test", required=True)
        assert arg.required is True


class TestArgumentDefault:
    """Tests for default parameter."""

    def test_default_is_none(self) -> None:
        """Test that default is None by default."""
        arg = Argument(name="test")
        assert arg.default is None

    def test_default_can_be_string(self) -> None:
        """Test that default can be a string."""
        arg = Argument(name="test", default="default_value")
        assert arg.default == "default_value"

    def test_default_can_be_int(self) -> None:
        """Test that default can be an int."""
        arg = Argument(name="test", default=42)
        assert arg.default == 42

    def test_default_can_be_list(self) -> None:
        """Test that default can be a list."""
        arg = Argument(name="test", default=["a", "b", "c"])
        assert arg.default == ["a", "b", "c"]

    def test_default_can_be_dict(self) -> None:
        """Test that default can be a dict."""
        arg = Argument(name="test", default={"key": "value"})
        assert arg.default == {"key": "value"}

    def test_default_makes_argument_optional(self) -> None:
        """Test that default automatically makes argument optional."""
        arg = Argument(name="test", default="default")
        assert arg.required is False
        assert arg.default == "default"

    def test_default_with_explicit_required_false(self) -> None:
        """Test default with explicit required=False still works."""
        arg = Argument(name="test", required=False, default="default")
        assert arg.required is False
        assert arg.default == "default"


class TestArgumentDefaultBehavior:
    """Tests for default value auto-optional behavior."""

    def test_default_string_makes_optional(self) -> None:
        """Test that string default makes argument optional."""
        arg = Argument(name="test", default="value")
        assert arg.required is False

    def test_default_int_makes_optional(self) -> None:
        """Test that int default makes argument optional."""
        arg = Argument(name="test", default=42)
        assert arg.required is False

    def test_default_zero_makes_optional(self) -> None:
        """Test that default=0 makes argument optional."""
        arg = Argument(name="test", default=0)
        assert arg.required is False

    def test_default_empty_string_makes_optional(self) -> None:
        """Test that default='' makes argument optional."""
        arg = Argument(name="test", default="")
        assert arg.required is False

    def test_default_false_makes_optional(self) -> None:
        """Test that default=False makes argument optional."""
        arg = Argument(name="test", default=False)
        assert arg.required is False

    def test_default_empty_list_makes_optional(self) -> None:
        """Test that default=[] makes argument optional."""
        arg = Argument(name="test", default=[])
        assert arg.required is False

    def test_no_default_stays_required(self) -> None:
        """Test that no default keeps argument required."""
        arg = Argument(name="test")
        assert arg.required is True

    def test_default_none_makes_optional(self) -> None:
        """Test that explicitly passing default=None makes argument optional."""
        arg = Argument(name="test", default=None)
        assert arg.required is False
        assert arg.default is None


class TestArgumentRequiredOptionalBehavior:
    """Tests for required/optional argument behavior with Click integration."""

    def test_required_argument_without_default(self) -> None:
        """Test that argument without default is required by Click."""
        from click.testing import CliRunner

        @command()
        @argument("value", type=int)
        def test_cmd(value: int) -> None:
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, [])  # type: ignore

        assert result.exit_code == 2
        assert (
            "Error (value):" in result.output
            or "Error (VALUE):" in result.output
        )

    def test_required_argument_with_value_works(self) -> None:
        """Test that required argument works when value is provided."""
        from click.testing import CliRunner

        @command()
        @argument("value", type=int)
        def test_cmd(value: int) -> None:
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["42"])  # type: ignore

        assert result.exit_code == 0
        assert "Value: 42" in result.output

    def test_optional_argument_with_none_default(self) -> None:
        """Test that default=None makes argument optional."""
        from click.testing import CliRunner

        @command()
        @argument("value", type=int, default=None)
        def test_cmd(value: int | None) -> None:
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, [])  # type: ignore

        assert result.exit_code == 0
        assert "Value: None" in result.output

    def test_optional_argument_with_value_default(self) -> None:
        """Test that argument with default value is optional."""
        from click.testing import CliRunner

        @command()
        @argument("port", type=int, default=8080)
        def test_cmd(port: int) -> None:
            print(f"Port: {port}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, [])  # type: ignore

        assert result.exit_code == 0
        assert "Port: 8080" in result.output

    def test_explicit_required_false_makes_optional(self) -> None:
        """Test that explicit required=False makes argument optional."""
        from click.testing import CliRunner

        @command()
        @argument("value", type=int, required=False)
        def test_cmd(value: int | None) -> None:
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, [])  # type: ignore

        assert result.exit_code == 0
        assert "Value: None" in result.output

    def test_optional_argument_can_be_overridden(self) -> None:
        """Test that optional argument can be provided a value."""
        from click.testing import CliRunner

        @command()
        @argument("value", type=int, default=10)
        def test_cmd(value: int) -> None:
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["99"])  # type: ignore

        assert result.exit_code == 0
        assert "Value: 99" in result.output

    def test_multiple_required_arguments(self) -> None:
        """Test that multiple required arguments work correctly."""
        from click.testing import CliRunner

        @command()
        @argument("first", type=int)
        @argument("second", type=int)
        def test_cmd(first: int, second: int) -> None:
            print(f"Values: {first}, {second}")

        runner = CliRunner()

        # Missing both
        result = runner.invoke(test_cmd, [])  # type: ignore
        assert result.exit_code == 2
        assert (
            "Error (first):" in result.output
            or "Error (FIRST):" in result.output
        )

        # With both values
        result = runner.invoke(test_cmd, ["1", "2"])  # type: ignore
        assert result.exit_code == 0
        assert "Values: 1, 2" in result.output

    def test_mixed_required_and_optional_arguments(self) -> None:
        """Test mixing required and optional arguments."""
        from click.testing import CliRunner

        @command()
        @argument("required_arg", type=int)
        @argument("optional_arg", type=int, default=100)
        def test_cmd(required_arg: int, optional_arg: int) -> None:
            print(f"Required: {required_arg}, Optional: {optional_arg}")

        runner = CliRunner()

        # Only required
        result = runner.invoke(test_cmd, ["50"])  # type: ignore
        assert result.exit_code == 0
        assert "Required: 50, Optional: 100" in result.output

        # Both provided
        result = runner.invoke(test_cmd, ["50", "200"])  # type: ignore
        assert result.exit_code == 0
        assert "Required: 50, Optional: 200" in result.output

    def test_argument_with_none_default_accepts_none(self) -> None:
        """Test that argument with default=None properly receives None."""
        from click.testing import CliRunner

        received_value = []

        @command()
        @argument("value", type=str, default=None)
        def test_cmd(value: str | None) -> None:
            received_value.append(value)  # type: ignore
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, [])  # type: ignore

        assert result.exit_code == 0
        assert received_value[0] is None

    def test_sentinel_value_not_exposed(self) -> None:
        """Test that the sentinel value is converted to None internally."""
        arg = Argument(name="test")
        # Should be None, not the sentinel
        assert arg.default is None
        assert arg.required is True


class TestArgumentExtraKwargs:
    """Tests for extra kwargs parameter."""

    def test_extra_kwargs_empty_by_default(self) -> None:
        """Test that extra_kwargs is empty by default."""
        arg = Argument(name="test")
        assert arg.extra_kwargs == {}

    def test_extra_kwargs_stores_additional_params(self) -> None:
        """Test that extra_kwargs stores additional parameters."""
        arg = Argument(name="test", custom="value", another=123)
        assert arg.extra_kwargs == {"custom": "value", "another": 123}

    def test_extra_kwargs_does_not_include_known_params(self) -> None:
        """Test that known parameters are not in extra_kwargs."""
        arg = Argument(
            name="test",
            nargs=2,
            type=int,
            help="Help",
            required=False,
            default=0,
            custom="value",
        )
        assert arg.extra_kwargs == {"custom": "value"}
        assert "name" not in arg.extra_kwargs
        assert "nargs" not in arg.extra_kwargs
        assert "type" not in arg.extra_kwargs
        assert "help" not in arg.extra_kwargs
        assert "required" not in arg.extra_kwargs
        assert "default" not in arg.extra_kwargs

    def test_extra_kwargs_multiple_values(self) -> None:
        """Test extra_kwargs with multiple values."""
        arg = Argument(name="test", param1="a", param2="b", param3="c")
        assert len(arg.extra_kwargs) == 3
        assert arg.extra_kwargs["param1"] == "a"
        assert arg.extra_kwargs["param2"] == "b"
        assert arg.extra_kwargs["param3"] == "c"


class TestArgumentEdgeCases:
    """Tests for Argument edge cases."""

    def test_empty_name_converted_to_snake_case(self) -> None:
        """Test that empty name is handled."""
        arg = Argument(name="")
        assert arg.name == ""

    def test_name_with_numbers(self) -> None:
        """Test name with numbers."""
        arg = Argument(name="file123")
        assert arg.name == "file123"

    def test_name_with_numbers_and_hyphens(self) -> None:
        """Test name with numbers and hyphens."""
        arg = Argument(name="file-123-name")
        assert arg.name == "file_123_name"

    def test_help_empty_string(self) -> None:
        """Test help as empty string."""
        arg = Argument(name="test", help="")
        assert arg.help == ""

    def test_nargs_negative_other_than_minus_one(self) -> None:
        """Test nargs with negative value other than -1."""
        arg = Argument(name="test", nargs=-5)
        assert arg.nargs == -5

    def test_multiple_arguments_independent(self) -> None:
        """Test that multiple Argument instances are independent."""
        arg1 = Argument(name="arg1", default="default1")
        arg2 = Argument(name="arg2", default="default2")

        assert arg1.name == "arg1"
        assert arg2.name == "arg2"
        assert arg1.default == "default1"
        assert arg2.default == "default2"
        assert arg1 is not arg2

    @patch("click_extended.core._parent_node.queue_parent")
    def test_decorator_can_be_reused(self, mock_queue: MagicMock) -> None:
        """Test that a decorator can be applied to multiple functions."""
        decorator = argument("test")

        @decorator
        def func1() -> str:
            return "func1"

        @decorator
        def func2() -> str:
            return "func2"

        assert func1() == "func1"
        assert func2() == "func2"
        assert mock_queue.call_count == 2

    def test_argument_preserves_parent_node_get_value(self) -> None:
        """Test that Argument has get_value method from ParentNode."""
        arg = Argument(name="test")
        assert hasattr(arg, "get_value")
        assert callable(arg.get_value)

    def test_argument_children_initially_empty(self) -> None:
        """Test that Argument children dict is initially empty."""
        arg = Argument(name="test")
        assert arg.children is not None
        assert len(arg.children) == 0

    def test_type_preserved_exactly(self) -> None:
        """Test that type parameter is preserved exactly."""

        class MyType:
            pass

        arg = Argument(name="test", type=MyType)
        assert arg.type is MyType
        assert arg.type.__name__ == "MyType"
