# coding: utf-8
from __future__ import unicode_literals

import unittest
from copy import copy

from querybuilder_rules import OPTION_TYPE_CHOICES
from querybuilder_rules.rules.price import PriceRule


class PriceCalculationTestCase(unittest.TestCase):
    def test_generic(self):
        """
        Для варианта считаются комбинированые опции, скорее всего редко будет использоватьтся,
        но может использоваться в комбинации с с выражениями,

         По умолчанию проще всего считать для опций, которые могут зависеть от остальных выражений.


        Дано:

        Есть следующие поля - аренда стульев

        [1] Количество  стульев
        [2] Опция - доставка стульев, максимум 30 стульев

        Правила:

        1) Стоимость опции доставки увеличвается от стоимости количества доставки по следующим критериям
            до 5 стульев - базовая цена доставки
            до 10 - +200р (>5)
            до 20 - +300р (>10)
            от 21 - +400р.

        :return:
        """

        values_info = {
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
                            "id": "quantity.value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "20",
                        },
                        {
                            "id": "ship.value",
                            "type": "boolean",
                            "operator": "equal",
                            "value": "true",
                        },
                    ],
                },
                "price": "400",
                "to_option": "ship",
            },
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "quantity.value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "10",
                        },
                        {
                            "id": "ship.value",
                            "type": "boolean",
                            "operator": "equal",
                            "value": "true",
                        },
                    ],

                },
                "price": "300",
                "to_option": "ship",
            },
            {
                "rule": {
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "quantity.value",
                            "type": "integer",
                            "operator": "greater",
                            "value": "5",
                        },
                        {
                            "id": "ship.value",
                            "type": "boolean",
                            "operator": "equal",
                            "value": "true",
                        },
                    ],

                },
                "price": "200",
                "to_option": "ship",
            },
        ]

        expected_results = [
            (
                {"quantity": 30, "ship": True},
                {"ship": 400}
            ),
            (
                {"quantity": 20, "ship": True},
                {"ship": 300}
            ),
            (
                {"quantity": 10, "ship": True},
                {"ship": 200}
            ),
            (
                {"quantity": 5, "ship": True},
                {None: 0}
            ),
            (
                {"quantity": 1, "ship": True},
                {None: 0}
            ),

        ]

        price_rule = PriceRule(ruleset=ruleset)

        for value_dict, expected_result in expected_results:
            _value_data = copy(values_info)
            for field, value in value_dict.items():
                _value_data[field]['value'] = value

            result, explain = price_rule.calculate_group_price(_value_data)

            self.assertEquals(result, expected_result)

    def test_price_calculation(self):
        """
        Нужна возможность внутри варианта использовать формулы со ссылкой на результат другой ценовой опции.

        Например, опция "Навигатор" должна иметь стоимость:
        N р. * [количество получившихся суток в ценовой позиции "интервал времени(сутки)"]
        :return:
        """

        RENT_OPT = '11'
        NAV_OPT = '12'

        values_info = {
            NAV_OPT: {
                "value": None,
                "type": OPTION_TYPE_CHOICES.BOOL,
            },
            RENT_OPT: {
                "value": None,
                "type": OPTION_TYPE_CHOICES.DATETIME_RANGE_DAY
            }
        }

        ruleset = [
            {
                "rule": {

                    "condition": "AND",
                    "rules": [
                        {
                            "id": "11.value",
                            "type": "time",
                            "operator": "is_not_empty",
                        },
                        {
                            "id": "12.value",
                            "type": "boolean",
                            "operator": "equal",
                            "value": "true",
                        },
                    ],
                },
                "price": "100 * o_11.days",
                "to_option": "12",
            },
        ]

        expected_results = [
            (
                {"11": ['2016-01-01 05:00', '2016-01-13 05:01'], "12": True},
                {"12": 100 * 13}
            ),
            (
                {"11": ['2016-01-01 05:00', '2016-01-13 05:00'], "12": True},
                {"12": 100 * 12}
            ),
            (
                {"11": ['2016-01-01 05:00', '2016-01-13 04:00'], "12": False},
                {None: 0}
            ),
        ]

        price_rule = PriceRule(ruleset=ruleset)

        for value_dict, expected_result in expected_results:
            _value_data = copy(values_info)
            for field, value in value_dict.items():
                _value_data[field]['value'] = value

            result, explain = price_rule.calculate_group_price(_value_data)

            self.assertEquals(result, expected_result)

    def test_variant_calculation(self):
        """
        Поиск бага
        :return:
        """
        null = None

        values_info = {
            27253: {u'type': u'datetime_range_day', u'value': None},
            27515: {u'type': u'text', u'value': None},
            27516: {u'type': u'text', u'value': None},
            27517: {u'type': u'bool', u'value': None},
            27518: {u'type': u'bool', u'value': None},
            27519: {u'type': u'bool', u'value': None},
            27520: {u'type': u'bool', u'value': None}
        }
        ruleset = [
            {
                "id": 6,
                "rule": {
                    "rules": [
                        {
                            "value": null,
                            "field": "27253.datetime",
                            "operator": "is_not_null",
                            "input": "text",
                            "type": "datetime",
                            "id": "27253.datetime"
                        },
                        {
                            "value": [
                                "true"
                            ],
                            "field": "27520.value",
                            "operator": "equal",
                            "input": "checkbox",
                            "type": "boolean",
                            "id": "27520.value"
                        }
                    ],
                    "condition": "AND"
                },
                "title": "Цена навигатора на период аренды",
                "price": "300 * o_27253.days",
                "order": 1000,
                "to_option": 27520
            },
            {
                "id": 7,
                "rule": {
                    "rules": [
                        {
                            "value": null,
                            "field": "27253.datetime",
                            "operator": "is_not_null",
                            "input": "text",
                            "type": "datetime",
                            "id": "27253.datetime"
                        },
                        {
                            "value": [
                                "true"
                            ],
                            "field": "27518.value",
                            "operator": "equal",
                            "input": "checkbox",
                            "type": "boolean",
                            "id": "27518.value"
                        }
                    ],
                    "condition": "AND"
                },
                "title": "Цена автокресла на период аренды",
                "price": "350 * o_27253.days",
                "order": 1000,
                "to_option": 27518
            },
            {
                "id": 8,
                "rule": {
                    "rules": [
                        {
                            "value": null,
                            "field": "27253.datetime",
                            "operator": "is_not_null",
                            "input": "text",
                            "type": "datetime",
                            "id": "27253.datetime"
                        },
                        {
                            "value": [
                                "true"
                            ],
                            "field": "27519.value",
                            "operator": "equal",
                            "input": "checkbox",
                            "type": "boolean",
                            "id": "27519.value"
                        }
                    ],
                    "condition": "AND"
                },
                "title": "Цена автолюльки на период аренды",
                "price": "250 * o_27253.days",
                "order": 1000,
                "to_option": 27519
            },
            {
                "id": 9,
                "rule": {
                    "rules": [
                        {
                            "value": null,
                            "field": "27253.datetime",
                            "operator": "is_not_null",
                            "input": "text",
                            "type": "datetime",
                            "id": "27253.datetime"
                        },
                        {
                            "value": [
                                "true"
                            ],
                            "field": "27517.value",
                            "operator": "equal",
                            "input": "checkbox",
                            "type": "boolean",
                            "id": "27517.value"
                        }
                    ],
                    "condition": "AND"
                },
                "title": "Цена за дополнительного водителя на период аренды",
                "price": "317 * o_27253.days",
                "order": 1000,
                "to_option": 27517
            }
        ]

        expected_results = [
            (
                {27253: [u'2016-05-24T16:00', u'2016-05-24T16:00'],
                 27515: u'',
                 27516: u'',
                 27517: False,
                 27519: False,
                 27518: True,
                 27520: True
                 },
                {27520: 300, 27518: 350}
            ),
            (
                {27253: [u'2016-05-24T16:00', u'2016-05-26T16:01'],
                 27515: u'',
                 27516: u'',
                 27517: False,
                 27519: False,
                 27518: True,
                 27520: True
                 },
                {27520: 300 * 3, 27518: 350 * 3}
            ),
            (
                {27253: [u'2016-05-24T16:00', u'2016-05-26T16:00'],
                 27515: u'',
                 27516: u'',
                 27517: False,
                 27519: False,
                 27518: True,
                 27520: True
                 },
                {27520: 300 * 1, 27518: 350 * 1}
            ),
        ]

        price_rule = PriceRule(ruleset=ruleset)

        for value_dict, expected_result in expected_results:
            _value_data = copy(values_info)
            for field, value in value_dict.items():
                _value_data[field]['value'] = value

            result, explain = price_rule.calculate_group_price(_value_data)

            self.assertEquals(result, expected_result)

    def test_service_1791(self):
        """
        Проблема в граничных условиях 23:00-00:00 - час подачи
        :return:
        """

        ruleset = [
            {
                "id": 2384,
                "rule": {
                    "rules": [
                        {
                            "value": [
                                "06:00",
                                "23:00"
                            ],
                            "field": "27526.time",
                            "operator": "between",
                            "input": "text",
                            "type": "time",
                            "id": "27526.time"
                        },
                        {
                            "value": [
                                "true"
                            ],
                            "field": "27528.value",
                            "operator": "equal",
                            "input": "checkbox",
                            "type": "boolean",
                            "id": "27528.value"
                        }
                    ],
                    "condition": "AND"
                },
                "title": "Дневной тариф",
                "price": "700",
                "order": 1000,
                "to_option": 27528
            },
            {
                "id": 2383,
                "rule": {
                    "rules": [
                        {
                            "value": [
                                "23:00",
                                "06:00",
                            ],
                            "field": "27526.time",
                            "operator": "between",
                            "input": "text",
                            "type": "time",
                            "id": "27526.time"
                        },
                        {
                            "value": [
                                "true"
                            ],
                            "field": "27528.value",
                            "operator": "equal",
                            "input": "checkbox",
                            "type": "boolean",
                            "id": "27528.value"
                        }
                    ],
                    "condition": "AND"
                },
                "title": "Ночной тариф",
                "price": "945",
                "order": 1000,
                "to_option": 27528
            }
        ]

        values_info = {
            27526: {
                "type": "datetime_range_hour",
            },
            27528: {"type": "bool"},
        }

        expected_results = [
            ({
                 27526: ["2016-05-27T23:00", "2016-05-28T00:00"],
                 27528: True,
             }, {27528: 700}
            ),
            ({
                 27526: ["2016-05-27T23:01", "2016-05-28T00:00"],
                 27528: True,
             }, {27528: 945}),
            ({
                 27526: ["2016-05-27T01:00", "2016-05-28T01:00"],
                 27528: True,
             }, {27528: 945}
            ),
            ({
                 27526: ["2016-05-27T23:01", "2016-05-28T07:00"],
                 27528: True,
             }, {27528: 945}
            ),
        ]

        ruleset = PriceRule(ruleset=ruleset)

        for value_dict, expected_result in expected_results:
            _value_data = copy(values_info)
            for field, value in value_dict.items():
                _value_data[field]['value'] = value

            result, explain = ruleset.calculate_group_price(_value_data)

            self.assertEquals(result, expected_result, [result, expected_result, value_dict])
