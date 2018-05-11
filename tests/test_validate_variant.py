# coding: utf-8
from __future__ import unicode_literals

import unittest
from copy import copy

from querybuilder_rules import OPTION_TYPE_CHOICES
from querybuilder_rules.rules.validation import ValidateRule


class ValidationVariantTestCase(unittest.TestCase):
    maxDiff = None

    def test_text(self):
        """
        Проверка "встреча с табличкой"

        Если отмечена опция "Встреча с табличкой", то тогда "Текст таблички становится требуемым"

        """

        values_info = {
            '1': {
                'value': True,
                'type': OPTION_TYPE_CHOICES.BOOL,
            },
            '2': {
                'value': '',
                'type': OPTION_TYPE_CHOICES.TEXT
            }

        }

        ruleset = [
            {
                "rule": {
                    "rules": [
                        {
                            "value": "true",
                            "field": "1.value",
                            "operator": "equal",
                            "input": "radio",
                            "type": "boolean",
                            "id": "1.value"
                        },
                        {
                            "value": None,
                            "field": "2.value",
                            "operator": "is_empty",
                            "input": "text",
                            "type": "string",
                            "id": "2.value"
                        }
                    ],
                    "condition": "AND"
                },
                "to_options": [
                    "2"
                ],
                "message": "Требуется заполнить"
            }
        ]
        validate_rule = ValidateRule(ruleset=ruleset)
        result = validate_rule.validate_group(values_info)

        self.assertEquals(result, {'2': [ruleset[0]['message']]})

    def test_generic(self):
        """
        Проверка заполнения варианта.

        Есть следующие поля - аренда стульев

        [1] Длительность аренды - 2 даты
        [2] Количество  стульев
        [3] Опция - доставка стульев

        Правила:

        1) Если стулья заказываются на длительный срок от 20 дней - то больше 10 стульев нельзя
        2) Доставка стульев осуществляется до 30 стульев, больше - только самовывоз своими силами.

        :return:
        """

        values_info = {
            'rent_period': {
                "value": None,
                "type": OPTION_TYPE_CHOICES.DATE_RANGE
            },
            'quantity': {
                "value": None,
                "type": OPTION_TYPE_CHOICES.QUANTITY,
            },
            'ship': {
                "value": None,
                "type": OPTION_TYPE_CHOICES.BOOL
            }
        }

        ruleset = [
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "rent_period.days",
                            "type": "integer",
                            "operator": "greater",
                            "value": "20",
                        },
                        {
                            "id": "quantity.value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "10",
                        },
                    ],

                },
                "message": "Больше 10 стульев на срок от 20 дней нельзя заказать!",
                "to_options": ["rent_period", "quantity"]
            },
            {
                "rule": {

                    "condition": "AND",
                    "rules": [
                        {
                            "id": "quantity.value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "30",
                        },
                        {
                            "id": "ship.value",
                            "type": "boolean",
                            "operator": "equal",
                            "value": "true",
                        },
                    ],
                },
                "message": "Мы можем доставить только до 30 стульев",
                "to_options": ["ship", "quantity"]
            },
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "quantity.value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "1000",
                        },
                    ],

                },
                "message": "Мы не можем принять такой заказ. Вы что, охуели?",
            },
        ]

        expected_results = [
            (
                {"rent_period": ["2016-01-01", "2016-01-22"], "quantity": 30},
                {
                    "rent_period": [ruleset[0]['message']],
                    "quantity": [ruleset[0]['message']]
                }
            ),
            (
                {"rent_period": ["2016-01-01", "2016-01-10"], "quantity": 45, "ship": True},
                {
                    "quantity": [ruleset[1]['message'], ],
                    "ship": [ruleset[1]['message'], ]
                }
            ),
            (
                {"rent_period": ["2016-01-01", "2016-01-10"], "quantity": 30},
                {
                }
            ),
            (
                {"rent_period": ["2016-01-01", "2016-01-22"], "quantity": 45, "ship": True},
                {
                    "rent_period": [ruleset[0]['message']],
                    "quantity": [ruleset[1]['message'], ruleset[0]['message'], ],
                    "ship": [ruleset[1]['message'], ]
                }
            ),
            (
                {"rent_period": ["2016-01-01", "2016-01-10"], "quantity": 10000},
                {
                    "__all__": [ruleset[-1]['message']],
                    "quantity": [ruleset[1]['message'], ],
                    "ship": [ruleset[1]['message'], ]
                }
            ),
            (
                {"rent_period": None, "quantity": None},
                {}
            ),
            (
                {"rent_period": ["", ""], "quantity": None},
                {}
            ),

        ]

        validate_rule = ValidateRule(ruleset=ruleset)

        for value_dict, expected_result in expected_results:
            _value_data = copy(values_info)
            for field, value in value_dict.items():
                _value_data[field]['value'] = value

            result = validate_rule.validate_group(_value_data)

            self.assertEquals(result, expected_result)

    def _test_with_more_dt(self):
        """
        Кейс на воспроизведение бага

        """

        values_info = {
            '1': {
                'value': True,
                'type': OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR,
            },
            '2': {
                'value': '',
                'type': OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR,
            }

        }

        ruleset = [
            {
                "rule": {
                    "rules": [
                    ],
                    "condition": "AND"
                },
                "to_options": [
                    "2"
                ],
                "message": "Требуется заполнить"
            }
        ]
        validate_rule = ValidateRule(ruleset=ruleset)
        result = validate_rule.validate_group(values_info)

        self.assertEquals(result, {'2': [ruleset[0]['message']]})
