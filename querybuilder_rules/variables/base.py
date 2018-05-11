import functools
import types
from collections import namedtuple

VariableOpts = namedtuple('VariableOpts', ['title', 'help_text', 'choices', 'many'])


class VariableField(object):
    def __init__(self, func):
        self.func = func

    def get_context(self):
        field_value = self.func()
        if isinstance(field_value, BaseVariable):
            return field_value.get_context()
        elif isinstance(field_value, list):
            return [v.get_context() for v in field_value]
        raise NotImplementedError("Must be BaseVariable subclass or list")

    @property
    def title(self):
        return self.func._variable_opts.title

    @property
    def help_text(self):
        return self.func._variable_opts.help_text

    @property
    def choices(self):
        return self.func._variable_opts.choices


class BaseVariable(object):
    title = None
    help_text = None

    def __init__(self, instance,
                 parent=None, title=None, many=False, help_text=None, **kwargs):
        self.parent = parent
        self.instance = instance
        self.many = many
        self.title = title or self.title
        self.help_text = help_text or self.help_text

    def get_fields(self):
        fields = {}
        for name, value in self.__class__.__dict__.items():
            if name.startswith('_'):
                continue
            if value and callable(value) and hasattr(value, '_variable_class'):
                fields[name] = VariableField(getattr(self, name))
        return fields

    def get_context(self):
        ctx = {}
        for name, field in self.get_fields().items():
            ctx[name] = field.get_context()
        return ctx

    @classmethod
    def d(cls, title=None, many=False, help_text=None, choices=None, **kwargs):
        def decorate(func):
            _opts = dict(
                title=title, choices=choices, many=many, help_text=help_text
            )
            func_kw = kwargs.copy()
            func_kw.update(_opts)

            @functools.wraps(func)
            def wrap(self):
                result = func(self)
                if isinstance(result, BaseVariable):
                    return result

                if isinstance(result, list):
                    _res = []
                    for r in result:
                        if isinstance(result, BaseVariable):
                            _res.append(r)
                        else:
                            _res.append(cls(r, parent=self, **func_kw))
                    return _res

                return cls(result, parent=self, **func_kw)

            wrap._variable_class = cls
            wrap._variable_opts = VariableOpts(**_opts)
            return wrap

        return decorate
