"""Tests for the `to_case` decorators."""

from typing import Any

from click.testing import CliRunner

from click_extended import command, option
from click_extended.decorators.transform.to_case import (
    to_camel_case,
    to_dot_case,
    to_flat_case,
    to_kebab_case,
    to_lower_case,
    to_meme_case,
    to_pascal_case,
    to_path_case,
    to_screaming_snake_case,
    to_snake_case,
    to_title_case,
    to_train_case,
    to_upper_case,
)


class TestToCaseBasic:
    """Tests basic functionality of to_case decorators."""

    def test_to_lower_case(self, cli_runner: CliRunner) -> None:
        """Test to_lower_case decorator."""

        @command()
        @option("text", default=None)
        @to_lower_case()
        def cmd(text: Any) -> None:
            assert text == "hello world"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0

    def test_to_upper_case(self, cli_runner: CliRunner) -> None:
        """Test to_upper_case decorator."""

        @command()
        @option("text", default=None)
        @to_upper_case()
        def cmd(text: Any) -> None:
            assert text == "HELLO WORLD"

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

    def test_to_snake_case(self, cli_runner: CliRunner) -> None:
        """Test to_snake_case decorator."""

        @command()
        @option("text", default=None)
        @to_snake_case()
        def cmd(text: Any) -> None:
            assert text == "hello_world"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0

    def test_to_camel_case(self, cli_runner: CliRunner) -> None:
        """Test to_camel_case decorator."""

        @command()
        @option("text", default=None)
        @to_camel_case()
        def cmd(text: Any) -> None:
            assert text == "helloWorld"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0

    def test_to_pascal_case(self, cli_runner: CliRunner) -> None:
        """Test to_pascal_case decorator."""

        @command()
        @option("text", default=None)
        @to_pascal_case()
        def cmd(text: Any) -> None:
            assert text == "HelloWorld"

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

    def test_to_kebab_case(self, cli_runner: CliRunner) -> None:
        """Test to_kebab_case decorator."""

        @command()
        @option("text", default=None)
        @to_kebab_case()
        def cmd(text: Any) -> None:
            assert text == "hello-world"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0


class TestToCaseVariations:
    """Tests for different case conversion variations."""

    def test_to_screaming_snake_case(self, cli_runner: CliRunner) -> None:
        """Test to_screaming_snake_case decorator."""

        @command()
        @option("text", default=None)
        @to_screaming_snake_case()
        def cmd(text: Any) -> None:
            assert text == "HELLO_WORLD"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0

    def test_to_train_case(self, cli_runner: CliRunner) -> None:
        """Test to_train_case decorator."""

        @command()
        @option("text", default=None)
        @to_train_case()
        def cmd(text: Any) -> None:
            assert text == "Hello-World"

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

    def test_to_flat_case(self, cli_runner: CliRunner) -> None:
        """Test to_flat_case decorator."""

        @command()
        @option("text", default=None)
        @to_flat_case()
        def cmd(text: Any) -> None:
            assert text == "helloworld"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0

    def test_to_dot_case(self, cli_runner: CliRunner) -> None:
        """Test to_dot_case decorator."""

        @command()
        @option("text", default=None)
        @to_dot_case()
        def cmd(text: Any) -> None:
            assert text == "hello.world"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0

    def test_to_title_case(self, cli_runner: CliRunner) -> None:
        """Test to_title_case decorator."""

        @command()
        @option("text", default=None)
        @to_title_case()
        def cmd(text: Any) -> None:
            assert text == "Hello World"

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0

    def test_to_path_case(self, cli_runner: CliRunner) -> None:
        """Test to_path_case decorator."""

        @command()
        @option("text", default=None)
        @to_path_case()
        def cmd(text: Any) -> None:
            assert text == "hello/world"

        result = cli_runner.invoke(cmd, ["--text", "Hello World"])
        assert result.exit_code == 0

    def test_to_meme_case(self, cli_runner: CliRunner) -> None:
        """Test to_meme_case decorator."""

        @command()
        @option("text", default=None)
        @to_meme_case()
        def cmd(text: Any) -> None:
            # Meme case alternates upper/lower case
            assert len(text) == len("hello world")
            # Just verify it's not the original
            assert text != "hello world"

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0


class TestToCaseFlatTuple:
    """Tests for flat tuple support."""

    def test_to_snake_case_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_snake_case with flat tuple."""

        @command()
        @option("texts", default=None, nargs=3)
        @to_snake_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert len(texts) == 3
            assert texts[0] == "hello_world"
            assert texts[1] == "foo_bar"
            assert texts[2] == "test_case"

        result = cli_runner.invoke(
            cmd, ["--texts", "Hello World", "Foo Bar", "Test Case"]
        )
        assert result.exit_code == 0

    def test_to_camel_case_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_camel_case with flat tuple."""

        @command()
        @option("texts", default=None, nargs=2)
        @to_camel_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert len(texts) == 2
            assert texts[0] == "helloWorld"
            assert texts[1] == "fooBar"

        result = cli_runner.invoke(cmd, ["--texts", "Hello World", "Foo Bar"])
        assert result.exit_code == 0

    def test_to_kebab_case_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_kebab_case with flat tuple."""

        @command()
        @option("texts", default=None, nargs=2)
        @to_kebab_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert texts[0] == "hello-world"
            assert texts[1] == "foo-bar"

        result = cli_runner.invoke(cmd, ["--texts", "Hello World", "Foo Bar"])
        assert result.exit_code == 0

    def test_to_upper_case_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_upper_case with flat tuple."""

        @command()
        @option("texts", default=None, nargs=2)
        @to_upper_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert texts[0] == "HELLO"
            assert texts[1] == "WORLD"

        result = cli_runner.invoke(cmd, ["--texts", "hello", "world"])
        assert result.exit_code == 0


class TestToCaseNestedTuple:
    """Tests for nested tuple support."""

    def test_to_snake_case_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_snake_case with nested tuple."""

        @command()
        @option("texts", multiple=True, nargs=2)
        @to_snake_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert len(texts) == 2
            assert all(isinstance(t, tuple) for t in texts)
            assert texts[0][0] == "hello_world"
            assert texts[0][1] == "foo_bar"
            assert texts[1][0] == "test_case"
            assert texts[1][1] == "another_test"

        result = cli_runner.invoke(
            cmd,
            [
                "--texts",
                "Hello World",
                "Foo Bar",
                "--texts",
                "Test Case",
                "Another Test",
            ],
        )
        assert result.exit_code == 0

    def test_to_camel_case_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_camel_case with nested tuple."""

        @command()
        @option("texts", multiple=True, nargs=2)
        @to_camel_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert len(texts) == 2
            assert texts[0][0] == "helloWorld"
            assert texts[0][1] == "fooBar"
            assert texts[1][0] == "testCase"
            assert texts[1][1] == "anotherTest"

        result = cli_runner.invoke(
            cmd,
            [
                "--texts",
                "Hello World",
                "Foo Bar",
                "--texts",
                "Test Case",
                "Another Test",
            ],
        )
        assert result.exit_code == 0

    def test_to_pascal_case_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_pascal_case with nested tuple."""

        @command()
        @option("texts", multiple=True, nargs=2)
        @to_pascal_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert texts[0][0] == "HelloWorld"
            assert texts[0][1] == "FooBar"
            assert texts[1][0] == "TestCase"
            assert texts[1][1] == "AnotherTest"

        result = cli_runner.invoke(
            cmd,
            [
                "--texts",
                "hello world",
                "foo bar",
                "--texts",
                "test case",
                "another test",
            ],
        )
        assert result.exit_code == 0

    def test_to_kebab_case_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_kebab_case with nested tuple."""

        @command()
        @option("texts", multiple=True, nargs=2)
        @to_kebab_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert texts[0][0] == "hello-world"
            assert texts[0][1] == "foo-bar"
            assert texts[1][0] == "test-case"
            assert texts[1][1] == "another-test"

        result = cli_runner.invoke(
            cmd,
            [
                "--texts",
                "Hello World",
                "Foo Bar",
                "--texts",
                "Test Case",
                "Another Test",
            ],
        )
        assert result.exit_code == 0

    def test_to_upper_case_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_upper_case with nested tuple."""

        @command()
        @option("texts", multiple=True, nargs=2)
        @to_upper_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert texts[0][0] == "HELLO"
            assert texts[0][1] == "WORLD"
            assert texts[1][0] == "FOO"
            assert texts[1][1] == "BAR"

        result = cli_runner.invoke(
            cmd,
            [
                "--texts",
                "hello",
                "world",
                "--texts",
                "foo",
                "bar",
            ],
        )
        assert result.exit_code == 0

    def test_to_lower_case_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_lower_case with nested tuple."""

        @command()
        @option("texts", multiple=True, nargs=2)
        @to_lower_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert texts[0][0] == "hello"
            assert texts[0][1] == "world"
            assert texts[1][0] == "foo"
            assert texts[1][1] == "bar"

        result = cli_runner.invoke(
            cmd,
            [
                "--texts",
                "HELLO",
                "WORLD",
                "--texts",
                "FOO",
                "BAR",
            ],
        )
        assert result.exit_code == 0


class TestToCasePractical:
    """Practical usage tests."""

    def test_convert_identifiers_to_snake_case(
        self, cli_runner: CliRunner
    ) -> None:
        """Test converting programming identifiers to snake_case."""

        @command()
        @option("identifiers", default=None, nargs=3)
        @to_snake_case()
        def cmd(identifiers: Any) -> None:
            assert identifiers[0] == "my_variable"
            assert identifiers[1] == "some_function_name"
            assert identifiers[2] == "another_class"

        result = cli_runner.invoke(
            cmd,
            [
                "--identifiers",
                "MyVariable",
                "SomeFunctionName",
                "AnotherClass",
            ],
        )
        assert result.exit_code == 0

    def test_convert_class_names_to_pascal_case(
        self, cli_runner: CliRunner
    ) -> None:
        """Test converting class names to PascalCase."""

        @command()
        @option("names", default=None, nargs=2)
        @to_pascal_case()
        def cmd(names: Any) -> None:
            assert names[0] == "UserAccount"
            assert names[1] == "DatabaseConnection"

        result = cli_runner.invoke(
            cmd, ["--names", "user_account", "database_connection"]
        )
        assert result.exit_code == 0

    def test_convert_urls_to_kebab_case(self, cli_runner: CliRunner) -> None:
        """Test converting URL slugs to kebab-case."""

        @command()
        @option("slugs", default=None, nargs=2)
        @to_kebab_case()
        def cmd(slugs: Any) -> None:
            assert slugs[0] == "my-blog-post"
            assert slugs[1] == "another-article"

        result = cli_runner.invoke(
            cmd, ["--slugs", "My Blog Post", "Another Article"]
        )
        assert result.exit_code == 0

    def test_nested_tuple_with_multiple_conversions(
        self, cli_runner: CliRunner
    ) -> None:
        """Test nested tuple with multiple case conversions."""

        @command()
        @option("texts", multiple=True, nargs=3)
        @to_snake_case()
        def cmd(texts: Any) -> None:
            assert isinstance(texts, tuple)
            assert len(texts) == 2
            # First group
            assert texts[0][0] == "first_item"
            assert texts[0][1] == "second_item"
            assert texts[0][2] == "third_item"
            # Second group
            assert texts[1][0] == "fourth_item"
            assert texts[1][1] == "fifth_item"
            assert texts[1][2] == "sixth_item"

        result = cli_runner.invoke(
            cmd,
            [
                "--texts",
                "First Item",
                "Second Item",
                "Third Item",
                "--texts",
                "Fourth Item",
                "Fifth Item",
                "Sixth Item",
            ],
        )
        assert result.exit_code == 0
