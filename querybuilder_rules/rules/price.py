# coding: utf-8
from __future__ import unicode_literals

from collections import defaultdict
from decimal import Decimal

import re
import sympy
from django.core.exceptions import ValidationError
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_tokenize import TokenError

from .base import BaseRule
from ..values import Context, OptionValue

OPTION_SYMBOL_RE = re.compile(r'^(o_(?P<id>\d+))(?P<sep>\.|__)(?P<field>[a-z]+)$')


def parse_symbol(symbol):
    result = {
        'value': symbol
    }
    match = OPTION_SYMBOL_RE.match(symbol)
    if match:
        result.update(match.groupdict())

    return result


def parse_price(value):
    try:
        value = value.replace(',', '.')
        value = re.sub(r'\.([a-z])', r'__\1', value)

        parsed = parse_expr(value)
        free_symbols = [s.name for s in parsed.free_symbols]

        return {
            'parsed': parsed,
            'symbols': list(map(parse_symbol, free_symbols)),
            'price': parsed.subs(dict.fromkeys(free_symbols, 1))
        }
    except TokenError:
        raise ValidationError("Некорректное выражение!")
    except Exception:
        return None


def price_validation(value):
    parsed = parse_expr(value)
    if len(parsed.free_symbols) > 0:
        raise ValidationError(
            "Выражение содержит неизвестные переменные. Доступные переменные - %s" % ", ".join(
                context.keys()))

    try:
        context = PriceRule._price_context(
            base_price=42
        )
        float(sympy.sympify(value).subs(context))
    except TypeError:
        raise ValidationError("Невозможно вычислить выражение.")


class PriceRule(BaseRule):
    """
    Применяем ценовые правила и считаем цену
    """

    def get_rule_result(self, condition, context):
        res = super(PriceRule, self).get_rule_result(condition, context)

        res['price'] = {
            'title': condition.get('title'),
            'value': condition.get('price'),
            'field': condition.get('to_option'),
            'replace_price': condition.get('replace_price'),
        }
        return res

    @staticmethod
    def _price_context(base_price=0, new_base_price=0, extra=None, context_class=Context):
        base_price = base_price or 0
        context = {
            'bp': float(base_price),
            'nbp': float(new_base_price),
        }
        if isinstance(extra, Context):
            context.update(extra.to_dict())
        else:
            context.update(extra or {})
        return context_class(context)

    def _calculate_price_expression(self, price_expr, context):
        local_context = {}
        for p in context.keys():
            local_context[p] = context[p]
        p = sympy.sympify(price_expr, locals=local_context)
        return Decimal(float(p))

    def _calculate(self, context_range, base_price=0, extra_price_context=None):

        base_price = new_base_price = base_price or 0

        price_map = defaultdict(Decimal)

        base_price_parts = 0

        extra_price_context = extra_price_context or {}
        extra_price_context.update({("o_%s" % field): value
                                    for field, value in self.extra_context.items()})
        explain_data = {}
        if self.explain:
            explain_data = {'extra_context': extra_price_context, 'price_parts': defaultdict(list)}

        for iter_res, context in self.apply_ruleset(context_range):
            res = None
            for res in iter_res:
                price_info = res['price']
                if not price_info:
                    break

                price_context = self._price_context(base_price=base_price,
                                                    new_base_price=new_base_price,
                                                    extra=extra_price_context)
                price_value = self._calculate_price_expression(price_info['value'], price_context)

                price_data = {
                    'rule_result': res.copy(),
                    'context': context,
                    'price_value': price_value,
                    'price_context': price_context.to_dict()
                }
                price_data['rule_result']['context'] = res['context'].to_dict()
                del price_data['rule_result']['condition']

                if res['condition'].has_backwards():
                    # Это встреченное ценовое правило меняет базовую цену, и далее ищем другие ценовые правила.
                    new_base_price = price_value
                    res = None

                    price_data['has_backwards'] = True
                    continue

                field = price_info.get('field')
                if field is None or not price_map.get(field):
                    if price_info.get('replace_price'):
                        price_map[field] = {'price': price_value, 'info': price_info}

                        price_data['replace_price'] = True
                    else:
                        price_map[field] += price_value

                if self.explain:
                    explain_data['price_parts'][field].append(price_data)
                # Ценовое правило найдено
                break

            if res is None:
                # Ценовых правил не обнаружено, увеличиваем счетчик частей для базовoй цены
                price_data = {
                    'context': context,
                    'rule_result': res,
                    'price_value': None
                }
                if self.explain:
                    explain_data['price_parts'][None].append(price_data)
                base_price_parts += 1

        if base_price_parts:
            price_map[None] += Decimal(base_price_parts * new_base_price)

        if self.explain:
            return price_map, explain_data
        return price_map, None

    def calculate_price(self, value, value_type, base_price=0):
        option_value = OptionValue(value, value_type)
        price_map, explain = self._calculate(option_value.get_context_range(),
                                             base_price=base_price)
        result = sum(price_map.values())
        return result, explain

    def calculate_group_price(self, context):
        """

        :param values_dict: dict of values
        :return:
        """
        extra_price_context = {("o_%s" % field): value for field, value in context.items()}

        return self._calculate([context], extra_price_context=extra_price_context)
