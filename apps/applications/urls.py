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
    url(r'^$', 'applications.views.applications', {
                'template_name':'applications/application_list.html',
                'paginate_by':20,    
            },
            name='application-list'),


    url(r'^(?P<application_slug>\w+)/$', 'applications.views.application', name='application' ),

    url(r'^tagged/(?P<slug>[^/]+)/$', 'core.views.objects_tagged', {'Model':Application, 'template_name':'applications/application_list.html',}, name='application-tagged',),

)
