"""Class to process strings and transform to different formats."""

import re

NON_ALPHANUMERIC_PATTERN = re.compile(r"[^A-Za-z0-9]+")
LOWER_TO_UPPER_PATTERN = re.compile(r"([a-z])([A-Z])")
UPPER_TO_UPPER_LOWER_PATTERN = re.compile(r"([A-Z]+)([A-Z][a-z])")
LETTER_TO_NUMBER_PATTERN = re.compile(r"([a-zA-Z])(\d)")
NUMBER_TO_LETTER_PATTERN = re.compile(r"(\d)([a-zA-Z])")


class Transform:
    """Class to process strings and transform to different formats."""

    def __init__(self, value: str) -> None:
        """
        Initialize a new `Transform` instance.

        Args:
            value (str):
                The string to transform.

        Raises:
            TypeError:
                If the input value is not a string.
        """
        if not isinstance(value, str):
            value_type = type(value).__name__
            raise TypeError(f"Value is not of type string, got {value_type}.")

        self.value = value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"<Transform value='{self.value}'>"

    def _normalize_value(self, value: str, sep: str) -> str:
        """Normalize a value with a separator."""
        value = LOWER_TO_UPPER_PATTERN.sub(r"\1" + sep + r"\2", value)
        value = UPPER_TO_UPPER_LOWER_PATTERN.sub(r"\1" + sep + r"\2", value)
        value = LETTER_TO_NUMBER_PATTERN.sub(r"\1" + sep + r"\2", value)
        value = NUMBER_TO_LETTER_PATTERN.sub(r"\1" + sep + r"\2", value)
        value = NON_ALPHANUMERIC_PATTERN.sub(sep, value)
        value = re.sub(f"({re.escape(sep)})+", sep, value)
        return value.strip(sep)

    def to_snake_case(self) -> str:
        """Convert the value to snake_case."""
        normalized = self._normalize_value(self.value, "_")
        return normalized.lower()

    def to_screaming_snake_case(self) -> str:
        """Convert the value to SCREAMING_SNAKE_CASE."""
        return self.to_snake_case().upper()

    def to_camel_case(self) -> str:
        """Convert the value to camelCase."""
        value = self.to_pascal_case()
        return value[:1].lower() + value[1:]

    def to_pascal_case(self) -> str:
        """Convert the value to PascalCase."""
        value = self._normalize_value(self.value, " ")
        return "".join(word.capitalize() for word in value.split(" "))

    def to_kebab_case(self) -> str:
        """Convert the value to kebab-case."""
        normalized = self._normalize_value(self.value, "-")
        return normalized.lower()

    def to_train_case(self) -> str:
        """Convert the value to Train-Case."""
        value = self._normalize_value(self.value, "-")
        return "-".join(word.capitalize() for word in value.split("-"))

    def to_flat_case(self) -> str:
        """Convert the value to flatcase."""
        value = self._normalize_value(self.value, " ")
        return "".join(value.lower().split(" "))

    def to_dot_case(self) -> str:
        """Convert the value to dot.case."""
        normalized = self._normalize_value(self.value, ".")
        return normalized.lower()

    def to_title_case(self) -> str:
        """Convert the value to Title Case."""
        value = self._normalize_value(self.value, " ")
        return " ".join(word.capitalize() for word in value.split(" "))

    def to_path_case(self) -> str:
        """Convert the value to path/case."""
        return self._normalize_value(self.value, "/")


if __name__ == "__main__":
    t = Transform("Hello, world!")
    print(t.to_dot_case())
