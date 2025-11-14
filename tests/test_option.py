"""Tests for the Option class."""

from unittest.mock import MagicMock, patch

from click_extended.core._parent_node import ParentNode
from click_extended.core.option import Option, option


class TestOptionInitialization:
    """Test Option class initialization."""

    def test_init_with_long_flag_only(self) -> None:
        """Test initializing Option with long flag only."""
        opt = Option(long="--port")
        assert opt.long == "--port"
        assert opt.name == "port"
        assert opt.short is None
        assert opt.is_flag is False
        assert opt.type is None
        assert opt.multiple is False
        assert opt.help is None
        assert opt.required is False
        assert opt.default is None

    def test_init_with_all_parameters(self) -> None:
        """Test initializing Option with all parameters."""
        opt = Option(
            long="--port",
            short="-p",
            is_flag=False,
            type=int,
            multiple=False,
            help="Port number",
            required=True,
            default=8080,
        )
        assert opt.long == "--port"
        assert opt.short == "-p"
        assert opt.is_flag is False
        assert opt.type == int
        assert opt.multiple is False
        assert opt.help == "Port number"
        assert opt.required is True
        assert opt.default == 8080
        assert opt.name == "port"

    def test_init_extracts_name_from_long_flag(self) -> None:
        """Test that name is extracted from long flag."""
        opt = Option(long="--config-file")
        assert opt.name == "config_file"

    def test_init_with_short_flag(self) -> None:
        """Test initializing with short flag."""
        opt = Option(long="--verbose", short="-v")
        assert opt.short == "-v"

    def test_init_with_is_flag_true(self) -> None:
        """Test initializing with is_flag=True."""
        opt = Option(long="--verbose", is_flag=True)
        assert opt.is_flag is True

    def test_init_with_type_int(self) -> None:
        """Test initializing with type=int."""
        opt = Option(long="--port", type=int)
        assert opt.type == int

    def test_init_with_multiple_true(self) -> None:
        """Test initializing with multiple=True."""
        opt = Option(long="--tag", multiple=True)
        assert opt.multiple is True

    def test_init_with_extra_kwargs(self) -> None:
        """Test initializing with extra kwargs."""
        opt = Option(long="--port", custom_param="value")
        assert opt.extra_kwargs == {"custom_param": "value"}

    def test_init_children_initialized_as_empty_dict(self) -> None:
        """Test that children dict is initialized empty."""
        opt = Option(long="--port")
        assert opt.children == {}
        assert isinstance(opt.children, dict)


class TestOptionValidation:
    """Test Option flag validation."""

    def test_valid_long_flag_simple(self) -> None:
        """Test valid simple long flag."""
        opt = Option(long="--port")
        assert opt.long == "--port"

    def test_valid_long_flag_with_hyphens(self) -> None:
        """Test valid long flag with hyphens."""
        opt = Option(long="--config-file")
        assert opt.long == "--config-file"

    def test_valid_long_flag_with_numbers(self) -> None:
        """Test valid long flag with numbers."""
        opt = Option(long="--timeout-30")
        assert opt.long == "--timeout-30"

    def test_invalid_long_flag_no_prefix(self) -> None:
        """Test invalid long flag without -- prefix."""
        try:
            Option(long="port")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid long flag" in str(e)
            assert "port" in str(e)

    def test_invalid_long_flag_single_dash(self) -> None:
        """Test invalid long flag with single dash."""
        try:
            Option(long="-port")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid long flag" in str(e)

    def test_invalid_long_flag_uppercase(self) -> None:
        """Test invalid long flag with uppercase letters."""
        try:
            Option(long="--Port")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid long flag" in str(e)

    def test_invalid_long_flag_starts_with_number(self) -> None:
        """Test invalid long flag starting with number."""
        try:
            Option(long="--3port")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid long flag" in str(e)

    def test_valid_short_flag_lowercase(self) -> None:
        """Test valid short flag with lowercase letter."""
        opt = Option(long="--port", short="-p")
        assert opt.short == "-p"

    def test_valid_short_flag_uppercase(self) -> None:
        """Test valid short flag with uppercase letter."""
        opt = Option(long="--port", short="-P")
        assert opt.short == "-P"

    def test_invalid_short_flag_no_dash(self) -> None:
        """Test invalid short flag without dash."""
        try:
            Option(long="--port", short="p")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid short flag" in str(e)
            assert "p" in str(e)

    def test_invalid_short_flag_double_dash(self) -> None:
        """Test invalid short flag with double dash."""
        try:
            Option(long="--port", short="--p")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid short flag" in str(e)

    def test_invalid_short_flag_multiple_chars(self) -> None:
        """Test invalid short flag with multiple characters."""
        try:
            Option(long="--port", short="-po")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid short flag" in str(e)

    def test_invalid_short_flag_number(self) -> None:
        """Test invalid short flag with number."""
        try:
            Option(long="--port", short="-1")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid short flag" in str(e)


class TestOptionNameTransformation:
    """Test Option name transformation from long flag."""

    def test_simple_name(self) -> None:
        """Test simple name extraction."""
        opt = Option(long="--port")
        assert opt.name == "port"

    def test_hyphenated_name(self) -> None:
        """Test hyphenated name converted to snake_case."""
        opt = Option(long="--config-file")
        assert opt.name == "config_file"

    def test_multiple_hyphens(self) -> None:
        """Test multiple hyphens converted to underscores."""
        opt = Option(long="--database-connection-string")
        assert opt.name == "database_connection_string"

    def test_name_with_numbers(self) -> None:
        """Test name with numbers."""
        opt = Option(long="--timeout-30")
        assert opt.name == "timeout_30"

    def test_single_letter_name(self) -> None:
        """Test single letter name."""
        opt = Option(long="--v")
        assert opt.name == "v"


class TestOptionInheritance:
    """Test Option class inheritance."""

    def test_option_is_parent_node_subclass(self) -> None:
        """Test that Option is a ParentNode subclass."""
        assert issubclass(Option, ParentNode)

    def test_option_instance_is_parent_node_instance(self) -> None:
        """Test that Option instance is a ParentNode instance."""
        opt = Option(long="--port")
        assert isinstance(opt, ParentNode)

    def test_option_has_parent_node_attributes(self) -> None:
        """Test that Option has ParentNode attributes."""
        opt = Option(long="--port", help="Help", required=True)
        assert hasattr(opt, "name")
        assert hasattr(opt, "help")
        assert hasattr(opt, "required")
        assert hasattr(opt, "default")
        assert hasattr(opt, "children")

    def test_option_has_children_dict(self) -> None:
        """Test that Option has children dict from ParentNode."""
        opt = Option(long="--port")
        assert hasattr(opt, "children")
        assert isinstance(opt.children, dict)


class TestOptionAsDecorator:
    """Test Option.as_decorator functionality."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_returns_decorator(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator returns a decorator function."""
        decorator = Option.as_decorator(long="--port")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_creates_option_instance(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator creates Option instance."""
        decorator = Option.as_decorator(long="--port")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        assert isinstance(args[0], Option)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_with_all_params(self, mock_queue: MagicMock) -> None:
        """Test as_decorator with all parameters."""
        decorator = Option.as_decorator(
            long="--port",
            short="-p",
            type=int,
            help="Port number",
            required=True,
            default=8080,
        )

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_queues_parent(self, mock_queue: MagicMock) -> None:
        """Test as_decorator queues parent node."""
        decorator = Option.as_decorator(long="--port")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_preserves_function(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator preserves function behavior."""
        decorator = Option.as_decorator(long="--port")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)
        assert result() == "test"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_with_async_function(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator with async function."""
        decorator = Option.as_decorator(long="--port")

        async def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)


class TestOptionDecoratorFunction:
    """Test the option() decorator function."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_long_only(
        self, mock_queue: MagicMock
    ) -> None:
        """Test option decorator with long flag only."""

        @option("--port")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_short_flag(
        self, mock_queue: MagicMock
    ) -> None:
        """Test option decorator with short flag."""

        @option("--port", short="-p")
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        opt_instance = args[0]
        assert opt_instance.short == "-p"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_is_flag(self, mock_queue: MagicMock) -> None:
        """Test option decorator with is_flag parameter."""

        @option("--verbose", is_flag=True)
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        opt_instance = args[0]
        assert opt_instance.is_flag is True

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_type(self, mock_queue: MagicMock) -> None:
        """Test option decorator with type parameter."""

        @option("--port", type=int)
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        opt_instance = args[0]
        assert opt_instance.type == int

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_multiple(
        self, mock_queue: MagicMock
    ) -> None:
        """Test option decorator with multiple parameter."""

        @option("--tag", multiple=True)
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        opt_instance = args[0]
        assert opt_instance.multiple is True

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_help(self, mock_queue: MagicMock) -> None:
        """Test option decorator with help parameter."""

        @option("--port", help="Port number")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_required(
        self, mock_queue: MagicMock
    ) -> None:
        """Test option decorator with required parameter."""

        @option("--port", required=True)
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        opt_instance = args[0]
        assert opt_instance.required is True

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_default(self, mock_queue: MagicMock) -> None:
        """Test option decorator with default parameter."""

        @option("--port", default=8080)
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        opt_instance = args[0]
        assert opt_instance.default == 8080

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_all_params(
        self, mock_queue: MagicMock
    ) -> None:
        """Test option decorator with all parameters."""

        @option(
            "--port",
            short="-p",
            is_flag=False,
            type=int,
            multiple=False,
            help="Port number",
            required=True,
            default=8080,
        )
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_with_extra_kwargs(
        self, mock_queue: MagicMock
    ) -> None:
        """Test option decorator with extra kwargs."""

        @option("--port", custom_param="custom_value")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_returns_callable(
        self, mock_queue: MagicMock
    ) -> None:
        """Test option decorator returns callable."""

        @option("--port")
        def test_func() -> str:
            return "test"

        assert callable(test_func)


class TestOptionTypes:
    """Test Option with different types."""

    def test_option_with_int_type(self) -> None:
        """Test option with int type."""
        opt = Option(long="--port", type=int)
        assert opt.type == int

    def test_option_with_str_type(self) -> None:
        """Test option with str type."""
        opt = Option(long="--name", type=str)
        assert opt.type == str

    def test_option_with_float_type(self) -> None:
        """Test option with float type."""
        opt = Option(long="--ratio", type=float)
        assert opt.type == float

    def test_option_with_bool_type(self) -> None:
        """Test option with bool type."""
        opt = Option(long="--enabled", type=bool)
        assert opt.type == bool

    def test_option_with_custom_class_type(self) -> None:
        """Test option with custom class type."""

        class CustomType:
            pass

        opt = Option(long="--custom", type=CustomType)
        assert opt.type == CustomType


class TestOptionFlags:
    """Test Option flag behavior."""

    def test_is_flag_false_by_default(self) -> None:
        """Test is_flag defaults to False."""
        opt = Option(long="--port")
        assert opt.is_flag is False

    def test_is_flag_true(self) -> None:
        """Test is_flag can be set to True."""
        opt = Option(long="--verbose", is_flag=True)
        assert opt.is_flag is True

    def test_flag_with_short_option(self) -> None:
        """Test flag with short option."""
        opt = Option(long="--verbose", short="-v", is_flag=True)
        assert opt.is_flag is True
        assert opt.short == "-v"

    def test_flag_default_is_false_when_not_set(self) -> None:
        """Test that flags default to False when is_flag=True and no default provided."""
        opt = Option(long="--verbose", is_flag=True)
        assert opt.default is False

    def test_flag_default_can_be_overridden(self) -> None:
        """Test that flag default can be explicitly set."""
        opt = Option(long="--verbose", is_flag=True, default=True)
        assert opt.default is True

    def test_non_flag_default_remains_none(self) -> None:
        """Test that non-flag options keep None as default."""
        opt = Option(long="--port")
        assert opt.default is None


class TestOptionMultiple:
    """Test Option multiple values behavior."""

    def test_multiple_false_by_default(self) -> None:
        """Test multiple defaults to False."""
        opt = Option(long="--tag")
        assert opt.multiple is False

    def test_multiple_true(self) -> None:
        """Test multiple can be set to True."""
        opt = Option(long="--tag", multiple=True)
        assert opt.multiple is True

    def test_multiple_with_type(self) -> None:
        """Test multiple with type parameter."""
        opt = Option(long="--tag", multiple=True, type=str)
        assert opt.multiple is True
        assert opt.type == str


class TestOptionEdgeCases:
    """Test Option edge cases."""

    def test_option_with_single_letter_long_flag(self) -> None:
        """Test option with single letter long flag."""
        opt = Option(long="--v")
        assert opt.long == "--v"
        assert opt.name == "v"

    def test_option_with_tags_string(self) -> None:
        """Test option with single string tag."""
        opt = Option(long="--port", tags="api-config")
        assert opt.tags == ["api-config"]

    def test_option_with_tags_list(self) -> None:
        """Test option with list of tags."""
        opt = Option(long="--port", tags=["api-config", "server"])
        assert opt.tags == ["api-config", "server"]

    def test_option_with_no_tags(self) -> None:
        """Test option without tags defaults to empty list."""
        opt = Option(long="--port")
        assert opt.tags == []

    def test_option_with_tags_and_other_params(self) -> None:
        """Test option with tags and other parameters."""
        opt = Option(
            long="--api-key",
            short="-k",
            tags="auth",
            required=True,
            help="API key for authentication",
        )
        assert opt.tags == ["auth"]
        assert opt.short == "-k"
        assert opt.required is True
        assert opt.help == "API key for authentication"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_multiple_option_decorators_independent(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that multiple option decorators are independent."""

        @option("--port")
        def func1() -> str:
            return "test1"

        @option("--host")
        def func2() -> str:
            return "test2"

        assert callable(func1)
        assert callable(func2)
        assert mock_queue.call_count == 2

    def test_default_can_be_any_type(self) -> None:
        """Test that default can be any type."""
        opt1 = Option(long="--name", default="string")
        opt2 = Option(long="--port", default=42)
        opt3 = Option(long="--tags", default=[1, 2, 3])
        opt4 = Option(long="--config", default={"key": "value"})

        assert opt1.default == "string"
        assert opt2.default == 42
        assert opt3.default == [1, 2, 3]
        assert opt4.default == {"key": "value"}

    def test_help_can_be_empty_string(self) -> None:
        """Test that help can be empty string."""
        opt = Option(long="--port", help="")
        assert opt.help == ""

    def test_required_and_default_both_set(self) -> None:
        """Test that both required and default can be set."""
        opt = Option(long="--port", required=True, default=8080)
        assert opt.required is True
        assert opt.default == 8080

    def test_extra_kwargs_empty_by_default(self) -> None:
        """Test that extra_kwargs is empty by default."""
        opt = Option(long="--port")
        assert opt.extra_kwargs == {}

    def test_extra_kwargs_stores_additional_params(self) -> None:
        """Test that extra_kwargs stores additional parameters."""
        opt = Option(long="--port", custom1="value1", custom2="value2")
        assert opt.extra_kwargs == {"custom1": "value1", "custom2": "value2"}

    def test_extra_kwargs_does_not_include_known_params(self) -> None:
        """Test that extra_kwargs doesn't include known parameters."""
        opt = Option(
            long="--port",
            short="-p",
            help="Help",
            custom="value",
        )
        assert "long" not in opt.extra_kwargs
        assert "short" not in opt.extra_kwargs
        assert "help" not in opt.extra_kwargs
        assert opt.extra_kwargs == {"custom": "value"}

    @patch("click_extended.core._parent_node.queue_parent")
    def test_decorator_can_be_reused(self, mock_queue: MagicMock) -> None:
        """Test that option decorator can be reused."""
        decorator = option("--port")

        def func1() -> str:
            return "test1"

        def func2() -> str:
            return "test2"

        result1 = decorator(func1)
        result2 = decorator(func2)

        assert callable(result1)
        assert callable(result2)
        assert mock_queue.call_count == 2

    def test_option_children_initially_empty(self) -> None:
        """Test that Option children dict is initially empty."""
        opt = Option(long="--port")
        assert opt.children == {}
        assert len(opt.children) == 0  # type: ignore


class TestOptionIntegration:
    """Test Option integration scenarios."""

    def test_option_name_extraction_integration(self) -> None:
        """Test that name extraction works with Transform utility."""
        opt1 = Option(long="--port")
        opt2 = Option(long="--config-file")
        opt3 = Option(long="--database-connection-string")

        assert opt1.name == "port"
        assert opt2.name == "config_file"
        assert opt3.name == "database_connection_string"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_option_decorator_function_signature(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that option() function has correct signature."""

        @option("--port")
        def func1() -> str:
            return "test"

        @option(long="--host", short="-h", type=str)
        def func2() -> str:
            return "test"

        assert callable(func1)
        assert callable(func2)
        assert mock_queue.call_count == 2

    def test_option_with_all_click_parameters(self) -> None:
        """Test option with all common Click parameters."""
        opt = Option(
            long="--port",
            short="-p",
            is_flag=False,
            type=int,
            multiple=False,
            help="Port number",
            required=False,
            default=8080,
        )

        assert opt.long == "--port"
        assert opt.short == "-p"
        assert opt.is_flag is False
        assert opt.type == int
        assert opt.multiple is False
        assert opt.help == "Port number"
        assert opt.required is False
        assert opt.default == 8080
        assert opt.name == "port"

    def test_flag_option_typical_usage(self) -> None:
        """Test typical flag option usage."""
        opt = Option(long="--verbose", short="-v", is_flag=True)
        assert opt.is_flag is True
        assert opt.short == "-v"
        assert opt.name == "verbose"

    def test_multiple_values_option_typical_usage(self) -> None:
        """Test typical multiple values option usage."""
        opt = Option(
            long="--tag",
            short="-t",
            multiple=True,
            help="Add tags (can be used multiple times)",
        )
        assert opt.multiple is True
        assert opt.name == "tag"

    def test_typed_option_typical_usage(self) -> None:
        """Test typical typed option usage."""
        opt = Option(
            long="--port",
            short="-p",
            type=int,
            default=8080,
            help="Port number",
        )
        assert opt.type == int
        assert opt.default == 8080
        assert opt.name == "port"

    def test_required_option_typical_usage(self) -> None:
        """Test typical required option usage."""
        opt = Option(
            long="--config-file",
            short="-c",
            required=True,
            help="Path to configuration file",
        )
        assert opt.required is True
        assert opt.name == "config_file"
