# coding: utf-8
from __future__ import unicode_literals

import datetime
import unittest

from querybuilder_rules.conditions import RuleCondition


class ConditionTestCase(unittest.TestCase):
    def test_success(self):
        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "id": "value",
                    "type": "integer",
                    "operator": "greater",
                    "value": "1",
                },
                {
                    "id": "value",
                    "type": "integer",
                    "operator": "equal",
                    "value": "2",
                },
            ]
        }
        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': 2,
        }
        self.assertEquals(price_cond(context), True)

    def test_failure(self):
        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "id": "value",
                    "type": "integer",
                    "operator": "greater",
                    "value": "1",
                },
                {
                    "id": "value",
                    "type": "integer",
                    "operator": "equal",
                    "value": "3",
                },
            ]
        }
        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': 2,
        }
        self.assertEquals(price_cond(context), False)

    def test_subconditions(self):
        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "condition": "OR",
                    "rules": [
                        {
                            "id": "value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "1",
                        },
                        {
                            "id": "value",
                            "type": "integer",
                            "operator": "equal",
                            "value": "3",
                        },
                    ]
                },
            ]
        }
        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': 2,
        }
        self.assertEquals(price_cond(context), True)

    def test_between(self):
        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "id": "value",
                    "type": "integer",
                    "operator": "between",
                    "value": ["1", "10"],
                },
            ]
        }
        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': 2,
        }
        self.assertEquals(price_cond(context), True)

    def test_negative_between(self):
        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "id": "value",
                    "type": "integer",
                    "operator": "between",
                    "value": ["10", "20"],
                },
            ]
        }
        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': 2,
        }
        self.assertEquals(price_cond(context), False)

    def test_datetime(self):
        value = datetime.datetime(2016, 2, 1)
        value_str = value.isoformat()

        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "id": "value",
                    "type": "datetime",
                    "operator": "less",
                    "value": (value + datetime.timedelta(days=2)).isoformat(),
                },
                {
                    "id": "value",
                    "type": "datetime",
                    "operator": "greater_or_equal",
                    "value": value_str,
                },
                {
                    "id": "value",
                    "type": "datetime",
                    "operator": "between",
                    "value": [(value - datetime.timedelta(days=2)).isoformat(),
                              (value + datetime.timedelta(days=2)).isoformat()],
                },
                {
                    "id": "value",
                    "type": "datetime",
                    "operator": "between",
                    "value": [value_str, value_str],
                },

            ]
        }

        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': value,
        }
        self.assertEquals(price_cond(context), True)

    def test_time(self):
        value = datetime.time(8, 00)
        value_str = value.isoformat()

        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "id": "value",
                    "type": "time",
                    "operator": "less",
                    "value": "09:00"
                },
                {
                    "id": "value",
                    "type": "time",
                    "operator": "greater_or_equal",
                    "value": "07:00",
                },
                {
                    "id": "value",
                    "type": "time",
                    "operator": "between",
                    "value": ["00:00", "12:00"],
                },
                {
                    "id": "value",
                    "type": "time",
                    "operator": "not_between",
                    "value": ["09:00", "19:00"],
                },

            ]
        }

        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': value,
        }
        self.assertEquals(price_cond(context), True)

    def test_backwards_conditions(self):
        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "id": "total_value",
                    "field": "total_value",
                    "type": "integer",
                    "operator": "greater",
                    "value": "1",
                },
            ]
        }
        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': 2,
            'total_value': 3
        }
        self.assertEquals(price_cond(context), True)
        self.assertEqual(price_cond.has_backwards(), True)

    def test_backwards_conditions_in_subconditions(self):
        example_condition = {
            "condition": "AND",
            "rules": [
                {
                    "condition": "OR",
                    "rules": [
                        {
                            "id": "value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "1",
                        },
                        {
                            "id": "total_value",
                            "type": "integer",
                            "operator": "equal",
                            "value": "3",
                        },
                    ]
                },
            ]
        }
        price_cond = RuleCondition({'rule': example_condition})

        price_cond.compile()
        context = {
            'value': 2,
            'total_value': 3
        }
        self.assertEquals(price_cond(context), True)
        self.assertEqual(price_cond.has_backwards(), True)

    def test_non_exists_value(self):
        test_conditions = [({
                                "condition": "AND",
                                "rules": [
                                    {
                                        "id": "value",
                                        "type": "boolean",
                                        "operator": "equal",
                                        "value": "true",
                                    },
                                ]
                            }, False),
            ({
                 "condition": "AND",
                 "rules": [
                     {
                         "id": "value",
                         "type": "boolean",
                         "operator": "equal",
                         "value": "false",
                     },
                 ]
             }, True)
        ]
        for cond, expect in test_conditions:
            price_cond = RuleCondition({'rule': cond})
            price_cond.compile()
            context = {}
            self.assertEquals(price_cond(context), expect)
