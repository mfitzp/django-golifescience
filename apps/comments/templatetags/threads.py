from django import template
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib import comments
from django.utils.encoding import smart_unicode

from django.contrib.comments.templatetags.comments import BaseCommentNode

register = template.Library()

class BaseThreadCommentNode(BaseCommentNode):
    """
    Base helper class (abstract) for handling the get_comment_* template tags.
    Looks a bit strange, but the subclasses below should make this a bit more
    obvious.
    """

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse get_comment_list/count/form and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% get_whatever for obj thread as varname %}
        if len(tokens) == 6:
            if tokens[4] != 'as':
                raise template.TemplateSyntaxError("Third argument in %r must be 'as'" % tokens[0])
            return cls(
                object_expr = parser.compile_filter(tokens[2]),
                thread_expr = parser.compile_filter(tokens[3]),
                as_varname = tokens[5],
            )

        # {% get_whatever for app.model pk thread as varname %}
        elif len(tokens) == 7:
            if tokens[5] != 'as':
                raise template.TemplateSyntaxError("Fourth argument in %r must be 'as'" % tokens[0])
            return cls(
                ctype = BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr = parser.compile_filter(tokens[3]),
                thread_expr = parser.compile_filter(tokens[4]),
                as_varname = tokens[6]
            )

        else:
            raise template.TemplateSyntaxError("%r tag requires 5 or 6 arguments" % tokens[0])

    # As with the base class, but with additional thread var
    def __init__(self, ctype=None, object_pk_expr=None, object_expr=None, as_varname=None, comment=None, thread_expr=None):
        if ctype is None and object_expr is None:
            raise template.TemplateSyntaxError("Comment nodes must be given either a literal object or a ctype and object pk.")
        self.comment_model = comments.get_model()
        self.as_varname = as_varname
        self.ctype = ctype
        self.object_pk_expr = object_pk_expr
        self.object_expr = object_expr
        self.comment = comment
        self.thread_expr = thread_expr

    def render(self, context):
        qs = self.get_thread_query_set(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        return ''

    def get_thread_query_set(self, context):
        qs = self.get_query_set(context)
        thread = self.thread_expr.resolve(context)

        # We extend here to filter to the current thread; exclude root post (in thread view)
        qs = qs.filter(tree_id=thread.tree_id).exclude(parent=None)

        return qs


class CommentListNode(BaseThreadCommentNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs)

class CommentCountNode(BaseThreadCommentNode):
    """Insert a count of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return qs.count()


@register.tag
def get_thread_comment_list(parser, token):
    """
    Gets the list of comments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_list for [object] [thread] as [varname]  %}
        {% get_comment_list for [app].[model] [object_id] [thread] as [varname]  %}

    Example usage::

        {% get_comment_list for event thread as comment_list %}
        {% for comment in comment_list %}
            ...
        {% endfor %}

    """
    return CommentListNode.handle_token(parser, token)



@register.tag
def get_thread_comment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_count for [object] [thread] as [varname]  %}
        {% get_comment_count for [app].[model] [object_id] [thread] as [varname]  %}

    Example usage::

        {% get_comment_count for event thread as comment_count %}
        {% get_comment_count for calendar.event event.id thread as comment_count %}
        {% get_comment_count for calendar.event 17 thread as comment_count %}

    """
    return CommentCountNode.handle_token(parser, token)

