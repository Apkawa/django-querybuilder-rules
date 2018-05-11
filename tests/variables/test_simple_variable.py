import pytest

from querybuilder_rules.variables.simple import (
    IntegerVariable,
    FloatVariable,
    BooleanVariable,
    TextVariable,
)


@pytest.mark.parametrize("variable_cls,value,expect", [
    [IntegerVariable, 10, 10],
    [IntegerVariable, "10", 10],
    [FloatVariable, 10, 10],
    [FloatVariable, 10.5, 10.5],
    [FloatVariable, "10.5", 10.5],
    [BooleanVariable, True, True],
    [BooleanVariable, 1, True],
    [BooleanVariable, "132", True],
    [BooleanVariable, False, False],
    [TextVariable, "test", "test"],
    [TextVariable, "юникод", "юникод"],
])
def test_simple(variable_cls, value, expect):
    v = variable_cls(value)
    assert v.get_fields()['value']
    assert v.get_context() == expect
