# coding: utf-8
from __future__ import unicode_literals

import datetime
import unittest

from querybuilder_rules import OPTION_TYPE_CHOICES
from querybuilder_rules.values import OptionValue, Context


class OptionValueTestCase(unittest.TestCase):
    def test_generic(self):
        option_value = OptionValue("20", OPTION_TYPE_CHOICES.QUANTITY)
        self.assertEquals(option_value.get_context(), {'value': 20})
        ctx_range = list(option_value.get_context_range())
        self.assertEquals(len(ctx_range), 20)
        self.assertEquals(ctx_range[0]['value'], 1)
        self.assertEquals(ctx_range[19]['value'], 20)

    def test_date(self):
        date = datetime.datetime(2016, 1, 1).date()
        option_value = OptionValue(date.isoformat(), OPTION_TYPE_CHOICES.DATE)
        self.assertEquals(option_value.get_context(), {'value': date, "date": date})
        ctx_range = list(option_value.get_context_range())
        self.assertEquals(len(ctx_range), 1)
        self.assertEquals(ctx_range[0]['value'], date)

    def test_datetime(self):
        date = datetime.datetime(2016, 1, 1, 15, 16, 1)
        option_value = OptionValue(date.isoformat(), OPTION_TYPE_CHOICES.DATETIME)
        self.assertEquals(option_value.get_context(), {
            'value': date,
            'datetime': date,
            "date": date.date(),
            "time": date.time()
        })
        ctx_range = list(option_value.get_context_range())
        self.assertEquals(len(ctx_range), 1)
        self.assertEquals(ctx_range[0]['value'], date)

    def test_time(self):
        date = datetime.datetime(2016, 1, 1, 15, 16, 1).time()
        option_value = OptionValue(date.isoformat(), OPTION_TYPE_CHOICES.TIME)
        self.assertEquals(option_value.get_context(), {'value': date, "time": date})
        ctx_range = list(option_value.get_context_range())
        self.assertEquals(len(ctx_range), 1)
        self.assertEquals(ctx_range[0]['value'], date)

    def test_bool(self):
        bool_variants = {
            True: ["1", '"1"', 'True', 'true', 'anystring', '"anystring"', ['true']],
            False: ["", "    ", '    0   ', "0", '"0"', 'False', 'false', None, ['false'], []],

        }
        for _bool, value_inputs in bool_variants.items():
            for v in value_inputs:
                option_value = OptionValue(v, OPTION_TYPE_CHOICES.BOOL)

                self.assertEquals(option_value.prepare_value(v, OPTION_TYPE_CHOICES.BOOL), _bool)
                self.assertEquals(option_value.get_context(), {'value': _bool})

                ctx_range = list(option_value.get_context_range())
                if _bool:
                    self.assertEquals(len(ctx_range), 1)
                    self.assertEquals(ctx_range[0]['value'], _bool)
                else:
                    self.assertEquals(len(ctx_range), 0)

    def test_text(self):
        text_value = "123123"
        option_value = OptionValue(text_value,
                                   OPTION_TYPE_CHOICES.TEXT)
        self.assertEqual(option_value.get_context(), {'value': text_value})

    def test_empty_text(self):
        possible_empty_text_values = ["", None, '     ']

        for text_value in possible_empty_text_values:
            option_value = OptionValue(text_value,
                                       OPTION_TYPE_CHOICES.TEXT)
            self.assertEqual(option_value.get_context(), {'value': None})


class DateTimeRangeTestCase(unittest.TestCase):
    maxDiff = None

    def test_date_range(self):
        start_date = datetime.datetime(2016, 1, 1).date()
        end_date = datetime.datetime(2016, 1, 20).date()

        option_value = OptionValue([start_date.isoformat(), end_date.isoformat()],
                                   OPTION_TYPE_CHOICES.DATE_RANGE)
        self.assertEquals(option_value.get_context(), {
            'value': start_date,
            "date": start_date,
            "start_date": start_date,
            "end_date": end_date,
            "days": 20,
            "hours": 20 * 24
        }
                          )
        ctx_range = list(option_value.get_context_range())
        self.assertEquals(len(ctx_range), 20)
        self.assertEquals(ctx_range[0]['value'], start_date + datetime.timedelta(days=0))
        self.assertEquals(ctx_range[0]['days'], 1)
        self.assertEquals(ctx_range[1]['days'], 2)
        self.assertEquals(ctx_range[3]['value'], start_date + datetime.timedelta(days=3))
        self.assertEquals(ctx_range[-1]['value'], end_date)

    def test_datetime_hour_range(self):
        start_date = datetime.datetime(2016, 1, 1)
        end_date = datetime.datetime(2016, 1, 20, 12, 0, 0)

        option_value = OptionValue(
            [start_date.isoformat(), end_date.isoformat()],
            OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR)
        expected_context = {
            'value': start_date,
            'datetime': start_date,
            "date": start_date.date(),
            "time": start_date.time(),
            "start_datetime": start_date,
            "end_datetime": end_date,
            "days": 20,
            "hours": (19 * 24) + 12,
        }
        self.assertEquals(option_value.get_context(), expected_context)
        ctx_range = list(option_value.get_context_range())

        self.assertEquals(len(ctx_range), expected_context['hours'])
        self.assertEquals(ctx_range[0]['value'], start_date + datetime.timedelta(hours=1))
        self.assertEquals(ctx_range[(4 * 24) - 1]['value'], start_date + datetime.timedelta(days=4))
        self.assertEquals(ctx_range[-1]['value'], end_date)

    def test_datetime_days_range(self):
        start_date = datetime.datetime(2016, 1, 1)
        end_date = datetime.datetime(2016, 1, 20)

        option_value = OptionValue([start_date.isoformat(), end_date.isoformat()],
                                   OPTION_TYPE_CHOICES.DATETIME_RANGE_DAY)

        expected_context = {'value': start_date, "datetime": start_date, "date": start_date.date(),
                            "time": start_date.time(),
                            "start_datetime": start_date, "end_datetime": end_date, "days": 19,
                            'hours': 19 * 24}

        self.assertEquals(option_value.get_context(), expected_context
                          )
        ctx_range = list(option_value.get_context_range())
        self.assertEquals(len(ctx_range), expected_context['days'])
        self.assertEquals(ctx_range[0]['value'], start_date + datetime.timedelta(days=0))
        self.assertEquals(ctx_range[0]['days'], 1)
        self.assertEquals(ctx_range[1]['days'], 2)
        self.assertEquals(ctx_range[3]['value'], start_date + datetime.timedelta(days=3))
        self.assertEquals(ctx_range[-1]['value'], end_date - datetime.timedelta(days=1))
        self.assertEquals(ctx_range[-1]['days'], 19)

    def test_datetime_days_range_half_day(self):
        start_date = datetime.datetime(2016, 1, 1)
        end_date = datetime.datetime(2016, 1, 20, 12, 0, 0)

        option_value = OptionValue([start_date.isoformat(), end_date.isoformat()],
                                   OPTION_TYPE_CHOICES.DATETIME_RANGE_DAY)
        expected_context = {'value': start_date,
                            "datetime": start_date,
                            "date": start_date.date(),
                            "time": start_date.time(),
                            "start_datetime": start_date,
                            "end_datetime": end_date,
                            "days": 20,
                            'hours': (19 * 24) + 12}
        self.assertEquals(option_value.get_context(), expected_context
                          )
        ctx_range = list(option_value.get_context_range())
        self.assertEquals(len(ctx_range), 20)
        self.assertEquals(ctx_range[0]['value'], start_date + datetime.timedelta(days=0))
        self.assertEquals(ctx_range[3]['value'], start_date + datetime.timedelta(days=3))
        self.assertEquals(ctx_range[-1]['value'], end_date.replace(hour=0))

    def test_datetime_days_border_values(self):

        test_cases = [
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 1, 15, 0, 0)],
                {"days": 1, 'hours': 1}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 1, 16, 0, 0)],
                {"days": 1, 'hours': 1}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 1, 16, 1, 0)],
                {"days": 1, 'hours': 2}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 2, 15, 0, 0)],
                {"days": 1, 'hours': 24}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 2, 15, 1, 0)],
                {"days": 2, 'hours': 25}
            ),
        ]

        for (start_date, end_date), expect in test_cases:
            option_value = OptionValue(
                [start_date.isoformat(), end_date.isoformat()],
                OPTION_TYPE_CHOICES.DATETIME_RANGE_DAY)
            context = option_value.get_context()
            picked = {k: context[k] for k in expect}
            self.assertEquals(picked, expect)
            ctx_range = list(option_value.get_context_range())
            self.assertEquals(len(ctx_range), expect['days'],
                              [len(ctx_range), start_date, end_date, expect])

            # picked = {k: ctx_range[-1][k] for k in expect}
            # self.assertEquals(picked, expect)

    def test_datetime_hours_border_values(self):

        test_cases = [
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 1, 15, 0, 0)],
                {"days": 1, 'hours': 1}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 1, 16, 0, 0)],
                {"days": 1, 'hours': 1}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 1, 16, 1, 0)],
                {"days": 1, 'hours': 2}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 2, 15, 0, 0)],
                {"days": 1, 'hours': 24}
            ),
            (
                [datetime.datetime(2016, 1, 1, 15, 0, 0), datetime.datetime(2016, 1, 2, 15, 1, 0)],
                {"days": 2, 'hours': 25}
            ),
            (
                [datetime.datetime(2016, 1, 1), datetime.datetime(2016, 1, 2)],
                {"days": 1, 'hours': 24}
            ),
        ]

        for (start_date, end_date), expect in test_cases:
            option_value = OptionValue(
                [start_date.isoformat(), end_date.isoformat()],
                OPTION_TYPE_CHOICES.DATETIME_RANGE_HOUR)
            context = option_value.get_context()
            picked = {k: context[k] for k in expect}
            self.assertEquals(picked, expect)
            ctx_range = list(option_value.get_context_range())
            self.assertEquals(len(ctx_range), expect['hours'])


class ContextTestCase(unittest.TestCase):
    def test_generic(self):
        ctx = Context({'r': {'days': 100}})
        self.assertEqual(ctx.resolve('r.days'), 100)
        self.assertEqual(ctx.r.days, 100)

    def test_undefined(self):
        ctx = Context({'value': None})
        self.assertFalse(ctx.days)
        self.assertFalse(ctx['days'])
