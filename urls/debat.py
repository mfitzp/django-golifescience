from django.conf.urls.defaults import *
from sitemap import *

sitemaps = {
    'methods': MethodSitemap,
}

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),

#    (r'^discussions/', include('comments.urls')),
    (r'^ajax/',      include('ajax.urls')),
#    (r'^comments/', include('django.contrib.comments.urls')),

    # Sitemaps
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

