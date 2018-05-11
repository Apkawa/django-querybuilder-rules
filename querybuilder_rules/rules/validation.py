# coding: utf-8
from __future__ import unicode_literals

from collections import defaultdict

from ..values import OptionValue
from .base import BaseRule


class ValidateRule(BaseRule):
    """
    Применяем правила валидации и возвращаем ошибки, если они есть.
    Проверяются именно введенные параметры, а не интервал
    """

    def get_rule_result(self, condition, context):
        res = super(ValidateRule, self).get_rule_result(condition, context)
        res['error'] = {
            'message': condition['message'],
            'fields': condition.get('to_options')
        }
        return res

    def _validate(self, context):
        total_errors = list()
        for iter_res, context in self.apply_ruleset([context]):
            for res in iter_res:
                total_errors.append(res['error'])
        return total_errors

    def _flat_errors_to_map(self, error_list):
        flatten_error = defaultdict(set)
        for err in error_list:
            fields = err.get('fields')
            if fields:
                for f in fields:
                    flatten_error[f].add(err['message'])
            else:
                flatten_error[None].add(err['message'])
        return {field: list(err) for field, err in flatten_error.items()}

    def validate(self, value, value_type):
        option_value = OptionValue(value, value_type)
        errors = self._validate(option_value.get_context())
        flatten_errors = self._flat_errors_to_map(errors)
        if flatten_errors:
            return list(flatten_errors.values())[0]
        return []

    def validate_group(self, values_dict):
        """

        :param values_dict: dict of values
        :return:
        """

        context = self.build_group_context(values_dict)

        errors = self._validate(context)

        dict_errors = self._flat_errors_to_map(errors)

        non_group_errors = dict_errors.pop(None, None)
        if non_group_errors:
            dict_errors['__all__'] = non_group_errors
        return dict_errors
