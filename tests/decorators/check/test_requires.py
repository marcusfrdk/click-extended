"""Tests for the @requires decorator."""

from typing import Any

import pytest
from click.testing import CliRunner

from click_extended import argument, command, option
from click_extended.decorators import requires


class TestRequiresBasic:
    """Test basic @requires functionality."""

    def test_requires_with_both_params_provided(self, cli_runner: Any) -> None:
        """Test that command succeeds when both params are provided."""

        @command()
        @option("username")
        @requires("password")
        @option("password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        result = cli_runner.invoke(
            login, ["--username", "john", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "Login: john/secret" in result.output

    def test_requires_fails_when_dependency_missing(
        self, cli_runner: Any
    ) -> None:
        """Test that command fails when required dependency is missing."""

        @command()
        @option("username")
        @requires("password")
        @option("password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        result = cli_runner.invoke(login, ["--username", "john"])
        assert result.exit_code == 1
        assert (
            "'--username' requires '--password' to be provided" in result.output
        )

    def test_requires_succeeds_when_neither_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that command succeeds when neither param is provided."""

        @command()
        @option("username")
        @requires("password")
        @option("password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        result = cli_runner.invoke(login, [])
        assert result.exit_code == 0
        assert "Login: None/None" in result.output


class TestRequiresMultipleDependencies:
    """Test @requires with multiple dependencies."""

    def test_requires_multiple_params_all_provided(
        self, cli_runner: Any
    ) -> None:
        """Test requires with multiple dependencies, all provided."""

        @command()
        @option("host")
        @requires("port", "protocol")
        @option("port", type=int)
        @option("protocol")
        def connect(host: str, port: int, protocol: str) -> None:
            print(f"Connect: {host}:{port} via {protocol}")

        result = cli_runner.invoke(
            connect,
            ["--host", "localhost", "--port", "8080", "--protocol", "http"],
        )
        assert result.exit_code == 0
        assert "Connect: localhost:8080 via http" in result.output

    def test_requires_multiple_params_one_missing(
        self, cli_runner: Any
    ) -> None:
        """Test requires with multiple dependencies, one missing."""

        @command()
        @option("host")
        @requires("port", "protocol")
        @option("port", type=int)
        @option("protocol")
        def connect(host: str, port: int, protocol: str) -> None:
            print(f"Connect: {host}:{port} via {protocol}")

        result = cli_runner.invoke(
            connect, ["--host", "localhost", "--port", "8080"]
        )
        assert result.exit_code == 1
        assert "'--host' requires '--protocol' to be provided" in result.output

    def test_requires_multiple_params_all_missing(
        self, cli_runner: Any
    ) -> None:
        """Test requires with multiple dependencies, all missing."""

        @command()
        @option("host")
        @requires("port", "protocol")
        @option("port", type=int)
        @option("protocol")
        def connect(host: str, port: int, protocol: str) -> None:
            print(f"Connect: {host}:{port} via {protocol}")

        result = cli_runner.invoke(connect, ["--host", "localhost"])
        assert result.exit_code == 1
        assert "'--host' requires '--port' and '--protocol'" in result.output


class TestRequiresWithArguments:
    """Test @requires with argument nodes."""

    def test_requires_argument_with_option(self, cli_runner: Any) -> None:
        """Test requires where argument requires an option."""

        @command()
        @argument("filename")
        @requires("format")
        @option("format")
        def process(filename: str, format: str) -> None:
            print(f"Process {filename} as {format}")

        result = cli_runner.invoke(process, ["test.txt", "--format", "json"])
        assert result.exit_code == 0
        assert "Process test.txt as json" in result.output

    def test_requires_argument_missing_option(self, cli_runner: Any) -> None:
        """Test requires fails when argument provided but required option missing."""

        @command()
        @argument("filename")
        @requires("format")
        @option("format")
        def process(filename: str, format: str) -> None:
            print(f"Process {filename} as {format}")

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 1
        assert "'FILENAME' requires '--format' to be provided" in result.output

    def test_requires_optional_argument_not_provided(
        self, cli_runner: Any
    ) -> None:
        """Test requires succeeds when optional argument not provided."""

        @command()
        @argument("filename", required=False)
        @requires("format")
        @option("format")
        def process(filename: str, format: str) -> None:
            print(f"Process {filename} as {format}")

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0
        assert "Process None as None" in result.output


class TestRequiresWithTags:
    """Test @requires with tag nodes."""

    def test_requires_tag_all_provided(self, cli_runner: Any) -> None:
        """Test requires with tag when all tagged params are provided."""
        from click_extended import tag

        @command()
        @option("username", tags="credentials")
        @option("password", tags="credentials")
        @requires("api_key")
        @tag("credentials")
        @option("api_key", "--api-key")
        def login(username: str, password: str, api_key: str) -> None:
            print(f"Login: {username}/{password} with {api_key}")

        result = cli_runner.invoke(
            login,
            [
                "--username",
                "john",
                "--password",
                "secret",
                "--api-key",
                "key123",
            ],
        )
        assert result.exit_code == 0
        assert "Login: john/secret with key123" in result.output

    def test_requires_tag_missing_dependency(self, cli_runner: Any) -> None:
        """Test requires with tag fails when dependency missing."""
        from click_extended import tag

        @command()
        @option("username", tags="credentials")
        @option("password", tags="credentials")
        @requires("api_key")
        @tag("credentials")
        @option("api_key", "--api-key")
        def login(username: str, password: str, api_key: str) -> None:
            print(f"Login: {username}/{password} with {api_key}")

        result = cli_runner.invoke(
            login, ["--username", "john", "--password", "secret"]
        )
        assert result.exit_code == 1
        assert "requires '--api-key' to be provided" in result.output


class TestRequiresWithDefaults:
    """Test @requires with default values."""

    def test_requires_with_default_not_provided(self, cli_runner: Any) -> None:
        """Test that param with default value is not considered 'provided'."""

        @command()
        @option("verbose", is_flag=True, default=False)
        @requires("output")
        @option("output")
        def process(verbose: bool, output: str) -> None:
            print(f"Verbose: {verbose}, Output: {output}")

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0
        assert "Verbose: False, Output: None" in result.output

    def test_requires_with_default_explicitly_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that explicitly providing param triggers requires."""

        @command()
        @option("verbose", is_flag=True, default=False)
        @requires("output")
        @option("output")
        def process(verbose: bool, output: str) -> None:
            print(f"Verbose: {verbose}, Output: {output}")

        result = cli_runner.invoke(process, ["--verbose"])
        assert result.exit_code == 1
        assert "'--verbose' requires '--output' to be provided" in result.output


class TestRequiresErrorMessages:
    """Test error message formatting."""

    def test_requires_single_dependency_error_message(
        self, cli_runner: Any
    ) -> None:
        """Test error message with single dependency."""

        @command()
        @option("input")
        @requires("output")
        @option("output")
        def convert(input: str, output: str) -> None:
            pass

        result = cli_runner.invoke(convert, ["--input", "file.txt"])
        assert result.exit_code == 1
        assert "'--input' requires '--output' to be provided" in result.output

    def test_requires_two_dependencies_error_message(
        self, cli_runner: Any
    ) -> None:
        """Test error message with two dependencies."""

        @command()
        @option("host")
        @requires("username", "password")
        @option("username")
        @option("password")
        def connect(host: str, username: str, password: str) -> None:
            pass

        result = cli_runner.invoke(connect, ["--host", "localhost"])
        assert result.exit_code == 1
        assert (
            "'--host' requires '--username' and '--password'" in result.output
        )

    def test_requires_three_dependencies_error_message(
        self, cli_runner: Any
    ) -> None:
        """Test error message with three dependencies."""

        @command()
        @option("action")
        @requires("user", "pass", "token")
        @option("user")
        @option("pass")
        @option("token")
        def auth(action: str, user: str, **kwargs: Any) -> None:
            pass

        result = cli_runner.invoke(auth, ["--action", "login"])
        assert result.exit_code == 1
        assert (
            "'--action' requires '--user', '--pass' and '--token'"
            in result.output
        )


class TestRequiresEdgeCases:
    """Test edge cases and special scenarios."""

    def test_requires_nonexistent_param(self, cli_runner: Any) -> None:
        """Test requires with nonexistent parameter name."""

        @command()
        @option("input")
        @requires("nonexistent")
        def process(input: str) -> None:
            print(f"Input: {input}")

        # Should not fail - nonexistent param is treated as not provided
        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0

    def test_requires_multiple_decorators_same_param(
        self, cli_runner: Any
    ) -> None:
        """Test multiple requires decorators on same param."""

        @command()
        @option("action")
        @requires("username")
        @requires("password")
        @option("username")
        @option("password")
        def login(action: str, username: str, password: str) -> None:
            print(f"Action: {action}")

        result = cli_runner.invoke(login, ["--action", "login"])
        assert result.exit_code == 1
        # Should fail on first missing requirement
        assert "requires" in result.output

    def test_requires_with_chained_dependencies(self, cli_runner: Any) -> None:
        """Test chained requires (A requires B, B requires C)."""

        @command()
        @option("a")
        @requires("b")
        @option("b")
        @requires("c")
        @option("c")
        def chain(a: str, b: str, c: str) -> None:
            print(f"A: {a}, B: {b}, C: {c}")

        # Providing A requires B, providing B requires C
        result = cli_runner.invoke(chain, ["--a", "1", "--b", "2"])
        assert result.exit_code == 1
        assert "'--b' requires '--c' to be provided" in result.output


@pytest.fixture
def cli_runner() -> CliRunner:
    """Fixture providing a Click CLI runner."""
    return CliRunner()
