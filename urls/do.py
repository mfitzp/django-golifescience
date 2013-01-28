from django.conf.urls.defaults import *
from sitemap import *

sitemaps = {
    'methods': MethodSitemap,
}

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),
    (r'^methods/',      include('methods.urls')),
    (r'^ajax/',      include('ajax.urls')),

    (r'widgets/wordpress/methods/',  'django.views.generic.simple.direct_to_template', {'template': 'widgets/disabled.html'}),

    # Sitemaps
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

