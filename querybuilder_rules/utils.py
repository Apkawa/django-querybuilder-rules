# coding: utf-8
from __future__ import unicode_literals

from django.template import Variable, VariableDoesNotExist

from .maps import UNDEFINED


def getattr_path(obj, path, default=UNDEFINED):
    try:
        return Variable(path).resolve(obj)
    except VariableDoesNotExist:
        if default is UNDEFINED:
            raise AttributeError("don't resolved path `%s`", path)
        return default


def update_rule(rule, callback=None):
    callback = callback or (lambda x: x)
    new_rules = []
    for r in rule['rules']:
        if 'condition' in r:
            nr = update_rule(r, callback)
        else:
            nr = callback(r)
        new_rules.append(nr)
    rule['rules'] = new_rules
    return rule
