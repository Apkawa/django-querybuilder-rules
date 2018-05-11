# coding: utf-8
from __future__ import unicode_literals

import datetime
import json
import math

import six
from dateutil.parser import parse as parse_datetime

from django.template import Variable, VariableDoesNotExist
from .compat import smart_text

from .maps import OPTION_TYPE_CHOICES, UNDEFINED


def date_to_datetime(date):
    return datetime.datetime(*date.timetuple()[:-3])


def check_empty(value):
    if isinstance(value, six.string_types):
        return not value.strip()

    if isinstance(value, (tuple, list)):
        return any(map(check_empty, value))

    return not value


HOUR_TOTAL_SECONDS = 3600.0
DAY_TOTAL_SECONDS = HOUR_TOTAL_SECONDS * 24


def get_floor_days(td):
    total_seconds = td.total_seconds()
    if total_seconds > 60:
        total_seconds -= 60.0
    return int(math.floor(total_seconds / DAY_TOTAL_SECONDS) + 1)


def get_floor_hours(td):
    total_seconds = td.total_seconds()
    if total_seconds > 60:
        total_seconds -= 60
    return int(math.floor(total_seconds / HOUR_TOTAL_SECONDS) + 1)


def get_ceil_days(td):
    total_seconds = td.total_seconds()
    if total_seconds > 60:
        total_seconds -= 60.0
    return int(math.ceil((total_seconds / DAY_TOTAL_SECONDS)))


def get_ceil_hours(td):
    total_seconds = td.total_seconds()
    if total_seconds > 60:
        total_seconds -= 60
    return int(math.ceil((total_seconds / HOUR_TOTAL_SECONDS)))


class OptionValue(object):
    def __init__(self, value, value_type, base_price=None):
        """
        {
            type: choices of [quantity, time, date, datetime, place, bool],
            value: char, integer or range
        }
        :param value_data: dict
        :return:
        """

        self.value_type = value_type
        self._raw_value = value
        self.value = self.prepare_value(value, value_type)
        self._is_empty = check_empty(self.value)
        self.base_price = base_price

    @property
    def raw_value(self):
        return self._raw_value

    @property
    def is_empty(self):
        return self._is_empty

    def prepare_value(self, value, value_type):
        type_choices = OPTION_TYPE_CHOICES

        if value_type != type_choices.BOOL and check_empty(value):
            return None

        if value_type == type_choices.QUANTITY:
            return int(value)

        elif value_type == type_choices.DATE_RANGE:
            assert isinstance(value, list)
            return map(lambda v: parse_datetime(v).date(), value)

        elif value_type in (type_choices.DATETIME_RANGE_HOUR, type_choices.DATETIME_RANGE_DAY):
            assert isinstance(value, list)
            return map(lambda v: parse_datetime(v), value)

        elif value_type == type_choices.DATE:
            return parse_datetime(value).date()

        elif value_type == type_choices.DATETIME:
            return parse_datetime(value)

        elif value_type == type_choices.TIME:
            return parse_datetime(value).time()

        elif value_type == type_choices.BOOL:
            if isinstance(value, (list, tuple)):
                # Бага
                try:
                    value = value[0]
                except IndexError:
                    value = False

            if isinstance(value, six.string_types):
                try:
                    return bool(int(json.loads(value.lower().strip())))
                except ValueError:
                    pass
                    # Попытка не пытка, просто конвертируем в bool
                return bool(value.strip())
            return bool(value)

        elif value_type == type_choices.TEXT:
            return smart_text(value or '').strip()

        elif value_type == type_choices.SELECT:
            if isinstance(value, dict):
                return value.get('value') or value.get('label')
        return value

    def get_context_range(self):
        return self._get_context_range(self.value, self.value_type)

    def get_context(self):
        return self._get_context(self.value, self.value_type, is_group=True)

    def _get_context(self, value, value_type, is_group=False):
        type_choices = OPTION_TYPE_CHOICES

        if self.is_empty and value_type != OPTION_TYPE_CHOICES.BOOL:
            return {
                "value": None
            }

        if value_type == type_choices.DATE_RANGE:
            start_date, end_date = value

            td = end_date - start_date
            days = td.days + 1
            hours = get_ceil_hours(td) + 24

            _value = end_date
            if is_group:
                _value = start_date
            return {
                "value": _value,
                "date": _value,
                "start_date": start_date,
                "end_date": end_date,
                "days": days,
                "hours": hours,
            }

        elif value_type in (type_choices.DATETIME_RANGE_HOUR, type_choices.DATETIME_RANGE_DAY):
            start_dt, end_dt = value

            td = end_dt - start_dt
            days = get_floor_days(td)
            hours = get_floor_hours(td)

            _value = end_dt
            if is_group:
                _value = start_dt
            return {
                "value": _value,
                "datetime": _value,

                "time": _value.time(),
                "date": _value.date(),

                "days": days,
                "hours": hours,

                "start_datetime": start_dt,
                "end_datetime": end_dt,

            }

        elif value_type == type_choices.DATE:
            assert isinstance(value, datetime.date)
            return {
                "value": value,
                "date": value
            }

        elif value_type == type_choices.DATETIME:
            assert isinstance(value, datetime.datetime)
            return {
                "value": value,
                "datetime": value,
                "time": value.time(),
                "date": value.date()
            }

        elif value_type == type_choices.TIME:
            assert isinstance(value, datetime.time)
            return {
                "value": value,
                "time": value
            }
        elif value_type == type_choices.SELECT:
            return {
                "value": self.prepare_value(value, value_type)
            }

        return {
            "value": value
        }

    def _get_context_range(self, value, value_type):
        """
        * ``hours`` - Если тип - ``datetime`` - то это количество часов.
        * ``days`` - Если тип - ``datetime`` или ``date`` - это количество суток
        * ``time`` - Если тип - ``datetime`` или ``time`` - это время в 24 формате, для расчета ценовых границ в пределах суток

        :param value:
        :param value_type:
        :return:
        """
        type_choices = OPTION_TYPE_CHOICES

        if self.is_empty:
            raise StopIteration()

        if value_type == type_choices.QUANTITY:
            for i in range(1, value + 1):
                context = self._get_context(i, value_type)
                context.update({'total_value': value})
                yield context

        elif value_type == type_choices.DATE_RANGE:
            start_date, end_date = value
            td = end_date - start_date

            total_hours = int(td.total_seconds() / 60 ** 2)
            total_days = td.days + 1

            default_context = {'total_days': total_days, 'total_hours': total_hours}

            for days in range(0, int(total_days)):
                day = start_date + datetime.timedelta(days=days)
                context = self._get_context([start_date, day], value_type)

                context.update(default_context)
                yield context

        elif value_type == type_choices.DATETIME_RANGE_DAY:
            start_date, end_date = value
            td = end_date - start_date

            total_hours = get_floor_hours(td)
            total_days = get_floor_days(td)

            default_context = {'total_days': total_days, 'total_hours': total_hours}

            if total_hours <= 24:
                total_days = 1

            for days in range(0, int(total_days)):
                day = start_date + datetime.timedelta(days=days)
                context = self._get_context([start_date, day], value_type)
                context.update(default_context)

                t_day = start_date + datetime.timedelta(days=days, seconds=61)
                context.update({
                    'days': get_floor_days(t_day - start_date)
                })
                yield context

        elif value_type == type_choices.DATETIME_RANGE_HOUR:
            start_dt, end_dt = value
            td = end_dt - start_dt
            total_hours = get_floor_hours(td)
            total_days = get_floor_days(td)

            for hours in range(1, int(total_hours) + 1):
                dt = datetime.timedelta(hours=hours)
                day = start_dt + dt
                context = self._get_context([start_dt, day], value_type)
                context.update({
                    'total_days': total_days, 'total_hours': total_hours
                })
                yield context
        else:
            yield self._get_context(value, value_type)


class Context(object):
    def __init__(self, context):
        self.context_dict = context

    def resolve(self, variable):
        # todo may be cached resolve
        variable = Variable(variable).resolve(self.context_dict)
        return variable

    def to_dict(self):
        return dict(self.context_dict)

    def keys(self):
        return self.context_dict.keys()

    def items(self):
        return self.context_dict.items()

    def update(self, d):
        return self.context_dict.update(d)

    def __getitem__(self, item):
        try:
            res = self.resolve(item)
            if isinstance(res, dict):
                res = Context(res)
            return res
        except VariableDoesNotExist:
            return UNDEFINED

    def __getattr__(self, item):
        try:
            res = self.context_dict[item]
            if isinstance(res, dict):
                res = Context(res)
            return res
        except KeyError:
            try:
                self.__getattribute__(item)
            except AttributeError:
                return UNDEFINED
