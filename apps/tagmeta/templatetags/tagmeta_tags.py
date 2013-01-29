from collections import OrderedDict
import datetime
import settings
# Django
from django import template
from django.template import resolve_variable, NodeList
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User, Group
from django.utils.timesince import timesince
from django.contrib.contenttypes.models import ContentType
# External
from taggit.models import Tag, TaggedItem
from tagmeta.models import TagMeta
# abl.es
from applications.models import Application
from blog.models import Article
from methods.models import Method

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
            context[self.context_var] = TagMeta.objects.get(tag=object)
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
   

class GetTagCount(template.Node):
 
    def __init__(self, tag, var_name, model=None):
        self.tag = tag
        self.var_name = var_name
        self.model = model
 
    def render(self, context):
        tag = template.Variable(self.tag).resolve(context)
        #var_name = template.Variable(self.var_name).resolve(context)

        if not isinstance(tag, Tag):
            assert False, tag
            try:
                tag = Tag.objects.get(slug='%s' % tag) 
            except:
                context[self.var_name] = 0
                return u""

        qs = TaggedItem.objects.filter(tag=tag)
        
        # We now have 'tag' object for the correct tag, can search on this base
        if self.model is not None:
            model = template.Variable(self.model).resolve(context)
            # Get model and apply filter    
            ct = ContentType.objects.get_for_model(model)
            qs = qs.filter(content_type_id=ct)

        context[self.var_name] = qs.count()

        return u""
 
def tagged_count(parser, token):
    """
       {% tagged_count for tag as var %}
       {% tagged_count for tag with model as var %}
    """

    parts = token.split_contents()
    if len(parts) == 5:
        return GetTagCount(parts[2], parts[4])
    if len(parts) == 7:
        return GetTagCount(parts[2], parts[6], parts[4])
    else:
        raise template.TemplateSyntaxError("'tagged_count' formatted incorrectly")
 
register.tag('tagged_count', tagged_count)






class SetDefaultTaggedModel(template.Node):

    def render(self, context):
        try:
            subdomain = template.Variable('request.subdomain').resolve(context)
        except template.VariableDoesNotExist:
            subdomain = None

        try:
            default_tag_model = template.Variable('tagged_model').resolve(context)
        except template.VariableDoesNotExist:
            pass
        else:
            # Is already set; exit
            return u""
    
        lookup = {
            None: None,
            'do': Method,
            'install': Application,
        }

        context['tagged_model'] = lookup[subdomain]
        return u""
 
def set_default_tagged_model(parser, token):
    """
       {% set_default_tagged_model %}
       Queries request.subdomain and sets a template var names tagged_model for correct tags on objects
    """
    parts = token.split_contents()
    return SetDefaultTaggedModel()
 
register.tag('set_default_tagged_model', set_default_tagged_model)
