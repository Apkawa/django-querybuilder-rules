# coding: utf-8
from __future__ import unicode_literals

import datetime

from .maps import CONDITIONS, OPERATORS, TYPES, BACKWARDS_FIELDS, OPERATORS_FOR_TYPES
from .values import Context


class RuleCondition(object):
    def __init__(self, condition, is_sub=False):
        '''
        {"condition": "AND",
        "rules": [
            ...
        ],

        :param condition:
        :return:
        '''
        self.condition = condition
        self.is_sub = is_sub
        self._compiled = None

    def get_condition(self):
        if self.is_sub:
            return self.condition
        return self.condition['rule']

    def _create_func(self, _operator, field, _args):
        def _func(context):
            v = context[field]
            res = _operator(v, *_args)
            # print field, v, _args, res
            return res
        return _func

    def _build_operator(self, rule):
        operator_name = rule['operator']
        value_type = rule['type']

        _operator = OPERATORS_FOR_TYPES.get(value_type, {}).get(operator_name)
        if not _operator:
            _operator = OPERATORS[operator_name]
        is_dt_type = value_type in ['date', 'time', 'datetime']

        if not operator_name.startswith('is_') and is_dt_type:
            _operator = (
                lambda _op: lambda value, *args: (_op(value, *args) if
                                                  isinstance(value, (datetime.time, datetime.datetime, datetime.date))

                                                  else False))(_operator)
        return _operator

    def _build_test_func(self, rule):
        func_info = {'has_backwards': False}
        _operator_name = rule['operator']
        _type = rule['type']
        value_type = TYPES[_type]

        _operator = self._build_operator(rule)

        args = ()
        field = rule.get('field', rule['id'])

        if field in BACKWARDS_FIELDS:
            func_info['has_backwards'] = True

        value = rule.get('value')

        if value is not None:
            if isinstance(value, list) and all(value):
                test_value = list(map(value_type, value))
            else:
                test_value = value_type(value)

            if isinstance(test_value, list):
                if _operator_name in ['between', 'not_between']:
                    args = tuple(test_value)
                elif _operator_name in ["in", "not_in"]:
                    args = (test_value,)
                else:
                    args = (test_value[0],)
            else:
                args = (test_value,)

        func_info['operator'] = _operator
        func_info['test_func'] = self._create_func(_operator, field, args)
        return func_info

    def compile(self):
        condition = self.get_condition()
        cond_func = CONDITIONS[condition['condition']]
        rule_func_list = []

        self._has_backwards = False

        for rule in condition['rules']:
            if 'condition' in rule:
                condition = RuleCondition(rule, is_sub=True)
                condition.compile()
                if condition.has_backwards():
                    self._has_backwards = True

                rule_func_list.append(condition)
            else:
                func_info = self._build_test_func(rule)
                self._has_backwards = func_info['has_backwards'] or self._has_backwards
                rule_func_list.append(func_info['test_func'])

        def _compiled(context):
            res = None
            for rule_func in rule_func_list:
                if res is None:
                    res = rule_func(context)
                else:
                    res = cond_func(res, rule_func(context))
            return res

        self._compiled = _compiled
        return _compiled

    def __call__(self, context):
        if isinstance(context, dict):
            context = Context(context)
        if self._compiled is None:
            self.compile()
        return self._compiled(context)

    def __getitem__(self, item):
        return self.condition[item]

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def to_dict(self):
        return dict(self.condition)

    def has_backwards(self):
        return self._has_backwards
