# Python
import math
import urllib
# Django
import settings
from django import template
from django.conf import settings
from django.template import resolve_variable, NodeList
from django.utils.hashcompat import md5_constructor
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
# External


register = template.Library()

@register.simple_tag
def author_list( authors ):
    """ 
    Usage: {% author_list authors %}
            Output a list of authors in full with markers for equal contribution
    """
    if authors:
        l_author = []
        l_orgs = []

        for author in authors:
            if author.contrib_marker > 0: # We have a marker
                s_author_marker = author.get_contrib_marker_display()
            else:
                s_author_marker = ''

            if author.user.get_profile().organisation:
                if author.user.get_profile().organisation in l_orgs: # Already have it
                    s_orgs_number = l_orgs.index( author.user.get_profile().organisation ) +1
                else:
                    l_orgs.append( author.user.get_profile().organisation )
                    s_orgs_number = len( l_orgs )
            else:
                s_orgs_number = ''

            l_author.append( '<a href="%s">%s</a><sup>%s%s</sup>' % ( reverse('user-profile',kwargs={'user_id':str(author.user.id)}), author.user.get_full_name(), s_orgs_number, s_author_marker ) )

        # Add the numbers after the names
        for n, org in enumerate(l_orgs):
            l_orgs[n] = '%s<sup>%d</sup>' % (org, n+1)
            

        return ', '.join( l_author ) + '<br />' + ', '.join( l_orgs )
    else:
        return 'No known authors'

@register.simple_tag
def author_et_al( authors ):
    """ 
    Usage: {% author_list_abbrev authors %}
            Output an abbreviated list of authors in full with markers for equal contribution   
    """
    if authors:
        return '<a href="%s">%s</a> <i>et al</i>' % ( reverse('user-profile',kwargs={'user_id':str(authors[0].user.id)}), authors[0].user.get_full_name() )
    else:
        return 'No known authors'

