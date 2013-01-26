from collections import OrderedDict
import datetime
import settings
from math import log
# Django
from django import template
from django.template import resolve_variable, NodeList
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User, Group
from django.utils.timesince import timesince
# External

register = template.Library()

@register.simple_tag
def duration( duration, fuzzy=False ):
    """ 
    Usage:  {% duration timedelta %}
            Returns seconds duration as weeks, days, hours, minutes, seconds
            Based on core timesince/timeuntil
    """

    def seconds_in_units(seconds):
        """
        Returns a tuple containing the most appropriate unit for the
        number of seconds supplied and the value in that units form.

            >>> seconds_in_units(7700)
            (2, 'hour')
        """

        unit_totals = OrderedDict()

        unit_limits = [
                       ("week", 7 * 24 * 3600),
                       ("day", 24 * 3600),
                       ("hour", 3600),
                       ("minute", 60),
                       ("second", 1)
                        ]

        for unit_name, limit in unit_limits:
            if seconds >= limit:
                amount = int(float(seconds) / limit)
                if amount != 1:
                    unit_name += 's' # dodgy pluralisation
                unit_totals[unit_name] = amount
                seconds = seconds - ( amount * limit )

        return unit_totals;


    if duration:
        if isinstance( duration, datetime.timedelta ):
            if duration.total_seconds > 0:
                if fuzzy:
                    # Base off Arbitrary date
                    return timesince(datetime.datetime(1970,1,1), datetime.datetime(1970,1,1)+duration)
                else:
                    unit_totals = seconds_in_units( duration.total_seconds() )
                    return ', '.join([str(v)+" "+str(k) for (k,v) in unit_totals.iteritems()])

    return 'None'


@register.simple_tag(takes_context=True)
def active_tab(context, tabname):
    url = context['request'].path
    try:
        if url.index( tabname ) == 0:
            return 'active'
    except:
        pass
        


@register.simple_tag
def timesinceauto(value):
    """Formats a date as the time since that date (i.e. "4 days, 6 hours")."""
    if not value:
        return u''
    try:
        return '<abbr class="timeago" title="%s">%s</abbr>' % ( value, value )
    except (ValueError, TypeError):
        return u''

@register.filter
@stringfilter
def truncatesentences(text,number=None):
    if not text:
        return u''
    try:
        if number:
            sentences = text.split('.')
            return '.'.join( sentences[0:number] ) + '.'
    except (ValueError, TypeError):
        return u''
truncatesentences.is_safe = False
        

@register.filter
@stringfilter
def splitnewlines(value):
    """
    Returns the value turned to a list split on newlines
    """
    value=value.strip(' \n') # Strip trailing values
    return value.split('\n') # Split on (internal) \newlines to string

splitnewlines.is_safe = False

@register.filter
def brieftimesince(value, arg=None):
    """Formats a date as the time since that date (i.e. "4 days")."""
    if not value:
        return u''
    try:
        if arg:
            t = timesince(value, arg)
            return t.partition(',')[0]
        t = timesince(value)
        return t.partition(',')[0]

    except (ValueError, TypeError):
        return u''
brieftimesince.is_safe = False

@register.filter
def verybrieftimesince(value, arg=None):
    """Formats a date as the time since that date (i.e. " 6h")."""
    if not value:
        return u''
    try:
        if arg:
            t = brieftimesince(value, arg)
        t = brieftimesince(value)
        # Substitute the words for d, h, m, s
        slist = ('years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds',
                'year', 'month', 'week', 'day', 'hour', 'minute', 'second',)
        sdict = {
            'years':'y', 'months': 'mo', 'weeks': 'w', 'days':'d', 'hours':'h', 'minutes':'m', 'seconds':'s',
            'year':'y', 'month': 'mo', 'week': 'w', 'day':'d', 'hour':'h', 'minute':'m', 'second':'s',
            }
        t = reduce(lambda x, y: x.replace(y, sdict[y]), slist, t)
        return t.replace(" ", "")

    except (ValueError, TypeError):
        return u''
verybrieftimesince.is_safe = False


@register.simple_tag
def colorname( name ):
    """ 
    Wrap the prefix of the ables name in a color span for theming on header bar
    """
    # Find 'ables' in the string, wrap span around the bit before this
    
    pos = name.lower().index('ables')
    return '<span class="sitecolor">' + name[:pos] + '</span>' + name[pos:]


@register.filter
def classname(obj):
    classname = obj.__class__.__name__
    return classname




