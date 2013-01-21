from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),
    (r'^methods/',      include('methods.urls')),
    (r'^ajax/',      include('ajax.urls')),
)

