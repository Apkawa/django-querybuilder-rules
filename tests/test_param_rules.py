# coding: utf-8
from __future__ import unicode_literals

import unittest

from querybuilder_rules import OPTION_TYPE_CHOICES
from querybuilder_rules.rules.param import ParamRules


class ValidationTestCase(unittest.TestCase):

    def test_generic(self):
        """
        Если внешняя опция включена, то текущую опцию отмечаем активной, иначе - неактивной.
        """
        external_option_id = "123.value"
        value_type = OPTION_TYPE_CHOICES.BOOL,

        ruleset = [
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": external_option_id,
                            "type": "boolean",
                            "operator": "equal",
                            "value": "true",
                        },
                    ],
                },
                "param_type": "is_active",
                "params": {"is_active": True}
            },
        ]

        expected_results = [
            (True, [{
                "param_type": "is_active",
                "params": {"is_active": True}
            }]),
            (False, []),
            (None, []),
        ]

        for value, expected_result in expected_results:
            _rule_evaluator = ParamRules(ruleset=ruleset, extra_context={"123": {"value": value}})
            result = _rule_evaluator.run(value=None, value_type=OPTION_TYPE_CHOICES.BOOL)
            self.assertEquals(list(r['param'] for r in result), expected_result)
