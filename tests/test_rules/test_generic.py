import pytest

from querybuilder_rules.rules.generic import GenericRule


@pytest.mark.parametrize("value, expect_res", [
    [1000, True],
    [1500, True],
    [999, False],
    [50, False]
])
def test_simple(value, expect_res):
    rule_condition = {
        "rule": {
            "condition": "AND",
            "rules": [
                {
                    "id": "total",
                    "type": "integer",
                    "operator": "greater_or_equal",
                    "value": "1000",
                },
            ],
        },
    }

    rule = GenericRule(ruleset=[rule_condition])
    res = rule.execute({"total": value})
    assert bool(res) == expect_res
