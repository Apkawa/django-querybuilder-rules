# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from django.utils.encoding import smart_text

from querybuilder_rules.rules.price import parse_price


class ParsePriceTestCase(unittest.TestCase):
    def test_generic(self):
        p = parse_price('( 400* o_33129.value) * o_33128.days')
        self.assertEqual(smart_text(p['parsed']), '400*o_33128__days*o_33129__value')
        self.assertEqual(p['price'], 400)
        self.assertEqual(p['symbols'][0],
                         {u'field': 'days', u'id': '33128', u'value': 'o_33128__days',
                          u'sep': '__'})

    def test_calculate_min_price(self):
        prices = [
            ('( 400* o_33129.value) * o_33128.days * (300 + 500)', (400 * 1) * 1 * (300 + 500)),
            ('200 - 400 * o_33129.value * o_33128.days * 300 + 500', 200 - 400 * 1 * 1 * 300 + 500),
        ]
        for s, expect in prices:
            p = parse_price(s)
            self.assertEqual(p['price'], expect)
