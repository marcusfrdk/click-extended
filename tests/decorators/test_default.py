"""Tests for default decorator."""

import click
import pytest
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.decorators.default import default


class TestDefaultBasic:
    """Test basic default functionality."""

    def test_default_from_value_string(self, cli_runner: CliRunner) -> None:
        """Test default with literal string value."""

        @command()
        @option("name", default=None)
        @default(from_value="World")
        def cmd(name: str | None) -> None:
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

    def test_default_from_value_integer(self, cli_runner: CliRunner) -> None:
        """Test default with literal integer value."""

        @command()
        @option("count", type=int, default=None)
        @default(from_value=42)
        def cmd(count: int | None) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Count: 42" in result.output

    def test_default_from_value_boolean(self, cli_runner: CliRunner) -> None:
        """Test default with literal boolean value."""

        @command()
        @option("flag", default=None)
        @default(from_value=True)
        def cmd(flag: bool | None) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Flag: True" in result.output

    def test_default_from_value_list(self, cli_runner: CliRunner) -> None:
        """Test default with literal list value."""

        @command()
        @option("items", default=None)
        @default(from_value=["a", "b", "c"])
        def cmd(items: list[str] | None) -> None:
            click.echo(f"Items: {items}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Items: ['a', 'b', 'c']" in result.output


class TestDefaultFromEnv:
    """Test default from environment variable."""

    def test_default_from_env_exists(self, cli_runner: CliRunner) -> None:
        """Test default from environment variable when it exists."""

        @command()
        @option("api_key", default=None)
        @default(from_env="API_KEY")
        def cmd(api_key: str | None) -> None:
            click.echo(f"API Key: {api_key}")

        result = cli_runner.invoke(cmd, [], env={"API_KEY": "secret123"})
        assert result.exit_code == 0
        assert "API Key: secret123" in result.output

    def test_default_from_env_not_exists(self, cli_runner: CliRunner) -> None:
        """Test default from environment variable when it doesn't exist."""

        @command()
        @option("api_key", default=None)
        @default(from_env="API_KEY")
        def cmd(api_key: str | None) -> None:
            click.echo(f"API Key: {api_key}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "API Key: None" in result.output

    def test_default_from_env_empty_string(self, cli_runner: CliRunner) -> None:
        """Test default from environment variable with empty string."""

        @command()
        @option("value", default=None)
        @default(from_env="VALUE")
        def cmd(value: str | None) -> None:
            click.echo(f"Value: '{value}'")

        result = cli_runner.invoke(cmd, [], env={"VALUE": ""})
        assert result.exit_code == 0
        assert "Value: ''" in result.output


class TestDefaultFromParam:
    """Test default from another parameter."""

    def test_default_from_param_provided(self, cli_runner: CliRunner) -> None:
        """Test default from another parameter when it's provided."""

        @command()
        @option("global_timeout", type=int, default=None)
        @option("timeout", type=int, default=None)
        @default(from_param="global_timeout")
        def cmd(global_timeout: int | None, timeout: int | None) -> None:
            click.echo(f"Timeout: {timeout}")

        result = cli_runner.invoke(cmd, ["--global-timeout", "30"])
        assert result.exit_code == 0
        assert "Timeout: 30" in result.output

    def test_default_from_param_not_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test default from another parameter when it's not provided."""

        @command()
        @option("global_timeout", type=int, default=None)
        @option("timeout", type=int, default=None)
        @default(from_param="global_timeout")
        def cmd(global_timeout: int | None, timeout: int | None) -> None:
            click.echo(f"Timeout: {timeout}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Timeout: None" in result.output

    def test_default_from_param_both_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that explicit value takes precedence over from_param."""

        @command()
        @option("global_timeout", type=int, default=None)
        @option("timeout", type=int, default=None)
        @default(from_param="global_timeout")
        def cmd(global_timeout: int | None, timeout: int | None) -> None:
            click.echo(f"Timeout: {timeout}")

        result = cli_runner.invoke(
            cmd, ["--global-timeout", "30", "--timeout", "60"]
        )
        assert result.exit_code == 0
        assert "Timeout: 60" in result.output


class TestDefaultNotAppliedWhenProvided:
    """Test that default doesn't override provided values."""

    def test_default_from_value_not_applied(
        self, cli_runner: CliRunner
    ) -> None:
        """Test default not applied when value is provided."""

        @command()
        @option("name", default=None)
        @default(from_value="Default")
        def cmd(name: str | None) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["--name", "Custom"])
        assert result.exit_code == 0
        assert "Name: Custom" in result.output

    def test_default_from_env_not_applied(self, cli_runner: CliRunner) -> None:
        """Test env default not applied when value is provided."""

        @command()
        @option("value", default=None)
        @default(from_env="VALUE")
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(
            cmd, ["--value", "Explicit"], env={"VALUE": "FromEnv"}
        )
        assert result.exit_code == 0
        assert "Value: Explicit" in result.output

    def test_default_from_param_not_applied(
        self, cli_runner: CliRunner
    ) -> None:
        """Test param default not applied when value is provided."""

        @command()
        @option("global_val", default=None)
        @option("local_val", default=None)
        @default(from_param="global_val")
        def cmd(global_val: str | None, local_val: str | None) -> None:
            click.echo(f"Local: {local_val}")

        result = cli_runner.invoke(
            cmd, ["--global-val", "Global", "--local-val", "Local"]
        )
        assert result.exit_code == 0
        assert "Local: Local" in result.output


class TestDefaultValidation:
    """Test default decorator validation."""

    def test_error_no_source(self) -> None:
        """Test error when no source is provided."""

        with pytest.raises(
            ValueError,
            match="At least one of 'from_value', 'from_env', or 'from_param' must be provided.",
        ):

            @command()
            @option("value", default=None)
            @default()
            def cmd(value: str | None) -> None:
                pass

    def test_error_multiple_sources_value_and_env(self) -> None:
        """Test error when both from_value and from_env are provided."""

        with pytest.raises(
            ValueError,
            match="Only one of 'from_value', 'from_env', or 'from_param' can be provided.",
        ):

            @command()
            @option("value", default=None)
            @default(from_value="test", from_env="VALUE")
            def cmd(value: str | None) -> None:
                pass

    def test_error_multiple_sources_value_and_param(self) -> None:
        """Test error when both from_value and from_param are provided."""

        with pytest.raises(
            ValueError,
            match="Only one of 'from_value', 'from_env', or 'from_param' can be provided.",
        ):

            @command()
            @option("other", default=None)
            @option("value", default=None)
            @default(from_value="test", from_param="other")
            def cmd(other: str | None, value: str | None) -> None:
                pass

    def test_error_multiple_sources_env_and_param(self) -> None:
        """Test error when both from_env and from_param are provided."""

        with pytest.raises(
            ValueError,
            match="Only one of 'from_value', 'from_env', or 'from_param' can be provided.",
        ):

            @command()
            @option("other", default=None)
            @option("value", default=None)
            @default(from_env="VALUE", from_param="other")
            def cmd(other: str | None, value: str | None) -> None:
                pass

    def test_error_all_sources(self) -> None:
        """Test error when all sources are provided."""

        with pytest.raises(
            ValueError,
            match="Only one of 'from_value', 'from_env', or 'from_param' can be provided.",
        ):

            @command()
            @option("other", default=None)
            @option("value", default=None)
            @default(from_value="test", from_env="VALUE", from_param="other")
            def cmd(other: str | None, value: str | None) -> None:
                pass


class TestDefaultMultipleOptions:
    """Test default with multiple options."""

    def test_multiple_defaults_from_value(self, cli_runner: CliRunner) -> None:
        """Test multiple options with different from_value defaults."""

        @command()
        @option("name", default=None)
        @default(from_value="Alice")
        @option("age", type=int, default=None)
        @default(from_value=25)
        def cmd(name: str | None, age: int | None) -> None:
            click.echo(f"Name: {name}, Age: {age}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Name: Alice, Age: 25" in result.output

    def test_multiple_defaults_mixed_sources(
        self, cli_runner: CliRunner
    ) -> None:
        """Test multiple options with different default sources."""

        @command()
        @option("name", default=None)
        @default(from_value="Bob")
        @option("api_key", default=None)
        @default(from_env="API_KEY")
        def cmd(name: str | None, api_key: str | None) -> None:
            click.echo(f"Name: {name}, Key: {api_key}")

        result = cli_runner.invoke(cmd, [], env={"API_KEY": "secret"})
        assert result.exit_code == 0
        assert "Name: Bob, Key: secret" in result.output


class TestDefaultPractical:
    """Test practical real-world use cases."""

    def test_config_file_path_default(self, cli_runner: CliRunner) -> None:
        """Test default config file path from environment."""

        @command()
        @option("config", default=None)
        @default(from_env="CONFIG_PATH")
        def cmd(config: str | None) -> None:
            click.echo(f"Config: {config}")

        result = cli_runner.invoke(
            cmd, [], env={"CONFIG_PATH": "/etc/app/config.yaml"}
        )
        assert result.exit_code == 0
        assert "Config: /etc/app/config.yaml" in result.output

    def test_timeout_cascade(self, cli_runner: CliRunner) -> None:
        """Test timeout cascading from global to specific."""

        @command()
        @option("global_timeout", type=int, default=None)
        @option("connect_timeout", type=int, default=None)
        @default(from_param="global_timeout")
        @option("read_timeout", type=int, default=None)
        @default(from_param="global_timeout")
        def cmd(
            global_timeout: int | None,
            connect_timeout: int | None,
            read_timeout: int | None,
        ) -> None:
            click.echo(
                f"Global: {global_timeout}, "
                f"Connect: {connect_timeout}, "
                f"Read: {read_timeout}"
            )

        result = cli_runner.invoke(cmd, ["--global-timeout", "30"])
        assert result.exit_code == 0
        assert "Global: 30, Connect: 30, Read: 30" in result.output

    def test_host_port_defaults(self, cli_runner: CliRunner) -> None:
        """Test host and port defaults from environment."""

        @command()
        @option("host", default=None)
        @default(from_env="HOST")
        @option("port", type=int, default=None)
        @default(from_env="PORT")
        def cmd(host: str | None, port: int | None) -> None:
            click.echo(f"Server: {host}:{port}")

        result = cli_runner.invoke(
            cmd, [], env={"HOST": "localhost", "PORT": "8080"}
        )
        assert result.exit_code == 0
        assert "Server: localhost:8080" in result.output


class TestDefaultEdgeCases:
    """Test edge cases for default decorator."""

    def test_default_from_value_zero(self, cli_runner: CliRunner) -> None:
        """Test default with zero value (falsy but valid)."""

        @command()
        @option("count", type=int, default=None)
        @default(from_value=0)
        def cmd(count: int | None) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Count: 0" in result.output

    def test_default_from_value_empty_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test default with empty string (falsy but valid)."""

        @command()
        @option("text", default=None)
        @default(from_value="")
        def cmd(text: str | None) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Text: ''" in result.output

    def test_default_from_value_false(self, cli_runner: CliRunner) -> None:
        """Test default with False value."""

        @command()
        @option("flag", default=None)
        @default(from_value=False)
        def cmd(flag: bool | None) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Flag: False" in result.output

    def test_default_from_param_nonexistent(
        self, cli_runner: CliRunner
    ) -> None:
        """Test default from_param with non-existent parameter."""

        @command()
        @option("value", default=None)
        @default(from_param="nonexistent")
        def cmd(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Value: None" in result.output
