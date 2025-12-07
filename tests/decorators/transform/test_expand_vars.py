import os
from unittest.mock import Mock

from click_extended.core.other.context import Context
from click_extended.decorators.transform.expand_vars import ExpandVars


def test_expand_vars() -> None:
    node = ExpandVars(name="test")
    ctx = Mock(spec=Context)

    os.environ["TEST_VAR"] = "expanded"
    try:
        assert node.handle_str("$TEST_VAR", ctx) == "expanded"
        assert node.handle_str("prefix_$TEST_VAR", ctx) == "prefix_expanded"
        assert node.handle_str("no_var", ctx) == "no_var"
    finally:
        del os.environ["TEST_VAR"]
