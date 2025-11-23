"""Class to process strings and transform to different casings."""

import re

NON_ALPHABETIC_PATTERN = re.compile(r"[^A-Za-z]+")
NON_ALPHANUMERIC_PATTERN = re.compile(r"[^A-Za-z0-9]+")
LOWER_TO_UPPER_PATTERN = re.compile(r"([a-z])([A-Z])")
UPPER_TO_UPPER_LOWER_PATTERN = re.compile(r"([A-Z]+)([A-Z][a-z])")
NUMBER_TO_LETTER_PATTERN = re.compile(r"(\d)([a-zA-Z])")


class Casing:
    """Class to process strings and transform to different casings."""

    @staticmethod
    def normalize(value: str, sep: str) -> str:
        """Normalize a value with a separator."""
        value = LOWER_TO_UPPER_PATTERN.sub(r"\1" + sep + r"\2", value)
        value = UPPER_TO_UPPER_LOWER_PATTERN.sub(r"\1" + sep + r"\2", value)
        value = NUMBER_TO_LETTER_PATTERN.sub(r"\1" + sep + r"\2", value)
        value = NON_ALPHANUMERIC_PATTERN.sub(sep, value)
        value = re.sub(f"({re.escape(sep)})+", sep, value)
        return value.strip(sep)

    @staticmethod
    def to_lower_case(value: str) -> str:
        """Convert the value to lower case."""
        return value.strip(" ").lower()

    @staticmethod
    def to_upper_case(value: str) -> str:
        """Convert the value to upper case."""
        return value.strip(" ").upper()

    @staticmethod
    def to_meme_case(value: str) -> str:
        """Convert the value to mEmE cAsE."""
        value = Casing.normalize(value, " ")
        value = NON_ALPHABETIC_PATTERN.sub(" ", value)
        return " ".join(
            "".join(
                v.upper() if i % 2 == 0 else v.lower()
                for i, v in enumerate(word)
            )
            for word in value.strip().split(" ")
        )

    @staticmethod
    def to_snake_case(value: str) -> str:
        """Convert the value to snake_case."""
        normalized = Casing.normalize(value, "_")
        return normalized.lower()

    @staticmethod
    def to_screaming_snake_case(value: str) -> str:
        """Convert the value to SCREAMING_SNAKE_CASE."""
        return Casing.to_snake_case(value).upper()

    @staticmethod
    def to_camel_case(value: str) -> str:
        """Convert the value to camelCase."""
        value = Casing.to_pascal_case(value)
        return value[:1].lower() + value[1:]

    @staticmethod
    def to_pascal_case(value: str) -> str:
        """Convert the value to PascalCase."""
        value = Casing.normalize(value, " ")
        return "".join(word.capitalize() for word in value.split(" "))

    @staticmethod
    def to_kebab_case(value: str) -> str:
        """Convert the value to kebab-case."""
        normalized = Casing.normalize(value, "-")
        return normalized.lower()

    @staticmethod
    def to_train_case(value: str) -> str:
        """Convert the value to Train-Case."""
        value = Casing.normalize(value, "-")
        return "-".join(word.capitalize() for word in value.split("-"))

    @staticmethod
    def to_flat_case(value: str) -> str:
        """Convert the value to flatcase."""
        value = Casing.normalize(value, " ")
        return "".join(value.lower().split(" "))

    @staticmethod
    def to_dot_case(value: str) -> str:
        """Convert the value to dot.case."""
        normalized = Casing.normalize(value, ".")
        return normalized.lower()

    @staticmethod
    def to_title_case(value: str) -> str:
        """Convert the value to Title Case."""
        value = Casing.normalize(value, " ")
        return " ".join(word.capitalize() for word in value.split(" "))

    @staticmethod
    def to_path_case(value: str) -> str:
        """Convert the value to path/case."""
        return Casing.normalize(value, "/")
