"""Test the Transform class."""

from click_extended.utils.transform import Transform


class Case:
    """A case to test for all transform methods."""

    def __init__(
        self,
        value: str,
        snake_case: str,
        screaming_snake_case: str,
        camel_case: str,
        pascal_case: str,
        kebab_case: str,
        train_case: str,
        flat_case: str,
        dot_case: str,
        title_case: str,
        path_case: str,
    ):
        """
        Initialize a new `Case` instance.

        Args:
            value (str):
                The value to test.
            snake_case (str):
                The expected result for the to_snake_case method.
            screaming_snake_case (str):
                The expected result for the to_screaming_snake_case method.
            camel_case (str):
                The expected result for the to_camel_case method.
            pascal_case (str):
                The expected result for the to_pascal_case method.
            kebab_case (str):
                The expected result for the to_kebab_case method.
            train_case (str):
                The expected result for the to_train_case method.
            flat_case (str):
                The expected result for the to_flat_case method.
            dot_case (str):
                The expected result for the to_dot_case method.
            title_case (str):
                The expected result for the to_title_case method.
            path_case (str):
                The expected result for the to_path_case method.
        """
        self.value = value
        self.snake_case = snake_case
        self.screaming_snake_case = screaming_snake_case
        self.camel_case = camel_case
        self.pascal_case = pascal_case
        self.kebab_case = kebab_case
        self.train_case = train_case
        self.flat_case = flat_case
        self.dot_case = dot_case
        self.title_case = title_case
        self.path_case = path_case


cases: list[Case] = [
    Case(
        value="",
        snake_case="",
        screaming_snake_case="",
        camel_case="",
        pascal_case="",
        kebab_case="",
        train_case="",
        flat_case="",
        dot_case="",
        title_case="",
        path_case="",
    ),
    Case(
        value="MISSING_ENV2",
        snake_case="missing_env2",
        screaming_snake_case="MISSING_ENV2",
        camel_case="missingEnv2",
        pascal_case="MissingEnv2",
        kebab_case="missing-env2",
        train_case="Missing-Env2",
        flat_case="missingenv2",
        dot_case="missing.env2",
        title_case="Missing Env2",
        path_case="MISSING/ENV2",
    ),
    Case(
        value="hello",
        snake_case="hello",
        screaming_snake_case="HELLO",
        camel_case="hello",
        pascal_case="Hello",
        kebab_case="hello",
        train_case="Hello",
        flat_case="hello",
        dot_case="hello",
        title_case="Hello",
        path_case="hello",
    ),
    Case(
        value="thisIsCamelCase",
        snake_case="this_is_camel_case",
        screaming_snake_case="THIS_IS_CAMEL_CASE",
        camel_case="thisIsCamelCase",
        pascal_case="ThisIsCamelCase",
        kebab_case="this-is-camel-case",
        train_case="This-Is-Camel-Case",
        flat_case="thisiscamelcase",
        dot_case="this.is.camel.case",
        title_case="This Is Camel Case",
        path_case="this/Is/Camel/Case",
    ),
    Case(
        value="test123case",
        snake_case="test123_case",
        screaming_snake_case="TEST123_CASE",
        camel_case="test123Case",
        pascal_case="Test123Case",
        kebab_case="test123-case",
        train_case="Test123-Case",
        flat_case="test123case",
        dot_case="test123.case",
        title_case="Test123 Case",
        path_case="test123/case",
    ),
    Case(
        value="   spaces   around   ",
        snake_case="spaces_around",
        screaming_snake_case="SPACES_AROUND",
        camel_case="spacesAround",
        pascal_case="SpacesAround",
        kebab_case="spaces-around",
        train_case="Spaces-Around",
        flat_case="spacesaround",
        dot_case="spaces.around",
        title_case="Spaces Around",
        path_case="spaces/around",
    ),
    Case(
        value="Hello, world",
        snake_case="hello_world",
        screaming_snake_case="HELLO_WORLD",
        camel_case="helloWorld",
        pascal_case="HelloWorld",
        kebab_case="hello-world",
        train_case="Hello-World",
        flat_case="helloworld",
        dot_case="hello.world",
        title_case="Hello World",
        path_case="Hello/world",
    ),
    Case(
        value="_Difficult, string!!!",
        snake_case="difficult_string",
        screaming_snake_case="DIFFICULT_STRING",
        camel_case="difficultString",
        pascal_case="DifficultString",
        kebab_case="difficult-string",
        train_case="Difficult-String",
        flat_case="difficultstring",
        dot_case="difficult.string",
        title_case="Difficult String",
        path_case="Difficult/string",
    ),
    Case(
        value="HELLO WORLD",
        snake_case="hello_world",
        screaming_snake_case="HELLO_WORLD",
        camel_case="helloWorld",
        pascal_case="HelloWorld",
        kebab_case="hello-world",
        train_case="Hello-World",
        flat_case="helloworld",
        dot_case="hello.world",
        title_case="Hello World",
        path_case="HELLO/WORLD",
    ),
    Case(
        value="hello___world---test",
        snake_case="hello_world_test",
        screaming_snake_case="HELLO_WORLD_TEST",
        camel_case="helloWorldTest",
        pascal_case="HelloWorldTest",
        kebab_case="hello-world-test",
        train_case="Hello-World-Test",
        flat_case="helloworldtest",
        dot_case="hello.world.test",
        title_case="Hello World Test",
        path_case="hello/world/test",
    ),
    Case(
        value="v2.0.1",
        snake_case="v2_0_1",
        screaming_snake_case="V2_0_1",
        camel_case="v201",
        pascal_case="V201",
        kebab_case="v2-0-1",
        train_case="V2-0-1",
        flat_case="v201",
        dot_case="v2.0.1",
        title_case="V2 0 1",
        path_case="v2/0/1",
    ),
    Case(
        value="already_snake_case",
        snake_case="already_snake_case",
        screaming_snake_case="ALREADY_SNAKE_CASE",
        camel_case="alreadySnakeCase",
        pascal_case="AlreadySnakeCase",
        kebab_case="already-snake-case",
        train_case="Already-Snake-Case",
        flat_case="alreadysnakecase",
        dot_case="already.snake.case",
        title_case="Already Snake Case",
        path_case="already/snake/case",
    ),
    Case(
        value="PascalCaseInput",
        snake_case="pascal_case_input",
        screaming_snake_case="PASCAL_CASE_INPUT",
        camel_case="pascalCaseInput",
        pascal_case="PascalCaseInput",
        kebab_case="pascal-case-input",
        train_case="Pascal-Case-Input",
        flat_case="pascalcaseinput",
        dot_case="pascal.case.input",
        title_case="Pascal Case Input",
        path_case="Pascal/Case/Input",
    ),
]


class TestSnakeCase:
    """Test the snake case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_snake_case() == case.snake_case


class TestScreamingSnakeCase:
    """Test the screaming snake case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_screaming_snake_case() == case.screaming_snake_case


class TestCamelCase:
    """Test the camel case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_camel_case() == case.camel_case


class TestPascalCase:
    """Test the pascal case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_pascal_case() == case.pascal_case


class TestKebabCase:
    """Test the kebab case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_kebab_case() == case.kebab_case


class TestTrainCase:
    """Test the train case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_train_case() == case.train_case


class TestFlatCaase:
    """Test the flat case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_flat_case() == case.flat_case


class TestDotCase:
    """Test the dot case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_dot_case() == case.dot_case


class TestTitleCase:
    """Test the pascal case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_title_case() == case.title_case


class TestPathCase:
    """Test the path case methods."""

    def test_cases(self) -> None:
        """Test cases."""
        for case in cases:
            t = Transform(case.value)
            assert t.to_path_case() == case.path_case
