# coding: utf-8
from __future__ import unicode_literals

import operator as op
from decimal import Decimal

from dateutil.parser import parse as parse_datetime, parserinfo

from django.utils.encoding import smart_text, smart_str

from jinja2 import DebugUndefined
from extended_choices import Choices


class ValueUndefined(DebugUndefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        try:
            super(ValueUndefined, self)._fail_with_undefined_error(*args, **kwargs)
        except self._undefined_exception as e:
            return e.message

    def _always_false(self, *args, **kwargs):
        return False

    def __or__(self, other):
        return self or other

    def __and__(self, other):
        return self and other

    __lt__ = __le__ = __gt__ = __ge__ = __int__ = _always_false


UNDEFINED = ValueUndefined()


def parse_bool(value):
    from .values import OptionValue
    ov = OptionValue(value, OPTION_TYPE_CHOICES.BOOL)
    return ov.value


TYPES = {
    'string': lambda v: smart_text(v or '').strip(),
    'integer': int,
    'double': float,
    'date': lambda v: parse_datetime(v, parserinfo=PARSER_INFO).date(),
    'time': lambda v: parse_datetime(v, parserinfo=PARSER_INFO).time(),
    'datetime': parse_datetime,
    'boolean': parse_bool
}

OPTION_TYPE_CHOICES = Choices(
    ['QUANTITY', 'quantity', 'Количество'],
    ['TIME', 'time', 'Время'],
    ['DATE', 'date', 'Дата'],
    ['DATETIME', 'datetime', 'Дата и время'],
    ['DATE_RANGE', 'date_range', 'Интервал дат'],
    ['DATETIME_RANGE_DAY', 'datetime_range_day', 'Интервал времени (сутки)'],
    ['DATETIME_RANGE_HOUR', 'datetime_range_hour', 'Интервал времени (часы)'],
    ['BOOL', 'bool', 'Опция'],
    ['TEXT', 'text', 'Текст'],
    ['DISPLAY_TEXT', 'display_text', 'Выводимый текст'],
    ['SELECT', 'select', 'Список с выбором'],
)

OPTION_TYPE_CHOICES.add_subset('DATE_TYPES', [
    'DATE',
    'DATETIME',
    'DATE_RANGE',
    'DATETIME_RANGE_DAY',
    'DATETIME_RANGE_HOUR',
])

OPTION_TYPE_CHOICES.add_subset('RANGE_TYPES', [
    'DATE_RANGE',
    'DATETIME_RANGE_DAY',
    'DATETIME_RANGE_HOUR',
])

BACKWARDS_FIELDS = {'total_hours', 'total_days', 'total_value'}

CONDITIONS = {
    "AND": op.and_,
    "OR": op.or_,
}


def time_between(_time, start_time, end_time):
    if start_time > end_time:
        # night
        return _time >= start_time or _time <= end_time

    elif start_time < end_time:
        # day
        return start_time <= _time <= end_time

    return _time == start_time


OPERATORS = {
    "equal": lambda value, test: op.eq(value, test),
    "not_equal": lambda value, test: op.not_(op.eq(value, test)),
    "in": lambda value, test: op.contains(test, value),
    "not_in": lambda value, test: op.not_(op.contains(test, value)),
    "greater": lambda value, test: op.gt(value, test),
    "less": lambda value, test: op.lt(value, test),
    "greater_or_equal": lambda value, test: op.ge(value, test),
    "less_or_equal": lambda value, test: op.le(value, test),
    "between": lambda value, a, b: (a <= value <= b),
    "not_between": lambda value, a, b: op.not_(a <= value <= b),
    "is_empty": lambda value: op.not_(value),
    "is_not_empty": lambda value: op.not_(op.not_(value)),
}

OPERATORS['is_not_null'] = OPERATORS['is_not_empty']
OPERATORS['is_null'] = OPERATORS['is_empty']

for name, func in OPERATORS.items():
    func.name = name

OPERATORS_FOR_TYPES = {
    "time": {
        "between": lambda value, a, b: time_between(value, a, b),
        "not_between": lambda value, a, b: op.not_(time_between(value, a, b)),
    },
    "boolean": {
        "equal": lambda value, test: op.eq(bool(value), bool(test)),
    }
}
PARSER_INFO = parserinfo(dayfirst=True)
