# coding: utf-8
from __future__ import unicode_literals

from .maps import CONDITIONS, TYPES, OPERATORS

# http://spacetelescope.github.io/understanding-json-schema/reference/object.html
DEFENITIONS_SCHEMA = {
    "price": {
        "type": "object",
        "required": ["value"],
        "additionalProperties": False,
        "properties": {
            "value": {
                "oneOf": [
                    {"type": "string"},
                ]
            },
            "title": {"type": "string"},
            "type": {
                "type": "string",
                "enum": ["decimal"],
            },
            "operation": {
                "type": "string",
                "enum": ["sum"]
            },
            "field": {"type": "string"}
        },
    },
    "error": {
        "type": "object",
        "required": ['message'],
        "properties": {
            "message": {'type': "string"},
            "fields": {"oneOf": [
                {"type": "null"},
                {"type": "array", "items": {"type": "string"}}
            ]},
        }

    },
    "rule_condition": {
        "type": "object",
        "properties": {
            "rule": {
                "$ref": "#/definitions/condition",
            }
        },
        "required": ['rule'],

    },
    "condition": {
        "type": "object",
        "required": [
            "condition",
            "rules"
        ],
        "properties": {
            "condition": {
                "type": "string",
                "enum": list(CONDITIONS.keys()),
            },
            "rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "oneOf": [
                        {"type": "object", "$ref": "#/definitions/condition"},
                        {"type": "object", "$ref": "#/definitions/rule"}
                    ]
                }
            }
        },
    },
    "rule": {
        "type": "object",
        "additionalProperties": True,
        "required": [
            "id",
            "type",
            "operator",
            "value",
        ],
        "properties": {
            "id": {"type": "string"},
            "field": {"type": "string"},
            "type": {
                "type": "string",
                "enum": list(TYPES.keys()),
            },
            "operator": {
                "type": "string",
                "enum": list(OPERATORS.keys()),
            },
            "value": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "null"},
                    {"type": "array",
                     "minItems": 2,
                     "maxItems": 2,
                     "additionalItems": False,
                     "items": {
                         "oneOf": [
                             {"type": "string",
                              "oneOf": [
                                  {"format": "date"},
                                  {"format": "date-time"},
                                  {"format": "time"},
                              ]},
                             {"type": "integer"},
                             {"type": "string", "regexp": "^\d+$"},
                         ]
                     }}
                ]
            }
        }
    }
}

CONDITION_SCHEMA = {
    "$ref": "#/definitions/condition",
    "definitions": DEFENITIONS_SCHEMA
}

PRICE_RULE_CONDITION_SCHEMA = {
    "type": "array",
    "items": {
        "allOf": [
            {"$ref": "#/definitions/rule_condition"},
            {
                "required": ['price'],
                "properties": {
                    "price": {"$ref": "#/definitions/price"},
                }
            }
        ]
    },
    "definitions": DEFENITIONS_SCHEMA,
}

VALIDATE_RULE_CONDITION_SCHEMA = {
    "type": "array",
    "items": {
        "allOf": [
            {"$ref": "#/definitions/rule_condition"},
            {
                "required": ['error'],
                "properties": {
                    "error": {"$ref": "#/definitions/error"},
                }
            }
        ]
    },
    "definitions": DEFENITIONS_SCHEMA,
}
