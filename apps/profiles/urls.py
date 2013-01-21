from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _
# Methodmint
from profiles.models import UserProfile
# External
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^edit/$', 'profiles.views.edit_profile', name='profile-edit' ),
    url(r'^avatar/$', 'profiles.views.change_avatar', name='avatar-change' ),

    url(r'^(?P<user_id>\d+)/$', 'profiles.views.profile', name='user-profile' ),
    url(r'^(?P<username>.+)/$', 'profiles.views.profile', name='user-profile' ),

    url(r'^$', 'profiles.views.search',
            name='users'
        ),
)
