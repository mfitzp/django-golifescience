from collections import OrderedDict
import datetime
import settings
# Django
from django import template
from django.template import resolve_variable, NodeList
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User, Group
from django.utils.timesince import timesince
# External
from tagmeta.models import TagMeta

register = template.Library()

class TagMetaForTagNode(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''
        try:
            context[self.context_var] = TagMeta.on_site.get(tag=object)
        except:
            context[self.context_var] = None
           
        return ''


def tagmeta_for_tag(parser, token):
    """
    Example usage::
        {% tagmeta_for_tag tag as tagmeta %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly 4 arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("2nd argument to '%s' tag must be 'as'" % bits[0])

    return TagMetaForTagNode(bits[1], bits[3])

register.tag('tagmeta_for_tag', tagmeta_for_tag)
   
        
