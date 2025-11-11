"""`ParentNode` that loads a value from an environment variable."""

import os
from typing import Any, Callable, ParamSpec, TypeVar

from dotenv import load_dotenv

from click_extended.core._parent_node import ParentNode
from click_extended.utils.transform import Transform

load_dotenv()

P = ParamSpec("P")
T = TypeVar("T")


class Env(ParentNode):
    """`ParentNode` that loads a value from an environment variable."""

    def __init__(
        self,
        name: str,
        env_name: str,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        **kwargs: Any,
    ):
        """
        Initialize a new `Env` instance.

        Args:
            name (str):
                The parameter name to inject into the function.
                Should already be in snake_case.
            env_name (str):
                The name of the environment variable to read from.
            help (str, optional):
                Help text for this parameter.
            required (bool):
                Whether this parameter is required. Defaults to `False`.
            default (Any):
                Default value if environment variable is not set.
            **kwargs (Any):
                Additional keyword arguments.
        """
        super().__init__(
            name=name, help=help, required=required, default=default
        )
        self.env_name = env_name

    def get_raw_value(self) -> Any:
        """
        Get the raw value from the environment variable.

        Returns:
            Any:
                The value of the environment variable, or the default
                value if not required and not set.

        Raises:
            ValueError:
                If the environment variable is required but not set,
                regardless of whether a default is provided.
        """
        value = os.getenv(self.env_name)
        if value is None:
            if self.required:
                raise ValueError(
                    f"Required environment variable '{self.env_name}' is not set"
                )
            return self.default
        return value


def env(
    env_name: str,
    name: str | None = None,
    help: str | None = None,
    required: bool = False,
    default: Any = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to inject an environment variable value into a command.

    If name is not provided, it defaults to env_name converted to snake_case.

    Args:
        env_name (str):
            The name of the environment variable to read.
        name (str, optional):
            The name of the parameter to inject. If not provided,
            uses env_name converted to snake_case.
        help (str, optional):
            Help text for this parameter.
        required (bool):
            Whether this parameter is required. Defaults to `False`.
            If `True`, the environment variable must be set, even if
            a default value is provided. The default is ignored when
            `required=True`.
        default (Any):
            Default value if environment variable is not set and
            `required=False`. Defaults to `None`.
        **kwargs (Any):
            Additional keyword arguments.

    Returns:
        Callable:
            A decorator function that registers the env parent node.

    Examples:
        >>> @env("API_KEY")
        ... def my_func(api_key):
        ...     print(api_key)

        >>> @env("DATABASE_URL", name="db", required=True)
        ... def my_func(db):
        ...     print(db)
    """
    param_name = (
        name if name is not None else Transform(env_name).to_snake_case()
    )
    return Env.as_decorator(
        name=param_name,
        env_name=env_name,
        help=help,
        required=required,
        default=default,
        **kwargs,
    )
