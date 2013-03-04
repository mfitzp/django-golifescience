from django.conf.urls.defaults import *
from sitemap import *

sitemaps = {
    'applications': ApplicationSitemap,
}

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),
    (r'^software/',      include('applications.urls')),
    (r'^ajax/',      include('ajax.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),

    (r'widgets/wordpress/methods/',  'django.views.generic.simple.direct_to_template', {'template': 'widgets/disabled.html'}),

    # Sitemaps
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

