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
    url(r'^$', 'references.views.references', {
                'template_name':'references/reference_list.html',
                'paginate_by':20,    
            },
            name='reference-list'),

    url(r'^(?P<reference_id>\d+)/(?P<reference_slug>.+)/$', 'references.views.reference', name='reference' ),
    url(r'^(?P<reference_id>\d+)/$', 'references.views.reference', name='reference_noslug' ),
    url(r'^(?P<reference_slug>\w+)/$', 'references.views.reference', name='reference' ),


)
