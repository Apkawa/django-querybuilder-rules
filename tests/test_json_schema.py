# coding: utf-8
from __future__ import unicode_literals

import unittest
from jsonschema import validate

from querybuilder_rules.json_schema import (
    CONDITION_SCHEMA,
    PRICE_RULE_CONDITION_SCHEMA,
    VALIDATE_RULE_CONDITION_SCHEMA
)


class JsonSchemaTestCase(unittest.TestCase):
    def test_condition_schema(self):
        ruleset = {
            "condition": "AND",
            "rules": [
                {
                    "id": "value",
                    "type": "integer",
                    "operator": "less",
                    "value": "4",
                },
            ],
        }

        self.assertIsNone(validate(ruleset, CONDITION_SCHEMA))

    def test_validate_rule_schema(self):
        """
        """
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
                "error": {
                    "message": "Вы не можете заказать меньше 4 яиц!"
                }
            },
        ]

        self.assertIsNone(validate(ruleset, VALIDATE_RULE_CONDITION_SCHEMA))

    def test_price_rule_schema(self):
        """
        """
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
                "price": {
                    "value": "200",
                    "type": "decimal",
                    "operation": "sum",
                }
            },
        ]

        self.assertIsNone(validate(ruleset, PRICE_RULE_CONDITION_SCHEMA))
