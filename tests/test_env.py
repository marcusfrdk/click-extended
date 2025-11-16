"""Tests for the Env class."""

import os
from typing import Any
from unittest.mock import MagicMock, patch

from click_extended.core._child_node import ChildNode
from click_extended.core._parent_node import ParentNode
from click_extended.core.env import Env, env
from click_extended.core.tag import Tag


class TestEnvInitialization:
    """Test Env class initialization."""

    def test_init_with_required_parameters(self) -> None:
        """Test initializing Env with required parameters."""
        e = Env(name="api_key", env_name="API_KEY")
        assert e.name == "api_key"
        assert e.env_name == "API_KEY"
        assert e.help is None
        assert e.required is False
        assert e.default is None

    def test_init_with_all_parameters(self) -> None:
        """Test initializing Env with all parameters."""
        e = Env(
            name="api_key",
            env_name="API_KEY",
            help="API key for service",
            required=True,
            default="default_key",
        )
        assert e.name == "api_key"
        assert e.env_name == "API_KEY"
        assert e.help == "API key for service"
        assert e.required is True
        assert e.default == "default_key"

    def test_init_with_help(self) -> None:
        """Test initializing Env with help text."""
        e = Env(name="db_url", env_name="DATABASE_URL", help="Database URL")
        assert e.help == "Database URL"

    def test_init_with_required_true(self) -> None:
        """Test initializing Env with required=True."""
        e = Env(name="token", env_name="AUTH_TOKEN", required=True)
        assert e.required is True

    def test_init_with_required_false(self) -> None:
        """Test initializing Env with required=False."""
        e = Env(name="token", env_name="AUTH_TOKEN", required=False)
        assert e.required is False

    def test_init_with_default_value(self) -> None:
        """Test initializing Env with default value."""
        e = Env(name="port", env_name="PORT", default=8080)
        assert e.default == 8080

    def test_init_children_initialized_as_empty_dict(self) -> None:
        """Test that children dict is initialized empty."""
        e = Env(name="api_key", env_name="API_KEY")
        assert e.children == {}
        assert isinstance(e.children, dict)


class TestEnvGetRawValue:
    """Test Env.get_raw_value functionality."""

    def test_get_raw_value_returns_env_variable(self) -> None:
        """Test get_raw_value returns environment variable value."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            e = Env(name="test_var", env_name="TEST_VAR")
            assert e.get_raw_value() == "test_value"

    def test_get_raw_value_returns_default_when_not_set(self) -> None:
        """Test get_raw_value returns default when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(
                name="missing_var", env_name="MISSING_VAR", default="default"
            )
            assert e.get_raw_value() == "default"

    def test_get_raw_value_returns_none_when_not_required_and_no_default(
        self,
    ) -> None:
        """Test get_raw_value returns None when env var not set and no default."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="optional_var", env_name="OPTIONAL_VAR")
            assert e.get_raw_value() is None

    def test_get_raw_value_raises_when_required_and_not_set(self) -> None:
        """Test get_raw_value raises ValueError when required env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="required_var", env_name="REQUIRED_VAR", required=True)
            try:
                e.get_raw_value()
                assert False, "Expected ValueError"
            except ValueError as ex:
                assert "REQUIRED_VAR" in str(ex)
                assert "not set" in str(ex)

    def test_get_raw_value_raises_when_required_even_with_default(self) -> None:
        """Test get_raw_value raises when required=True even with default."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(
                name="required_var",
                env_name="REQUIRED_VAR",
                required=True,
                default="default",
            )
            try:
                e.get_raw_value()
                assert False, "Expected ValueError"
            except ValueError as ex:
                assert "REQUIRED_VAR" in str(ex)

    def test_get_raw_value_with_empty_string(self) -> None:
        """Test get_raw_value with empty string environment variable."""
        with patch.dict(os.environ, {"EMPTY_VAR": ""}):
            e = Env(name="empty_var", env_name="EMPTY_VAR")
            assert e.get_raw_value() == ""

    def test_get_raw_value_with_numeric_string(self) -> None:
        """Test get_raw_value with numeric string value."""
        with patch.dict(os.environ, {"PORT": "8080"}):
            e = Env(name="port", env_name="PORT")
            assert e.get_raw_value() == "8080"

    def test_get_raw_value_with_multiline_string(self) -> None:
        """Test get_raw_value with multiline environment variable."""
        with patch.dict(os.environ, {"CONFIG": "line1\nline2\nline3"}):
            e = Env(name="config", env_name="CONFIG")
            assert e.get_raw_value() == "line1\nline2\nline3"


class TestEnvInheritance:
    """Test Env class inheritance."""

    def test_env_is_parent_node_subclass(self) -> None:
        """Test that Env is a ParentNode subclass."""
        assert issubclass(Env, ParentNode)

    def test_env_instance_is_parent_node_instance(self) -> None:
        """Test that Env instance is a ParentNode instance."""
        e = Env(name="test", env_name="TEST")
        assert isinstance(e, ParentNode)

    def test_env_has_parent_node_attributes(self) -> None:
        """Test that Env has ParentNode attributes."""
        e = Env(name="test", env_name="TEST", help="Help", required=True)
        assert hasattr(e, "name")
        assert hasattr(e, "help")
        assert hasattr(e, "required")
        assert hasattr(e, "default")
        assert hasattr(e, "children")

    def test_env_has_children_dict(self) -> None:
        """Test that Env has children dict from ParentNode."""
        e = Env(name="test", env_name="TEST")
        assert hasattr(e, "children")
        assert isinstance(e.children, dict)


class TestEnvAsDecorator:
    """Test Env.as_decorator functionality."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_returns_decorator(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator returns a decorator function."""
        decorator = Env.as_decorator(name="api_key", env_name="API_KEY")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_creates_env_instance(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator creates Env instance."""
        decorator = Env.as_decorator(name="api_key", env_name="API_KEY")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        assert isinstance(args[0], Env)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_with_all_params(self, mock_queue: MagicMock) -> None:
        """Test as_decorator with all parameters."""
        decorator = Env.as_decorator(
            name="db_url",
            env_name="DATABASE_URL",
            help="Database connection URL",
            required=True,
            default="sqlite:///:memory:",
        )

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_queues_parent(self, mock_queue: MagicMock) -> None:
        """Test as_decorator queues parent node."""
        decorator = Env.as_decorator(name="api_key", env_name="API_KEY")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_as_decorator_preserves_function(
        self, mock_queue: MagicMock
    ) -> None:
        """Test as_decorator preserves function behavior."""
        decorator = Env.as_decorator(name="api_key", env_name="API_KEY")

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
        decorator = Env.as_decorator(name="api_key", env_name="API_KEY")

        async def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)


class TestEnvDecoratorFunction:
    """Test the env() decorator function."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_with_env_name_only(
        self, mock_queue: MagicMock
    ) -> None:
        """Test env decorator with env_name only."""

        @env("API_KEY")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_infers_name_from_env_name(
        self, mock_queue: MagicMock
    ) -> None:
        """Test env decorator infers parameter name from env_name."""

        @env("API_KEY")
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.name == "api_key"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_with_explicit_name(
        self, mock_queue: MagicMock
    ) -> None:
        """Test env decorator with explicit parameter name."""

        @env("DATABASE_URL", name="db")
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.name == "db"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_with_help(self, mock_queue: MagicMock) -> None:
        """Test env decorator with help parameter."""

        @env("API_KEY", help="API key for authentication")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_with_required(self, mock_queue: MagicMock) -> None:
        """Test env decorator with required parameter."""

        @env("API_KEY", required=True)
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.required is True

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_with_default(self, mock_queue: MagicMock) -> None:
        """Test env decorator with default parameter."""

        @env("PORT", default=8080)
        def test_func() -> str:  # type: ignore
            return "test"

        mock_queue.assert_called_once()
        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.default == 8080

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_with_all_params(self, mock_queue: MagicMock) -> None:
        """Test env decorator with all parameters."""

        @env(
            "DATABASE_URL",
            name="db",
            help="Database connection URL",
            required=True,
            default="sqlite:///:memory:",
        )
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_with_extra_kwargs(
        self, mock_queue: MagicMock
    ) -> None:
        """Test env decorator with extra kwargs."""

        @env("API_KEY", custom_param="custom_value")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_queue.assert_called_once()

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_returns_callable(
        self, mock_queue: MagicMock
    ) -> None:
        """Test env decorator returns callable."""

        @env("API_KEY")
        def test_func() -> str:
            return "test"

        assert callable(test_func)


class TestEnvNameTransformation:
    """Test env name transformation to parameter name."""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_uppercase_to_lowercase(self, mock_queue: MagicMock) -> None:
        """Test uppercase env name converted to lowercase."""

        @env("API_KEY")
        def test_func() -> str:  # type: ignore
            return "test"

        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.name == "api_key"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_underscore_preserved(self, mock_queue: MagicMock) -> None:
        """Test underscores are preserved in transformation."""

        @env("DATABASE_URL")
        def test_func() -> str:  # type: ignore
            return "test"

        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.name == "database_url"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_explicit_name_overrides_transformation(
        self, mock_queue: MagicMock
    ) -> None:
        """Test explicit name overrides transformation."""

        @env("API_KEY", name="custom_name")
        def test_func() -> str:  # type: ignore
            return "test"

        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.name == "custom_name"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_single_word_lowercase(self, mock_queue: MagicMock) -> None:
        """Test single word uppercase converted to lowercase."""

        @env("PORT")
        def test_func() -> str:  # type: ignore
            return "test"

        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.name == "port"

    @patch("click_extended.core._parent_node.queue_parent")
    def test_mixed_case_to_snake_case(self, mock_queue: MagicMock) -> None:
        """Test mixed case env name converted to snake_case."""

        @env("MyApiKey")
        def test_func() -> str:  # type: ignore
            return "test"

        args, _ = mock_queue.call_args
        env_instance = args[0]
        assert env_instance.name == "my_api_key"


class TestEnvEdgeCases:
    """Test Env edge cases."""

    def test_env_name_can_be_empty(self) -> None:
        """Test that env_name can be empty string."""
        e = Env(name="test", env_name="")
        assert e.env_name == ""

    def test_parameter_name_can_be_empty(self) -> None:
        """Test that parameter name can be empty string."""
        e = Env(name="", env_name="TEST_VAR")
        assert e.name == ""

    @patch("click_extended.core._parent_node.queue_parent")
    def test_multiple_env_decorators_independent(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that multiple env decorators are independent."""

        @env("VAR1")
        def func1() -> str:
            return "test1"

        @env("VAR2")
        def func2() -> str:
            return "test2"

        assert callable(func1)
        assert callable(func2)
        assert mock_queue.call_count == 2

    def test_default_can_be_any_type(self) -> None:
        """Test that default can be any type."""
        e1 = Env(name="str_var", env_name="STR_VAR", default="string")
        e2 = Env(name="int_var", env_name="INT_VAR", default=42)
        e3 = Env(name="list_var", env_name="LIST_VAR", default=[1, 2, 3])
        e4 = Env(name="dict_var", env_name="DICT_VAR", default={"key": "value"})

        assert e1.default == "string"
        assert e2.default == 42
        assert e3.default == [1, 2, 3]
        assert e4.default == {"key": "value"}

    def test_help_can_be_empty_string(self) -> None:
        """Test that help can be empty string."""
        e = Env(name="test", env_name="TEST", help="")
        assert e.help == ""

    def test_required_and_default_both_set(self) -> None:
        """Test that both required and default can be set."""
        e = Env(name="test", env_name="TEST", required=True, default="default")
        assert e.required is True
        assert e.default == "default"

    def test_env_name_with_special_characters(self) -> None:
        """Test env_name with special characters."""
        e = Env(name="test", env_name="TEST_VAR-123")
        assert e.env_name == "TEST_VAR-123"

    def test_get_value_inherits_from_parent_node(self) -> None:
        """Test that get_value is inherited from ParentNode."""
        e = Env(name="test", env_name="TEST")
        assert hasattr(e, "get_value")
        assert callable(e.get_value)

    @patch("click_extended.core._parent_node.queue_parent")
    def test_decorator_can_be_reused(self, mock_queue: MagicMock) -> None:
        """Test that env decorator can be reused."""
        decorator = env("API_KEY")

        def func1() -> str:
            return "test1"

        def func2() -> str:
            return "test2"

        result1 = decorator(func1)
        result2 = decorator(func2)

        assert callable(result1)
        assert callable(result2)
        assert mock_queue.call_count == 2

    def test_env_children_initially_empty(self) -> None:
        """Test that Env children dict is initially empty."""
        e = Env(name="test", env_name="TEST")
        assert e.children == {}
        assert e.children is not None
        assert len(e.children) == 0


class TestEnvIntegration:
    """Test Env integration scenarios."""

    def test_get_raw_value_with_get_value(self) -> None:
        """Test get_raw_value integration with get_value from ParentNode."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            e = Env(name="test", env_name="TEST_VAR")
            value = e.get_value()
            assert value == "test_value"

    def test_get_value_with_children(self) -> None:
        """Test get_value processes value through children."""
        from click_extended.core._child_node import ChildNode

        class UppercaseChild(ChildNode):
            """Test child that uppercases values."""

            def process(
                self,
                value: str,
                *args: Any,
                siblings: list[str],
                tags: dict[str, Tag],
                parent: ParentNode | Tag,
                **kwargs: Any,
            ) -> str:
                """Uppercase the value."""
                return value.upper() if value else value

        with patch.dict(os.environ, {"TEST_VAR": "lowercase"}):
            e = Env(name="test", env_name="TEST_VAR")
            child = UppercaseChild(name="uppercase")
            assert e.children is not None
            e[0] = child

            value = e.get_value()
            assert value == "LOWERCASE"

    def test_required_behavior_with_default(self) -> None:
        """Test that required=True overrides default behavior."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(
                name="test",
                env_name="MISSING_VAR",
                required=True,
                default="should_be_ignored",
            )
            try:
                e.get_raw_value()
                assert False, "Expected ValueError"
            except ValueError as ex:
                assert "MISSING_VAR" in str(ex)

    def test_optional_with_none_default(self) -> None:
        """Test optional env var returns None when not set."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="test", env_name="OPTIONAL_VAR", required=False)
            assert e.get_raw_value() is None

    @patch("click_extended.core._parent_node.queue_parent")
    def test_env_decorator_function_signature(
        self, mock_queue: MagicMock
    ) -> None:
        """Test that env() function has correct signature."""

        @env("VAR1")
        def func1() -> str:
            return "test"

        @env(env_name="VAR2", name="var", required=True)
        def func2() -> str:
            return "test"

        assert callable(func1)
        assert callable(func2)
        assert mock_queue.call_count == 2

    def test_env_with_dotenv_integration(self) -> None:
        """Test that Env integrates with dotenv (load_dotenv called at module level)."""
        with patch.dict(os.environ, {"TEST_VAR": "from_env"}):
            e = Env(name="test", env_name="TEST_VAR")
            assert e.get_raw_value() == "from_env"

    def test_env_value_from_environment(self) -> None:
        """Test reading actual environment variable value."""
        test_var_name = "TEST_ENV_VARIABLE_12345"
        test_var_value = "test_value_12345"

        with patch.dict(os.environ, {test_var_name: test_var_value}):
            e = Env(name="test", env_name=test_var_name)
            assert e.get_raw_value() == test_var_value

    def test_env_respects_os_getenv_behavior(self) -> None:
        """Test that Env respects os.getenv behavior for None."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="test", env_name="NONEXISTENT_VAR")
            assert e.get_raw_value() is None


class TestEnvCheckRequired:
    """Test Env.check_required functionality."""

    def test_check_required_returns_none_when_env_var_set(self) -> None:
        """Test check_required returns None when required env var is set."""
        with patch.dict(os.environ, {"TEST_VAR": "value"}):
            e = Env(name="test", env_name="TEST_VAR", required=True)
            assert e.check_required() is None

    def test_check_required_returns_env_name_when_missing(self) -> None:
        """Test check_required returns env_name when required var is missing."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="test", env_name="MISSING_VAR", required=True)
            assert e.check_required() == "MISSING_VAR"

    def test_check_required_returns_none_when_not_required(self) -> None:
        """Test check_required returns None when env var is not required."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="test", env_name="OPTIONAL_VAR", required=False)
            assert e.check_required() is None

    def test_check_required_with_required_false_and_env_set(self) -> None:
        """Test check_required with optional env var that is set."""
        with patch.dict(os.environ, {"OPTIONAL_VAR": "value"}):
            e = Env(name="test", env_name="OPTIONAL_VAR", required=False)
            assert e.check_required() is None

    def test_check_required_ignores_default_value(self) -> None:
        """Test check_required ignores default value when required=True."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(
                name="test",
                env_name="MISSING_VAR",
                required=True,
                default="default_value",
            )
            assert e.check_required() == "MISSING_VAR"

    def test_check_required_does_not_raise_exception(self) -> None:
        """Test check_required does not raise exception (unlike get_raw_value)."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="test", env_name="MISSING_VAR", required=True)
            result = e.check_required()
            assert result == "MISSING_VAR"

    def test_check_required_multiple_times(self) -> None:
        """Test check_required can be called multiple times."""
        with patch.dict(os.environ, {}, clear=True):
            e = Env(name="test", env_name="MISSING_VAR", required=True)
            assert e.check_required() == "MISSING_VAR"
            assert e.check_required() == "MISSING_VAR"
            assert e.check_required() == "MISSING_VAR"

    def test_check_required_with_empty_string_env_var(self) -> None:
        """Test check_required treats empty string as set."""
        with patch.dict(os.environ, {"EMPTY_VAR": ""}):
            e = Env(name="test", env_name="EMPTY_VAR", required=True)
            assert e.check_required() is None


class TestEnvMultipleMissingVariables:
    """Test multiple missing required environment variables error handling."""

    def test_single_missing_variable_error_message(self) -> None:
        """Test error message for single missing required variable."""
        from click_extended.core.command import command

        @command()
        @env("MISSING_VAR_1", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError as ex:
                error_msg = str(ex)
                assert (
                    "Required environment variable 'MISSING_VAR_1' is not set"
                    in error_msg
                )
                assert " and " not in error_msg

    def test_two_missing_variables_error_message(self) -> None:
        """Test error message for two missing required variables."""
        from click_extended.core.command import command

        @command()
        @env("MISSING_VAR_1", required=True)
        @env("MISSING_VAR_2", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError as ex:
                error_msg = str(ex)
                assert "Required environment variables" in error_msg
                assert "'MISSING_VAR_1'" in error_msg
                assert "'MISSING_VAR_2'" in error_msg
                assert " and " in error_msg
                assert error_msg.count("'") == 4

    def test_three_missing_variables_error_message(self) -> None:
        """Test error message for three missing required variables."""
        from click_extended.core.command import command

        @command()
        @env("MISSING_VAR_1", required=True)
        @env("MISSING_VAR_2", required=True)
        @env("MISSING_VAR_3", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError as ex:
                error_msg = str(ex)
                assert "Required environment variables" in error_msg
                assert "'MISSING_VAR_1'" in error_msg
                assert "'MISSING_VAR_2'" in error_msg
                assert "'MISSING_VAR_3'" in error_msg
                assert " and " in error_msg
                assert "," in error_msg

    def test_mixed_required_and_optional_variables(self) -> None:
        """Test only required missing variables are reported."""
        from click_extended.core.command import command

        @command()
        @env("REQUIRED_VAR", required=True)
        @env("OPTIONAL_VAR", required=False)
        @env("REQUIRED_VAR_2", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError as ex:
                error_msg = str(ex)
                assert "'REQUIRED_VAR'" in error_msg
                assert "'REQUIRED_VAR_2'" in error_msg
                assert "'OPTIONAL_VAR'" not in error_msg

    def test_some_required_variables_set(self) -> None:
        """Test error message when some required variables are set."""
        from click_extended.core.command import command

        @command()
        @env("SET_VAR", required=True)
        @env("MISSING_VAR_1", required=True)
        @env("MISSING_VAR_2", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {"SET_VAR": "value"}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError as ex:
                error_msg = str(ex)
                assert "'MISSING_VAR_1'" in error_msg
                assert "'MISSING_VAR_2'" in error_msg
                assert "'SET_VAR'" not in error_msg

    def test_all_required_variables_set_no_error(self) -> None:
        """Test no error when all required variables are set."""
        from click_extended.core.command import command

        call_count = 0

        @command()
        @env("VAR_1", required=True)
        @env("VAR_2", required=True)
        @env("VAR_3", required=True)
        def test_cmd(**kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1

        with patch.dict(
            os.environ,
            {"VAR_1": "v1", "VAR_2": "v2", "VAR_3": "v3"},
            clear=True,
        ):
            test_cmd([], standalone_mode=False)
            assert call_count == 1

    def test_error_raised_before_processing(self) -> None:
        """Test that validation happens before any processing."""
        from click_extended.core.command import command

        process_called = False

        class TestChild(ChildNode):  # type: ignore
            def process(
                self,
                value: Any,
                *args: Any,
                siblings: list[str],
                tags: dict[str, Tag],
                parent: ParentNode | Tag,
                **kwargs: Any,
            ) -> Any:
                nonlocal process_called
                process_called = True
                return value

        @command()
        @env("MISSING_VAR", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError:
                assert not process_called

    def test_error_message_grammar_for_one_variable(self) -> None:
        """Test proper grammar (singular) for one missing variable."""
        from click_extended.core.command import command

        @command()
        @env("MISSING_VAR", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError as ex:
                error_msg = str(ex)
                assert "variable" in error_msg.lower()
                assert "is not set" in error_msg

    def test_error_message_grammar_for_multiple_variables(self) -> None:
        """Test proper grammar (plural) for multiple missing variables."""
        from click_extended.core.command import command

        @command()
        @env("VAR_1", required=True)
        @env("VAR_2", required=True)
        def test_cmd(**kwargs: Any) -> None:
            pass

        with patch.dict(os.environ, {}, clear=True):
            try:
                test_cmd([], standalone_mode=False)
                assert False, "Expected ValueError"
            except ValueError as ex:
                error_msg = str(ex)
                assert "variables" in error_msg.lower()
                assert "are not set" in error_msg
