from querybuilder_rules.variables.base import BaseVariable

from querybuilder_rules.variables.simple import (
    FloatVariable, IntegerVariable, BooleanVariable,
    TextVariable
)


def test_decorate_field():
    class CustomVariable(BaseVariable):
        @FloatVariable.d()
        def total(self):
            return 1000.5

    var = CustomVariable(None)
    total = var.total()
    assert isinstance(total, FloatVariable)
    assert total.value() == 1000.5
    assert var.get_fields()['total'].func()
    assert var.get_context() == {'total': 1000.5}


def test_custom_variable():
    class CustomVariable(BaseVariable):
        @FloatVariable.d()
        def total(self):
            return 1000.5

        @BooleanVariable.d()
        def is_active(self):
            return True

        @IntegerVariable.d()
        def quantity(self):
            return 20

    var = CustomVariable(None)
    assert var.get_fields().keys()
    assert var.get_context() == {
        'total': 1000.5,
        'quantity': 20,
        'is_active': True,
    }


def test_nested_variable():
    class NestedVariable(BaseVariable):
        @IntegerVariable.d()
        def quantity(self):
            return self.instance['quantity']

        @FloatVariable.d()
        def price(self):
            return self.instance['price']

    class CustomVariable(BaseVariable):
        @FloatVariable.d()
        def total(self):
            return 1000.5

        @NestedVariable.d()
        def nested(self):
            return {
                "quantity": 20,
                "price": 1235.40

            }

    var = CustomVariable(None)
    assert var.get_fields().keys()
    assert var.get_context() == {
        "nested": {
            "price": 1235.40,
            'quantity': 20,
        },
        'total': 1000.5,
    }


def test_nested_list_variable():
    class NestedVariable(BaseVariable):
        @IntegerVariable.d()
        def quantity(self):
            return self.instance['quantity']

        @FloatVariable.d()
        def price(self):
            return self.instance['price']

    class CustomVariable(BaseVariable):
        @FloatVariable.d()
        def total(self):
            return 1000.5

        @NestedVariable.d(many=True)
        def nested_list(self):
            return [
                {
                    "quantity": 20,
                    "price": 1235.40
                },
                {
                    "quantity": 1,
                    "price": 1.40
                }
            ]

    var = CustomVariable(None)
    assert var.get_fields().keys()
    assert var.get_context() == {
        "nested_list": [
            {
                "quantity": 20,
                "price": 1235.40
            },
            {
                "quantity": 1,
                "price": 1.40
            }
        ],
        'total': 1000.5,
    }
