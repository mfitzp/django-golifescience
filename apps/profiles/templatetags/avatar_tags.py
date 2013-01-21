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
from django.contrib.auth.models import AnonymousUser
# External
from easy_thumbnails.files import get_thumbnailer



register = template.Library()

@register.simple_tag
def avatar( user, size=50, user_name=None, user_email=None ):
    """ 
    Usage: {% avatar user [size] [force] %}
            Returns image tag for avatar image at given size
            Force enforces the source of the image
    """
   
    if user is None or isinstance(user, AnonymousUser): # Anonymous users; if we allow them
        if user_email:
            url = gravatar_url_email( user_email, size )
        else:
            url = settings.AVATAR_DEFAULT_URL

    elif user.get_profile().avatar:
        # Use user-defined onsite avatar by default
        url = profile_avatar_url( user, size )
        user_name = user.get_full_name()
    
    elif hasattr(user, 'facebook_profile'):
        # If user has come in via facebook use their facebook image     
        url = facebook_avatar_url( user ) # Size is not used by facebook standard square, resized by html
        user_name = user.get_full_name()
        
    else:
        # Use gravatar as backup (with backup to local default url if no gravatar user)
        url = gravatar_url( user, size )
        user_name = user.get_full_name()


    return '<img src="%s" style="width:%dpx;height:%dpx" class="avatar" alt="%s" title="%s">' % (url, size, size, user_name, user_name)

@register.simple_tag
def avatar_from_provider( user, size=50, provider='profile'):

    if provider=='profile':
        url = profile_avatar_url( user, size )

    elif provider=='facebook':
        # If user has come in via facebook use their facebook image     
        url = facebook_avatar_url( user )
        
    elif provider=='gravatar':
        # Use gravatar as backup (with backup to local default url if no gravatar user)
        url = gravatar_url( user, size )

    return '<img src="%s" style="width:%dpx;height:%dpx">' % (url, size, size)




def profile_avatar_url( user, size=50 ):

    # Thumbnail uploaded image to correct size
    thumbnail = get_thumbnailer(user.get_profile().avatar).get_thumbnail( dict(size=(size, size), crop=True ) )
    return thumbnail.url


def facebook_avatar_url( user ):

    fb = user.facebook_profile
    return  "http://graph.facebook.com/%s/picture?type=square" % escape(fb.username)

def gravatar_url( user, size=50):
    return gravatar_url_email( user.email, size )

def gravatar_url_email( user_email, size=50 ):

    gravatar_options = {
        's': str(size), 
        'r': 'g',
        'default':'identicon',
        }
    #gravatar_options['d'] = getattr(settings, 'AVATAR_DEFAULT_URL', '')
    return "http://www.gravatar.com/avatar/%s?%s" % (
        md5_constructor(user_email).hexdigest(),
        urllib.urlencode(gravatar_options),)



