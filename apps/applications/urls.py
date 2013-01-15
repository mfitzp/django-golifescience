from django.conf.urls.defaults import *
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
# Methodmint
from applications.models import Application
# External
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    # Applications
    url(r'^$', 'applications.views.applications', name='applications' ),
    url(r'^(?P<application_slug>\w+)/$', 'applications.views.application', name='application' ),
)
