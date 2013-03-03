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
    url(r'^$', 'publications.views.publications', {
                'template_name':'publications/publication_list.html',
                'paginate_by':20,    
            },
            name='publication-list'),

    url(r'^(?P<publication_id>\d+)/(?P<publication_slug>.+)/$', 'publications.views.publication', name='publication' ),
    url(r'^(?P<publication_id>\d+)/$', 'publications.views.publication_noslug', name='publication' ),
    url(r'^(?P<publication_slug>\w+)/$', 'publications.views.publication', name='publication' ),


)
