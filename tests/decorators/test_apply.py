"""Tests for apply decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.apply import apply


class TestApplyBasic:
    """Test basic apply functionality."""

    def test_apply_simple_function(self, cli_runner: CliRunner) -> None:
        """Test applying a simple function."""

        @command()
        @option("value", type=int, default=5)
        @apply(lambda x: x * 2)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "10"])
        assert result.exit_code == 0
        assert "Value: 20" in result.output

    def test_apply_string_transformation(self, cli_runner: CliRunner) -> None:
        """Test applying string transformation."""

        @command()
        @option("name", default="world")
        @apply(lambda x: x.upper())
        def cmd(name: str) -> None:
            click.echo(f"Hello {name}")

        result = cli_runner.invoke(cmd, ["--name", "alice"])
        assert result.exit_code == 0
        assert "Hello ALICE" in result.output

    def test_apply_with_default_value(self, cli_runner: CliRunner) -> None:
        """Test apply with default value."""

        @command()
        @option("count", type=int, default=1)
        @apply(lambda x: x + 10)
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Count: 11" in result.output

    def test_apply_type_conversion(self, cli_runner: CliRunner) -> None:
        """Test apply can convert types."""

        @command()
        @option("number", type=float, default=3.14)
        @apply(lambda x: int(x))
        def cmd(number: int) -> None:
            click.echo(f"Number: {number}")

        result = cli_runner.invoke(cmd, ["--number", "7.89"])
        assert result.exit_code == 0
        assert "Number: 7" in result.output


class TestApplyMathOperations:
    """Test mathematical operations with apply."""

    def test_apply_addition(self, cli_runner: CliRunner) -> None:
        """Test adding a constant."""

        @command()
        @option("x", type=int, default=0)
        @apply(lambda x: x + 100)
        def cmd(x: int) -> None:
            click.echo(f"X: {x}")

        result = cli_runner.invoke(cmd, ["--x", "50"])
        assert result.exit_code == 0
        assert "X: 150" in result.output

    def test_apply_multiplication(self, cli_runner: CliRunner) -> None:
        """Test multiplying by a constant."""

        @command()
        @option("price", type=float, default=10.0)
        @apply(lambda x: x * 1.2)  # Add 20% tax
        def cmd(price: float) -> None:
            click.echo(f"Price with tax: {price:.2f}")

        result = cli_runner.invoke(cmd, ["--price", "100"])
        assert result.exit_code == 0
        assert "Price with tax: 120.00" in result.output

    def test_apply_power(self, cli_runner: CliRunner) -> None:
        """Test raising to a power."""

        @command()
        @option("base", type=int, default=2)
        @apply(lambda x: x**3)
        def cmd(base: int) -> None:
            click.echo(f"Cubed: {base}")

        result = cli_runner.invoke(cmd, ["--base", "5"])
        assert result.exit_code == 0
        assert "Cubed: 125" in result.output

    def test_apply_negation(self, cli_runner: CliRunner) -> None:
        """Test negating a number."""

        @command()
        @option("num", type=int, default=42)
        @apply(lambda x: -x)
        def cmd(num: int) -> None:
            click.echo(f"Negative: {num}")

        result = cli_runner.invoke(cmd, ["--num", "10"])
        assert result.exit_code == 0
        assert "Negative: -10" in result.output

    def test_apply_absolute_value(self, cli_runner: CliRunner) -> None:
        """Test getting absolute value."""

        @command()
        @option("val", type=int, default=-5)
        @apply(abs)
        def cmd(val: int) -> None:
            click.echo(f"Absolute: {val}")

        result = cli_runner.invoke(cmd, ["--val", "-42"])
        assert result.exit_code == 0
        assert "Absolute: 42" in result.output


class TestApplyStringOperations:
    """Test string operations with apply."""

    def test_apply_uppercase(self, cli_runner: CliRunner) -> None:
        """Test converting to uppercase."""

        @command()
        @option("text", default="hello")
        @apply(str.upper)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "world"])
        assert result.exit_code == 0
        assert "Text: WORLD" in result.output

    def test_apply_lowercase(self, cli_runner: CliRunner) -> None:
        """Test converting to lowercase."""

        @command()
        @option("text", default="HELLO")
        @apply(str.lower)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "WORLD"])
        assert result.exit_code == 0
        assert "Text: world" in result.output

    def test_apply_strip(self, cli_runner: CliRunner) -> None:
        """Test stripping whitespace."""

        @command()
        @option("text", default="  hello  ")
        @apply(str.strip)
        def cmd(text: str) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", "  world  "])
        assert result.exit_code == 0
        assert "Text: 'world'" in result.output

    def test_apply_title_case(self, cli_runner: CliRunner) -> None:
        """Test converting to title case."""

        @command()
        @option("text", default="hello world")
        @apply(str.title)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "foo bar baz"])
        assert result.exit_code == 0
        assert "Text: Foo Bar Baz" in result.output

    def test_apply_replace(self, cli_runner: CliRunner) -> None:
        """Test replacing text."""

        @command()
        @option("path", default="/home/user")
        @apply(lambda x: x.replace("/home", "/root"))
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "/home/marcus"])
        assert result.exit_code == 0
        assert "Path: /root/marcus" in result.output

    def test_apply_split_and_join(self, cli_runner: CliRunner) -> None:
        """Test splitting and joining."""

        @command()
        @option("tags", default="a,b,c")
        @apply(lambda x: "-".join(x.split(",")))
        def cmd(tags: str) -> None:
            click.echo(f"Tags: {tags}")

        result = cli_runner.invoke(cmd, ["--tags", "red,green,blue"])
        assert result.exit_code == 0
        assert "Tags: red-green-blue" in result.output


class TestApplyListOperations:
    """Test list operations with apply."""

    def test_apply_to_list(self, cli_runner: CliRunner) -> None:
        """Test applying to a tuple value (multiple=True returns tuple)."""

        @command()
        @option("items", multiple=True)
        @apply(lambda x: x.upper())
        def cmd(items: tuple[str, ...]) -> None:
            click.echo(f"Items: {','.join(items)}")

        result = cli_runner.invoke(cmd, ["--items", "x", "--items", "y"])
        assert result.exit_code == 0
        assert "Items: X,Y" in result.output

    def test_apply_list_length(self, cli_runner: CliRunner) -> None:
        """Test applying transformation to each element."""

        @command()
        @option("values", multiple=True)
        @apply(lambda x: len(x))
        def cmd(values: tuple[int, ...]) -> None:
            click.echo(f"Lengths: {','.join(map(str, values))}")

        result = cli_runner.invoke(
            cmd, ["--values", "a", "--values", "bb", "--values", "ccc"]
        )
        assert result.exit_code == 0
        assert "Lengths: 1,2,3" in result.output

    def test_apply_list_sum(self, cli_runner: CliRunner) -> None:
        """Test transforming each element."""

        @command()
        @option("numbers", type=int, multiple=True)
        @apply(lambda x: x * 2)
        def cmd(numbers: tuple[int, ...]) -> None:
            click.echo(f"Doubled: {','.join(map(str, numbers))}")

        result = cli_runner.invoke(
            cmd, ["--numbers", "10", "--numbers", "20", "--numbers", "30"]
        )
        assert result.exit_code == 0
        assert "Doubled: 20,40,60" in result.output


class TestApplyChaining:
    """Test chaining multiple apply decorators."""

    def test_chain_two_applies(self, cli_runner: CliRunner) -> None:
        """Test chaining two apply decorators."""

        @command()
        @option("value", type=int, default=5)
        @apply(lambda x: x * 2)
        @apply(lambda x: x + 10)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "3"])
        assert result.exit_code == 0
        # 3 * 2 = 6, then 6 + 10 = 16
        assert "Value: 16" in result.output

    def test_chain_three_applies(self, cli_runner: CliRunner) -> None:
        """Test chaining three apply decorators."""

        @command()
        @option("text", default="hello")
        @apply(str.upper)
        @apply(lambda x: x + "!")
        @apply(lambda x: x * 2)
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hi"])
        assert result.exit_code == 0
        # "hi" -> "HI" -> "HI!" -> "HI!HI!"
        assert "Text: HI!HI!" in result.output

    def test_chain_with_type_conversions(self, cli_runner: CliRunner) -> None:
        """Test chaining with type conversions."""

        @command()
        @option("num", default="42")
        @apply(int)  # str -> int
        @apply(lambda x: x * 2)  # int -> int
        @apply(str)  # int -> str
        def cmd(num: str) -> None:
            click.echo(f"Num: {num}")

        result = cli_runner.invoke(cmd, ["--num", "10"])
        assert result.exit_code == 0
        assert "Num: 20" in result.output


class TestApplyComplexFunctions:
    """Test apply with more complex functions."""

    def test_apply_with_named_function(self, cli_runner: CliRunner) -> None:
        """Test apply with a named function."""

        def double_and_add_one(x: int) -> int:
            return x * 2 + 1

        @command()
        @option("value", type=int, default=0)
        @apply(double_and_add_one)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "5"])
        assert result.exit_code == 0
        assert "Value: 11" in result.output

    def test_apply_with_builtin_function(self, cli_runner: CliRunner) -> None:
        """Test apply with builtin functions."""

        @command()
        @option("value", type=float, default=3.7)
        @apply(round)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "7.4"])
        assert result.exit_code == 0
        assert "Value: 7" in result.output

    def test_apply_with_multiline_lambda(self, cli_runner: CliRunner) -> None:
        """Test apply with complex lambda."""

        @command()
        @option("score", type=int, default=50)
        @apply(lambda x: "A" if x >= 90 else "B" if x >= 80 else "C")
        def cmd(score: str) -> None:
            click.echo(f"Grade: {score}")

        result = cli_runner.invoke(cmd, ["--score", "95"])
        assert result.exit_code == 0
        assert "Grade: A" in result.output

        result = cli_runner.invoke(cmd, ["--score", "85"])
        assert result.exit_code == 0
        assert "Grade: B" in result.output

        result = cli_runner.invoke(cmd, ["--score", "75"])
        assert result.exit_code == 0
        assert "Grade: C" in result.output


class TestApplyWithMultipleOptions:
    """Test apply with multiple options."""

    def test_apply_to_different_options(self, cli_runner: CliRunner) -> None:
        """Test applying different functions to different options."""

        @command()
        @option("x", type=int, default=1)
        @apply(lambda x: x * 2)
        @option("y", type=int, default=1)
        @apply(lambda y: y + 10)
        def cmd(x: int, y: int) -> None:
            click.echo(f"X: {x}, Y: {y}")

        result = cli_runner.invoke(cmd, ["--x", "5", "--y", "3"])
        assert result.exit_code == 0
        assert "X: 10, Y: 13" in result.output

    def test_apply_order_with_multiple_options(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that apply only affects most recent option."""

        @command()
        @option("first", type=int, default=10)
        @option("second", type=int, default=20)
        @apply(lambda x: x * 100)
        def cmd(first: int, second: int) -> None:
            click.echo(f"First: {first}, Second: {second}")

        result = cli_runner.invoke(cmd, ["--first", "1", "--second", "2"])
        assert result.exit_code == 0
        # Only second should be transformed
        assert "First: 1, Second: 200" in result.output


class TestApplyEdgeCases:
    """Test edge cases and special scenarios."""

    def test_apply_identity_function(self, cli_runner: CliRunner) -> None:
        """Test apply with identity function."""

        @command()
        @option("value", default="test")
        @apply(lambda x: x)
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "hello"])
        assert result.exit_code == 0
        assert "Value: hello" in result.output

    def test_apply_to_none_value(self, cli_runner: CliRunner) -> None:
        """Test apply handles None values."""

        @command()
        @option("value", default=None)
        @apply(lambda x: x if x is not None else "default")
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Value: default" in result.output

    def test_apply_to_empty_string(self, cli_runner: CliRunner) -> None:
        """Test apply with empty string."""

        @command()
        @option("text", default="")
        @apply(lambda x: x if x else "empty")
        def cmd(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0
        assert "Text: empty" in result.output

    def test_apply_to_zero(self, cli_runner: CliRunner) -> None:
        """Test apply with zero value."""

        @command()
        @option("num", type=int, default=0)
        @apply(lambda x: x if x != 0 else 1)
        def cmd(num: int) -> None:
            click.echo(f"Num: {num}")

        result = cli_runner.invoke(cmd, ["--num", "0"])
        assert result.exit_code == 0
        assert "Num: 1" in result.output


class TestApplyPractical:
    """Test practical real-world use cases."""

    def test_apply_for_url_normalization(self, cli_runner: CliRunner) -> None:
        """Test normalizing URL input."""

        def normalize_url(url: str) -> str:
            if not url.startswith(("http://", "https://")):
                return f"https://{url}"
            return url

        @command()
        @option("url", default="example.com")
        @apply(normalize_url)
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")

        result = cli_runner.invoke(cmd, ["--url", "google.com"])
        assert result.exit_code == 0
        assert "URL: https://google.com" in result.output

        result = cli_runner.invoke(cmd, ["--url", "https://github.com"])
        assert result.exit_code == 0
        assert "URL: https://github.com" in result.output

    def test_apply_for_path_expansion(self, cli_runner: CliRunner) -> None:
        """Test expanding ~ in paths."""

        @command()
        @option("path", default="~/documents")
        @apply(lambda x: x.replace("~", "/home/user"))
        def cmd(path: str) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", "~/config"])
        assert result.exit_code == 0
        assert "Path: /home/user/config" in result.output

    def test_apply_for_email_validation(self, cli_runner: CliRunner) -> None:
        """Test email normalization."""

        @command()
        @option("email", default="test@example.com")
        @apply(str.lower)
        @apply(str.strip)
        def cmd(email: str) -> None:
            click.echo(f"Email: {email}")

        result = cli_runner.invoke(cmd, ["--email", "  USER@EXAMPLE.COM  "])
        assert result.exit_code == 0
        assert "Email: user@example.com" in result.output

    def test_apply_for_percentage_to_decimal(
        self, cli_runner: CliRunner
    ) -> None:
        """Test converting percentage to decimal."""

        @command()
        @option("rate", type=float, default=50.0)
        @apply(lambda x: x / 100)
        def cmd(rate: float) -> None:
            click.echo(f"Rate: {rate:.2f}")

        result = cli_runner.invoke(cmd, ["--rate", "75"])
        assert result.exit_code == 0
        assert "Rate: 0.75" in result.output

    def test_apply_for_temperature_conversion(
        self, cli_runner: CliRunner
    ) -> None:
        """Test Celsius to Fahrenheit conversion."""

        @command()
        @option("celsius", type=float, default=0.0)
        @apply(lambda c: (c * 9 / 5) + 32)
        def cmd(celsius: float) -> None:
            click.echo(f"Fahrenheit: {celsius:.1f}")

        result = cli_runner.invoke(cmd, ["--celsius", "100"])
        assert result.exit_code == 0
        assert "Fahrenheit: 212.0" in result.output

        result = cli_runner.invoke(cmd, ["--celsius", "0"])
        assert result.exit_code == 0
        assert "Fahrenheit: 32.0" in result.output
