from django.conf.urls.defaults import *
# Methodmint

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^$', 'comments.views.threads', name='thread-list' ),

    url(r'^(?P<thread_id>\d+)/$', 'comments.views.thread_noslug', name='thread' ),
    url(r'^(?P<thread_slug>\w+)/$', 'comments.views.thread_noid', name='thread' ),

#    url(r'^tagged/(?P<slug>[^/]+)/$', 'core.views.objects_tagged', {'Model':Application, 'template_name':'comments/thread_list.html',}, name='comments-tagged',),

    # this is potentially buggy if the slug is anything listed above, oh dear
    url(r'^(?P<thread_id>\d+)/(?P<thread_slug>.+)/$', 'comments.views.thread', name='thread' ),

)

