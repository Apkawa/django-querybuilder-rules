# coding: utf-8
from __future__ import unicode_literals

import unittest

import datetime

from querybuilder_rules.conditions import RuleCondition
from querybuilder_rules.values import OptionValue, OPTION_TYPE_CHOICES, Context


class ConditionTestCase(unittest.TestCase):
    def test_bool_op(self):
        cases = [
            (
                {
                    "type": "boolean",
                    "value": "true",
                    "operator": "equal",
                    "id": "value",
                },
                "true",
                True
            ),
            (
                {
                    "type": "boolean",
                    "value": "false",
                    "operator": "equal",
                    "id": "value",
                },
                "false",
                True
            ),
            (
                {
                    "type": "boolean",
                    "value": "true",
                    "operator": "equal",
                    "id": "value",
                },
                "false",
                False
            ),
            (
                {
                    "type": "boolean",
                    "value": "false",
                    "operator": "equal",
                    "id": "value",
                },
                "true",
                False
            ),
        ]

        rule_cond = RuleCondition([])

        for rule, input_value, expect in cases:
            test_func = rule_cond._build_test_func(rule)['test_func']
            value = OptionValue(input_value, value_type=OPTION_TYPE_CHOICES.BOOL)
            self.assertEqual(test_func(value.get_context()), expect)

    def test_datetime_negative(self):
        cases = [
            (
                {
                    "type": "datetime",
                    "operator": "greater",
                    "value": "3",
                    "id": "hours",
                },
                None,
                False
            ),
            (
                {
                    "type": "datetime",
                    "operator": "between",
                    "value": ["1", "4"],
                    "id": "hours",
                },
                None,
                False
            ),
            (
                {
                    "type": "time",
                    "operator": "between",
                    "value": ["10:00", "14:00"],
                    "id": "time",
                },
                None,
                False
            )
        ]

        rule_cond = RuleCondition([])

        for rule, input_value, expect in cases:
            test_func = rule_cond._build_test_func(rule)['test_func']
            value = OptionValue(input_value, value_type=OPTION_TYPE_CHOICES.DATETIME)
            self.assertEqual(test_func(Context(value.get_context())), expect)
