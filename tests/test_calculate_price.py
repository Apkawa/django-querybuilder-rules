# coding: utf-8
from __future__ import unicode_literals

from querybuilder_rules import OPTION_TYPE_CHOICES
from querybuilder_rules.rules.price import PriceRule


def test_generic():
    """

    Простое правило вида

    Количество.

    до 10 штук - 250р
    до 50 штук - 200р
    до 100 штук - 100р
    от 100 штук - 50р



    :return:
    """
    value = 150
    base_price = 250
    value_type = OPTION_TYPE_CHOICES.QUANTITY
    expect_total_price = ((10 * 250)
                          + ((50 - 10) * 200)
                          + ((100 - 50) * 100)
                          + ((value - 100) * 50)
                          )

    ruleset = [
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "value",
                        "type": "integer",
                        "operator": "between",
                        "value": ["11", "50"],
                    },
                ],
            },
            "price": "200",
        },
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "value",
                        "type": "integer",
                        "operator": "between",
                        "value": ["51", "100"],
                    },
                ],
            },
            "price": "100",
        },
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "value",
                        "type": "integer",
                        "operator": "greater",
                        "value": "100",
                    },
                ],
            },
            "price": "50",
        },
    ]

    price_rule = PriceRule(ruleset=ruleset)

    result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                 base_price=base_price)

    assert result == expect_total_price


def test_formulas():
    """
    Тест использования формул вместо цен

    :return:
    """
    value = 150
    base_price = 250
    value_type = OPTION_TYPE_CHOICES.QUANTITY
    expect_total_price = value * (base_price - 42)

    ruleset = [
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "value",
                        "type": "integer",
                        "operator": "greater",
                        "value": 0,
                    },
                ],
            },
            "price": "bp - 42",
        },
    ]

    price_rule = PriceRule(ruleset=ruleset)

    result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                 base_price=base_price)

    assert result == expect_total_price


def test_change_base_price():
    """

    Тест использования правил на изменение базовой цены (объемная скидка)

    :return:
    """
    value = 150
    base_price = 250
    value_type = OPTION_TYPE_CHOICES.QUANTITY
    expect_total_price = value * (base_price - 42)

    ruleset = [
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "total_value",
                        "field": "total_value",
                        "type": "integer",
                        "operator": "greater",
                        "value": 100,
                    },
                ],
            },
            "price": "bp - 42",
        },
    ]

    price_rule = PriceRule(ruleset=ruleset)

    result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                 base_price=base_price)

    assert result == expect_total_price


def test_generic_rent_car():
    """

    Простое правило аренды

    Аренда почасовая

    Дневной тариф - с 9 до 18 - 400 руб
    Ночной тариф - с 18 до 9 - 600 руб

    Арендуем с 2016-01-01 09:00 по 2016-01-02 19:00

    :return:
    """
    value_type = OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR

    base_price = None

    ruleset = [
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "time",
                        "type": "time",
                        "operator": "between",
                        "value": ["09:01", "18:00"],
                    },
                ],
            },
            "price": "400",
        },
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "time",
                        "type": "time",
                        "operator": "not_between",
                        "value": ["09:01", "18:00"],
                    },
                ],
            },
            "price": "600",
        },
    ]

    price_rule = PriceRule(ruleset=ruleset)

    expected = [
        (
            ['2016-01-01 09:00', '2016-01-01 10:00'],
            (
                (1 * 400)
            )
        ),
        (
            ['2016-01-01 09:00', '2016-01-01 18:00'],
            (
                (9 * 400)
            )
        ),
        (
            ['2016-01-01 09:00', '2016-01-01 19:00'],
            (
                (9 * 400)
                + (1 * 600)
            )
        ),
        (
            ['2016-01-01 18:00', '2016-01-02 9:00'],
            (
                + (14 * 600)  # 8400
            )
        ),
        (
            ['2016-01-01 09:00', '2016-01-02 19:00'],
            (
                # 2016-01-01 09:00 - 2016-01-01 18:00
                (9 * 400)  # 3600
                # 2016-01-01 18:00 - 2016-01-02 09:00
                + (14 * 600)  # 9000
                # 2016-01-02 09:00 - 2016-01-02 18:00
                + (9 * 400)  # 3600
                # 2016-01-02 18:00 - 2016-01-02 19:00
                + (1 * 600)  # 600
            )
        )
    ]

    for value, expect_total in expected:
        result, explain = price_rule.calculate_price(value=value,
                                                     value_type=value_type,
                                                     base_price=base_price
                                                     )

        assert result == expect_total


def test_empty_rule():
    """
    Случай, когда нет каких либо правил, а есть только базовая цена.
    Стоимость тогда считается как quantity * base_price

    :return:
    """
    value = 150
    base_price = 250
    value_type = OPTION_TYPE_CHOICES.QUANTITY
    expect_total_price = value * base_price

    price_rule = PriceRule(ruleset=[])

    result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                 base_price=base_price)

    assert result == expect_total_price


def test_empty_datetime_rule():
    base_price = 250
    value = [
        '2016-01-01 09:00', '2016-01-02 19:00'
    ]
    value_type = OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR
    price_rule = PriceRule(ruleset=[])
    result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                 base_price=base_price)
    assert result == 34 * base_price


def test_non_iso_datetime_rule():
    base_price = 250
    value = [
        '01.01.2016 09:00', '02.01.2016 19:00'
    ]
    value_type = OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR
    price_rule = PriceRule(ruleset=[])
    result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                 base_price=base_price)
    assert result == (34 * base_price)


def test_empty_option():
    empty_value_types = [
        [False, OPTION_TYPE_CHOICES.BOOL]
    ]

    price_rule = PriceRule(ruleset=[])
    for value, value_type in empty_value_types:
        result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                     base_price=100500)

        assert result == 0


def test_generic_rent_car_buggy():
    """

    Простое правило аренды

    Аренда почасовая

    Дневной тариф - с 9 до 18 - 400 руб
    Ночной тариф - с 18 до 9 - 600 руб

    Арендуем с 2016-01-01 09:00 по 2016-01-02 19:00

    :return:
    """
    value_type = OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR

    base_price = None

    ruleset = [
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "time",
                        "type": "time",
                        "operator": "between",
                        "value": ["09:01", "18:00"],
                    },
                ],
            },
            "price": "400",
        },
        {
            "rule": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "time",
                        "type": "time",
                        "operator": "not_between",
                        "value": ["09:01", "18:00"],
                    },
                ],
            },
            "price": "600",
        },
    ]

    price_rule = PriceRule(ruleset=ruleset)

    expected = [
        (
            ['2016-01-01 18:00', '2016-01-02 9:00'],
            (
                + (14 * 600)  # 8400
            )
        ),
    ]

    for value, expect_total in expected:
        result, explain = price_rule.calculate_price(value=value, value_type=value_type,
                                                     base_price=base_price)

        assert result == expect_total
