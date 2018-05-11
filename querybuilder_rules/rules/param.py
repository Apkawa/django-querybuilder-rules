# coding: utf-8
from __future__ import unicode_literals

from collections import defaultdict

from ..values import OptionValue
from .base import BaseRule


def flatten_results(result_list):
    flatten_error = defaultdict(set)
    for res in result_list:
        fields = res.get('fields')
        if fields:
            for f in fields:
                flatten_error[f].add(res)
        else:
            flatten_error[None].add(res)
    return {field: list(err) for field, err in flatten_error.items()}


class ParamRules(BaseRule):
    """
    Применяем правила валидации и возвращаем ошибки, если они есть.
    Проверяются именно введенные параметры, а не интервал
    """

    def get_rule_result(self, condition, context):
        res = super(ParamRules, self).get_rule_result(condition, context)
        res['param'] = {f: condition[f] for f in ['param_type', 'params']}
        return res

    def collect_results(self, context):
        total_errors = list()
        for iter_res, context in self.apply_ruleset([context]):
            for res in iter_res:
                total_errors.append(res)
        return total_errors

    def run(self, value, value_type):
        option_value = OptionValue(value, value_type)
        results = self.collect_results(option_value.get_context())
        return [r['param'] for r in results]

    def run_group(self, values_dict):
        """

        :param values_dict: dict of values
        :return:
        """

        context = self.build_group_context(values_dict)

        results = self.collect_results(context)
        return results
