# coding: utf-8
from __future__ import unicode_literals

import unittest

from querybuilder_rules.maps import UNDEFINED
from querybuilder_rules import OPTION_TYPE_CHOICES
from querybuilder_rules.rules.validation import ValidateRule


class ValidationTestCase(unittest.TestCase):
    def test_generic(self):
        """

        Нельзя заказать меньше 4х и больше 20ти.
        Так же нельзя купить строго 13 штук - харам!
        :return:
        """

        value_type = OPTION_TYPE_CHOICES.QUANTITY

        ruleset = [
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "value",
                            "type": "integer",
                            "operator": "less",
                            "value": "4",
                        },
                    ],
                },
                "message": "Вы не можете заказать меньше 4 яиц!"
            },
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "20",
                        },
                    ],
                },
                "message": "Вы не можете заказать больше 20 яиц!"
            },
            {
                "rule": {

                    "condition": "AND",
                    "rules": [
                        {
                            "id": "value",
                            "type": "integer",
                            "operator": "equal",
                            "value": "13",
                        },
                    ],
                },
                "message": "Вы нарушаете харам!"
            },
        ]

        expected_results = [
            (1, [ruleset[0]['message']]),
            (4, []),
            (5, []),
            (20, []),
            (21, [ruleset[1]['message']]),
            (13, [ruleset[2]['message']]),

        ]

        validate_rule = ValidateRule(ruleset=ruleset)

        for value, expected_result in expected_results:
            result = validate_rule.validate(value=value, value_type=value_type)
            self.assertEquals(list(result), expected_result)

    def test_shipment(self):
        """
        Правила доставки

        1) Доставка не осуществляется в выходные
        2) Доставка не осуществляется в каждый 13 день месяца
        3) Доставка не осуществляется в период с 1го по 11 января.
        4) Доставка осуществляется в часы с 10 до 18


        :return:

        """
        value_type = OPTION_TYPE_CHOICES.DATETIME

        ruleset = [
            {
                "rule": {

                    "condition": "AND",
                    "rules": [
                        {
                            "id": "time",
                            "type": "time",
                            "operator": "not_between",
                            "value": ["10:00", "18:00"],
                        },
                    ],
                },
                "message": "Доставка осуществляется с 10 до 18"
            },
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "date.day",
                            "type": "integer",
                            "operator": "equal",
                            "value": "13",
                        },
                    ],

                },
                "message": "В 13 числах доставку не осуществляем"
            },
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "date.day",
                            "type": "integer",
                            "operator": "between",
                            "value": ["1", "10"],
                        },
                        {
                            "id": "date.month",
                            "type": "integer",
                            "operator": "equal",
                            "value": "1",
                        },

                    ],

                },
                "message": "C 1 по 10 января доставку не осуществляем",
            },
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "date.isoweekday",
                            "type": "integer",
                            "operator": "between",
                            "value": ["6", "7"],
                        },

                    ],

                },
                "message": "По выходным доставка не работает",
            },
        ]

        expected_results = [
            ("2016-01-12 21:00", [ruleset[0]['message']]),
            ("2016-01-13 10:00", [ruleset[1]['message']]),
            ("2016-01-13 21:00", [ruleset[0]['message'], ruleset[1]['message']]),

            ("2016-01-06 10:00", [ruleset[2]['message']]),
            ("2016-01-17 10:00", [ruleset[-1]['message']]),

            ("2016-01-12 10:00", []),

        ]

        validate_rule = ValidateRule(ruleset=ruleset)

        for value, expected_result in expected_results:
            result = validate_rule.validate(value=value, value_type=value_type)
            self.assertEquals(sorted(result), sorted(expected_result))

    def test_text_is_empty(self):
        value_type = OPTION_TYPE_CHOICES.TEXT

        ruleset = [
            {
                "rule": {

                    "condition": "AND",
                    "rules": [
                        {
                            "id": "value",
                            "field": 'value',
                            "type": "string",
                            "operator": "is_empty",
                        },
                    ],
                },
                "message": "текст"
            }]

        validate_rule = ValidateRule(ruleset=ruleset)
        result = validate_rule.validate(value='', value_type=value_type)

        self.assertEquals(sorted(result), [ruleset[0]['message']])

    def test_datetime_validate(self):
        value_type = OPTION_TYPE_CHOICES.DATE

        ruleset = [
            {
                "rule": {

                    "condition": "OR",
                    "rules": [
                        {
                            "id": "days",
                            "field": 'days',
                            "type": "date",
                            "value": ["2016-05-01", "2016-05-05"],
                            "operator": "between",
                        },
                        {
                            "id": "days",
                            "field": 'days',
                            "type": "date",
                            "operator": "is_empty",
                        },
                    ],
                },
                "message": "test dt"
            }]

        validate_rule = ValidateRule(ruleset=ruleset)
        result = validate_rule.validate(value=None, value_type=value_type)

        self.assertEquals(sorted(result), [ruleset[0]['message']])

    def test_datetime_empty_value(self):
        value_type = OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR

        ruleset = [
            {
                "id": 18,
                "rule": {
                    "rules": [
                        {
                            "value": "2",
                            "field": "hours",
                            "operator": "less_or_equal",
                            "input": "text",
                            "type": "integer",
                            "id": "hours"
                        }
                    ],
                    "condition": "AND"
                },
                "message": "Минимальный заказ 3 часа"
            },
        ]

        validate_rule = ValidateRule(ruleset=ruleset)
        for value in [None, ["", ""], UNDEFINED]:
            result = validate_rule.validate(value=value, value_type=value_type)

            self.assertEquals(sorted(result), [])
