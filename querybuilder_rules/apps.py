from django.apps import AppConfig as BaseConfig
from django.utils.translation import ugettext_lazy as _


class QuerybuilderRulesConfig(BaseConfig):
    name = 'querybuilder_rules'
    verbose_name = _('Querybuilder Rules')
