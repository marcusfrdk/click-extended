"""Tests for add_prefix decorator."""

from typing import Any

from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.add.add_prefix import add_prefix


class TestAddPrefixBasic:
    """Test basic add_prefix functionality."""

    def test_add_prefix_simple(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with simple string."""

        @command()
        @option("text", default=None)
        @add_prefix("pre_")
        def cmd(text: Any) -> None:
            assert text == "pre_hello"

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0

    def test_add_prefix_empty_string(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with empty string."""

        @command()
        @option("text", default=None)
        @add_prefix("prefix_")
        def cmd(text: Any) -> None:
            assert text == "prefix_"

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0

    def test_add_prefix_with_special_chars(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with special characters."""

        @command()
        @option("text", default=None)
        @add_prefix("@#$_")
        def cmd(text: Any) -> None:
            assert text == "@#$_test"

        result = cli_runner.invoke(cmd, ["--text", "test"])
        assert result.exit_code == 0

    def test_add_prefix_multiple_words(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with multi-word string."""

        @command()
        @option("text", default=None)
        @add_prefix("Hello ")
        def cmd(text: Any) -> None:
            assert text == "Hello World!"

        result = cli_runner.invoke(cmd, ["--text", "World!"])
        assert result.exit_code == 0

    def test_add_prefix_numbers(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with numbers."""

        @command()
        @option("text", default=None)
        @add_prefix("v")
        def cmd(text: Any) -> None:
            assert text == "v1.0.0"

        result = cli_runner.invoke(cmd, ["--text", "1.0.0"])
        assert result.exit_code == 0


class TestAddPrefixVariations:
    """Test add_prefix with different prefix types."""

    def test_add_prefix_path_style(self, cli_runner: CliRunner) -> None:
        """Test add_prefix for path prefixes."""

        @command()
        @option("filename", default=None)
        @add_prefix("/usr/local/bin/")
        def cmd(filename: Any) -> None:
            assert filename == "/usr/local/bin/myapp"

        result = cli_runner.invoke(cmd, ["--filename", "myapp"])
        assert result.exit_code == 0

    def test_add_prefix_url_protocol(self, cli_runner: CliRunner) -> None:
        """Test add_prefix for URL protocols."""

        @command()
        @option("url", default=None)
        @add_prefix("https://")
        def cmd(url: Any) -> None:
            assert url == "https://example.com"

        result = cli_runner.invoke(cmd, ["--url", "example.com"])
        assert result.exit_code == 0

    def test_add_prefix_namespace(self, cli_runner: CliRunner) -> None:
        """Test add_prefix for namespace prefixing."""

        @command()
        @option("name", default=None)
        @add_prefix("company.")
        def cmd(name: Any) -> None:
            assert name == "company.product"

        result = cli_runner.invoke(cmd, ["--name", "product"])
        assert result.exit_code == 0

    def test_add_prefix_version_tag(self, cli_runner: CliRunner) -> None:
        """Test add_prefix for version tags."""

        @command()
        @option("tag", default=None)
        @add_prefix("release-")
        def cmd(tag: Any) -> None:
            assert tag == "release-2024.12"

        result = cli_runner.invoke(cmd, ["--tag", "2024.12"])
        assert result.exit_code == 0


class TestAddPrefixFlatTuple:
    """Test add_prefix with flat tuples."""

    def test_add_prefix_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with flat tuple of strings."""

        @command()
        @option("names", default=None, nargs=3)
        @add_prefix("user_")
        def cmd(names: Any) -> None:
            assert names is not None
            assert isinstance(names, tuple)
            assert len(names) == 3  # type: ignore
            assert names[0] == "user_alice"
            assert names[1] == "user_bob"
            assert names[2] == "user_charlie"

        result = cli_runner.invoke(cmd, ["--names", "alice", "bob", "charlie"])
        assert result.exit_code == 0

    def test_add_prefix_flat_tuple_filenames(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_prefix with flat tuple for file naming."""

        @command()
        @option("files", default=None, nargs=2)
        @add_prefix("backup_")
        def cmd(files: Any) -> None:
            assert files is not None
            assert files[0] == "backup_data.txt"
            assert files[1] == "backup_config.json"

        result = cli_runner.invoke(cmd, ["--files", "data.txt", "config.json"])
        assert result.exit_code == 0

    def test_add_prefix_flat_tuple_ids(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with flat tuple for ID prefixing."""

        @command()
        @option("ids", default=None, nargs=4)
        @add_prefix("ID-")
        def cmd(ids: Any) -> None:
            assert ids is not None
            assert len(ids) == 4
            assert all(id.startswith("ID-") for id in ids)
            assert ids[0] == "ID-001"
            assert ids[3] == "ID-004"

        result = cli_runner.invoke(cmd, ["--ids", "001", "002", "003", "004"])
        assert result.exit_code == 0


class TestAddPrefixNestedTuple:
    """Test add_prefix with nested tuples."""

    def test_add_prefix_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test add_prefix with nested tuple of strings."""

        @command()
        @option("groups", multiple=True, nargs=2)
        @add_prefix("team_")
        def cmd(groups: Any) -> None:
            assert groups is not None
            assert isinstance(groups, tuple)
            assert len(groups) == 2  # type: ignore
            assert groups[0][0] == "team_alpha"
            assert groups[0][1] == "team_beta"
            assert groups[1][0] == "team_gamma"
            assert groups[1][1] == "team_delta"

        result = cli_runner.invoke(
            cmd,
            [
                "--groups",
                "alpha",
                "beta",
                "--groups",
                "gamma",
                "delta",
            ],
        )
        assert result.exit_code == 0

    def test_add_prefix_nested_tuple_environments(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_prefix nested tuple for environment prefixing."""

        @command()
        @option("envs", multiple=True, nargs=2)
        @add_prefix("env-")
        def cmd(envs: Any) -> None:
            assert envs is not None
            assert len(envs) == 2
            assert envs[0][0] == "env-dev"
            assert envs[0][1] == "env-staging"
            assert envs[1][0] == "env-prod"
            assert envs[1][1] == "env-backup"

        result = cli_runner.invoke(
            cmd,
            [
                "--envs",
                "dev",
                "staging",
                "--envs",
                "prod",
                "backup",
            ],
        )
        assert result.exit_code == 0

    def test_add_prefix_nested_tuple_versioned_files(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_prefix nested tuple for versioned file batches."""

        @command()
        @option("batches", multiple=True, nargs=3)
        @add_prefix("v2.0_")
        def cmd(batches: Any) -> None:
            assert batches is not None
            assert len(batches) == 2
            for filename in batches[0]:
                assert filename.startswith("v2.0_")
            assert batches[1][0] == "v2.0_module1.py"
            assert batches[1][1] == "v2.0_module2.py"
            assert batches[1][2] == "v2.0_module3.py"

        result = cli_runner.invoke(
            cmd,
            [
                "--batches",
                "app.py",
                "utils.py",
                "config.py",
                "--batches",
                "module1.py",
                "module2.py",
                "module3.py",
            ],
        )
        assert result.exit_code == 0


class TestAddPrefixPractical:
    """Test practical use cases for add_prefix."""

    def test_add_prefix_docker_image_tags(self, cli_runner: CliRunner) -> None:
        """Test add_prefix for Docker image tagging."""

        @command()
        @option("images", default=None, nargs=3)
        @add_prefix("myregistry.io/")
        def cmd(images: Any) -> None:
            assert images is not None
            assert images[0] == "myregistry.io/app:latest"
            assert images[1] == "myregistry.io/api:v1.0"
            assert images[2] == "myregistry.io/worker:stable"

        result = cli_runner.invoke(
            cmd, ["--images", "app:latest", "api:v1.0", "worker:stable"]
        )
        assert result.exit_code == 0

    def test_add_prefix_log_categories(self, cli_runner: CliRunner) -> None:
        """Test add_prefix for log message categorization."""

        @command()
        @option("messages", default=None, nargs=2)
        @add_prefix("[ERROR] ")
        def cmd(messages: Any) -> None:
            assert messages is not None
            assert messages[0] == "[ERROR] Database connection failed"
            assert messages[1] == "[ERROR] File not found"

        result = cli_runner.invoke(
            cmd,
            [
                "--messages",
                "Database connection failed",
                "File not found",
            ],
        )
        assert result.exit_code == 0

    def test_add_prefix_database_table_prefix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_prefix for database table naming."""

        @command()
        @option("tables", multiple=True, nargs=2)
        @add_prefix("app_")
        def cmd(tables: Any) -> None:
            assert tables is not None
            assert tables[0][0] == "app_users"
            assert tables[0][1] == "app_sessions"
            assert tables[1][0] == "app_products"
            assert tables[1][1] == "app_orders"

        result = cli_runner.invoke(
            cmd,
            [
                "--tables",
                "users",
                "sessions",
                "--tables",
                "products",
                "orders",
            ],
        )
        assert result.exit_code == 0

    def test_add_prefix_git_branch_naming(self, cli_runner: CliRunner) -> None:
        """Test add_prefix for git branch naming conventions."""

        @command()
        @option("branches", default=None, nargs=3)
        @add_prefix("feature/")
        def cmd(branches: Any) -> None:
            assert branches is not None
            assert branches[0] == "feature/user-auth"
            assert branches[1] == "feature/api-endpoints"
            assert branches[2] == "feature/database-schema"

        result = cli_runner.invoke(
            cmd,
            [
                "--branches",
                "user-auth",
                "api-endpoints",
                "database-schema",
            ],
        )
        assert result.exit_code == 0


class TestAddPrefixSkipParameter:
    """Test add_prefix skip parameter functionality."""

    def test_skip_true_prefix_already_exists(
        self, cli_runner: CliRunner
    ) -> None:
        """Test skip=True when prefix already exists (default behavior)."""

        @command()
        @option("text", default=None)
        @add_prefix("pre_", skip=True)
        def cmd(text: Any) -> None:
            assert text == "pre_value"

        result = cli_runner.invoke(cmd, ["--text", "pre_value"])
        assert result.exit_code == 0

    def test_skip_true_prefix_not_exists(self, cli_runner: CliRunner) -> None:
        """Test skip=True when prefix doesn't exist."""

        @command()
        @option("text", default=None)
        @add_prefix("pre_", skip=True)
        def cmd(text: Any) -> None:
            assert text == "pre_value"

        result = cli_runner.invoke(cmd, ["--text", "value"])
        assert result.exit_code == 0

    def test_skip_false_adds_duplicate_prefix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test skip=False adds prefix even if it already exists."""

        @command()
        @option("text", default=None)
        @add_prefix("pre_", skip=False)
        def cmd(text: Any) -> None:
            assert text == "pre_pre_value"

        result = cli_runner.invoke(cmd, ["--text", "pre_value"])
        assert result.exit_code == 0

    def test_skip_default_behavior(self, cli_runner: CliRunner) -> None:
        """Test that skip defaults to True."""

        @command()
        @option("text", default=None)
        @add_prefix("test_")
        def cmd(text: Any) -> None:
            assert text == "test_value"

        result = cli_runner.invoke(cmd, ["--text", "test_value"])
        assert result.exit_code == 0

    def test_skip_with_url_prefix(self, cli_runner: CliRunner) -> None:
        """Test skip parameter with URL prefixes."""

        @command()
        @option("url", default=None)
        @add_prefix("https://", skip=True)
        def cmd(url: Any) -> None:
            assert url == "https://example.com"

        result = cli_runner.invoke(cmd, ["--url", "https://example.com"])
        assert result.exit_code == 0

    def test_skip_with_tuple(self, cli_runner: CliRunner) -> None:
        """Test skip parameter with tuple values."""

        @command()
        @option("names", default=None, nargs=3)
        @add_prefix("user_", skip=True)
        def cmd(names: Any) -> None:
            assert names[0] == "user_alice"
            assert names[1] == "user_bob"
            assert names[2] == "user_charlie"

        result = cli_runner.invoke(
            cmd, ["--names", "user_alice", "bob", "user_charlie"]
        )
        assert result.exit_code == 0


class TestAddPrefixCaseSensitive:
    """Test add_prefix case_sensitive parameter functionality."""

    def test_case_insensitive_uppercase_prefix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test case_sensitive=False with uppercase prefix in value."""

        @command()
        @option("text", default=None)
        @add_prefix("prefix_", skip=True, case_sensitive=False)
        def cmd(text: Any) -> None:
            assert text == "PREFIX_value"

        result = cli_runner.invoke(cmd, ["--text", "PREFIX_value"])
        assert result.exit_code == 0

    def test_case_insensitive_lowercase_prefix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test case_sensitive=False with lowercase prefix in value."""

        @command()
        @option("text", default=None)
        @add_prefix("PREFIX_", skip=True, case_sensitive=False)
        def cmd(text: Any) -> None:
            assert text == "prefix_value"

        result = cli_runner.invoke(cmd, ["--text", "prefix_value"])
        assert result.exit_code == 0

    def test_case_insensitive_mixed_case(self, cli_runner: CliRunner) -> None:
        """Test case_sensitive=False with mixed case."""

        @command()
        @option("text", default=None)
        @add_prefix("test_", skip=True, case_sensitive=False)
        def cmd(text: Any) -> None:
            assert text == "TeSt_value"

        result = cli_runner.invoke(cmd, ["--text", "TeSt_value"])
        assert result.exit_code == 0

    def test_case_sensitive_exact_match(self, cli_runner: CliRunner) -> None:
        """Test case_sensitive=True with exact case match."""

        @command()
        @option("text", default=None)
        @add_prefix("pre_", skip=True, case_sensitive=True)
        def cmd(text: Any) -> None:
            assert text == "pre_value"

        result = cli_runner.invoke(cmd, ["--text", "pre_value"])
        assert result.exit_code == 0

    def test_case_sensitive_different_case_adds_prefix(
        self, cli_runner: CliRunner
    ) -> None:
        """Test case_sensitive=True adds prefix when case differs."""

        @command()
        @option("text", default=None)
        @add_prefix("pre_", skip=True, case_sensitive=True)
        def cmd(text: Any) -> None:
            assert text == "pre_PRE_value"

        result = cli_runner.invoke(cmd, ["--text", "PRE_value"])
        assert result.exit_code == 0

    def test_case_sensitive_default_behavior(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that case_sensitive defaults to False."""

        @command()
        @option("text", default=None)
        @add_prefix("test_", skip=True)
        def cmd(text: Any) -> None:
            assert text == "TEST_value"

        result = cli_runner.invoke(cmd, ["--text", "TEST_value"])
        assert result.exit_code == 0

    def test_case_sensitive_with_tuple(self, cli_runner: CliRunner) -> None:
        """Test case_sensitive parameter with tuple values."""

        @command()
        @option("names", default=None, nargs=3)
        @add_prefix("User_", skip=True, case_sensitive=False)
        def cmd(names: Any) -> None:
            assert names[0] == "user_alice"
            assert names[1] == "User_bob"
            assert names[2] == "USER_charlie"

        result = cli_runner.invoke(
            cmd, ["--names", "user_alice", "bob", "USER_charlie"]
        )
        assert result.exit_code == 0


class TestAddPrefixCombinedParameters:
    """Test add_prefix with combined parameter scenarios."""

    def test_skip_false_case_sensitive_ignored(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that case_sensitive is ignored when skip=False."""

        @command()
        @option("text", default=None)
        @add_prefix("pre_", skip=False, case_sensitive=True)
        def cmd(text: Any) -> None:
            assert text == "pre_PRE_value"

        result = cli_runner.invoke(cmd, ["--text", "PRE_value"])
        assert result.exit_code == 0

    def test_skip_true_case_sensitive_true(self, cli_runner: CliRunner) -> None:
        """Test skip=True with case_sensitive=True."""

        @command()
        @option("text", default=None)
        @add_prefix("Test_", skip=True, case_sensitive=True)
        def cmd(text: Any) -> None:
            # Different case, so prefix is added
            assert text == "Test_test_value"

        result = cli_runner.invoke(cmd, ["--text", "test_value"])
        assert result.exit_code == 0

    def test_empty_prefix_with_skip(self, cli_runner: CliRunner) -> None:
        """Test empty prefix with skip parameter."""

        @command()
        @option("text", default=None)
        @add_prefix("", skip=True)
        def cmd(text: Any) -> None:
            assert text == "value"

        result = cli_runner.invoke(cmd, ["--text", "value"])
        assert result.exit_code == 0

    def test_special_chars_case_insensitive(
        self, cli_runner: CliRunner
    ) -> None:
        """Test special characters with case insensitive matching."""

        @command()
        @option("text", default=None)
        @add_prefix("@Test_", skip=True, case_sensitive=False)
        def cmd(text: Any) -> None:
            assert text == "@test_value"

        result = cli_runner.invoke(cmd, ["--text", "@test_value"])
        assert result.exit_code == 0
