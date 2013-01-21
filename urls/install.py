from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),
    (r'^software/',      include('applications.urls')),
    (r'^ajax/',      include('ajax.urls')),
)

