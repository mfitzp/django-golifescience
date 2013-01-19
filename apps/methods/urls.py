from django.conf.urls.defaults import *
#from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
# Methodmint
from methods.models import Method
from methods.forms import MethodForm
from methods.feeds import *
# External
#from haystack.forms import SearchForm
#from haystack.views import SearchView
#from haystack.query import SearchQuerySet
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^$', 'methods.views.method_list', {
                'template_name':'methods/method_list.html',
                'paginate_by':20,                
            },
            name='methods'),

    # Methods
    url(r'^(?P<method_id>\d+)/$', 'methods.views.method_noslug', name='method-detail' ),
    url(r'^(?P<method_id>\d+)/edit/$', 'methods.views.method_edit', name='method-edit' ),

    url(r'^rss/$', LatestMethodsFeed(), name='method-rss-latest'),

#    url(r'^create/$', 'methods.views.method_create', name='method-create' ),
#    url(r'^request/$', 'methods.views.method_request', name='method-request' ),


    # Revisions
#   url(r'^(?P<method_id>\d+)/history/$', 'methods.views.method_history', name='method-history' ),


    # Searching/finding
    url(r'^tagged/(?P<slug>[^/]+)/$', 'methods.views.methods_tagged', name='method-tagged'),


#    url(r'^search/$', 'methods.views.search', name='method-search'),


#    url(r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', 'voting.views.vote_on_object', {
#        'model': Method,
#        'template_object_name': 'method',
#        'allow_xmlhttprequest': 'true',
#        }, 
#        name='method-voting'),


#    url(r'^ajax/parse-duration/$', 'methods.views.parse_duration_ajax' ),

    # this is potentially buggy if the slug is anything listed above, oh dear
    url(r'^(?P<method_id>\d+)/(?P<method_slug>.+)/$', 'methods.views.method', name='method-detail' ),

)
