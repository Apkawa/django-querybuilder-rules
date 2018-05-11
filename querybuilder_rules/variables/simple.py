from collections import namedtuple

from django.utils.encoding import smart_text

from .base import BaseVariable

TypeVariableField = namedtuple('VariableOpts', ['title', 'help_text', 'choices', 'get_context'])


class SimpleTypeVariable(BaseVariable):
    type = None
    leaf = True

    def value(self):
        return self.type(self.instance)

    def get_context(self):
        return self.value()

    def get_fields(self):
        return {
            'value': TypeVariableField(self.title, self.help_text, None, self.get_context)
        }


class IntegerVariable(SimpleTypeVariable):
    type = int


class FloatVariable(SimpleTypeVariable):
    type = float


class TextVariable(SimpleTypeVariable):
    type = str


class BooleanVariable(SimpleTypeVariable):
    type = bool
