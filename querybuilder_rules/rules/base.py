# coding: utf-8
from __future__ import unicode_literals

from ..conditions import RuleCondition
from ..values import OptionValue, Context


class BaseRule(object):
    def __init__(self, ruleset, extra_context=None, explain=False):
        self.explain = explain
        self.ruleset_conditions = list(map(RuleCondition, ruleset or []))
        self.extra_context = extra_context or {}

    def execute(self, context, take_first=True):
        results = []
        for iter_res, context in self.apply_ruleset([context]):
            for res in iter_res:
                if take_first:
                    return res
                results.append(res)
        return results

    @staticmethod
    def build_group_context(value_fields_dict, calculate_result=None):
        context = {
            option_id: OptionValue(value_data['value'], value_data['type']).get_context()
            for option_id, value_data in value_fields_dict.items()
        }
        if calculate_result:
            order_total = calculate_result['total']
            options_total_map = {str(o_id): dict(d) for o_id, d in
                                 calculate_result['options'].items() if o_id}

            for option_id, ctx in context.items():
                option_total = options_total_map[option_id]['total']
                ctx['total'] = option_total
                ctx['order_total'] = order_total - option_total

        return context

    def get_rule_result(self, condition, context):
        return {
            "condition": condition,
            "rule": condition['rule'],
            "context": context,
        }

    def get_rule(self, context):
        """

        :param context:
        :return: generator
        """

        if isinstance(context, dict):
            context = Context(context)

        context.update(self.extra_context)

        for condition in self.ruleset_conditions:
            if condition(context):
                yield self.get_rule_result(condition, context)

    def apply_ruleset(self, context_iterable):
        for context in context_iterable:
            yield self.get_rule(context), context
