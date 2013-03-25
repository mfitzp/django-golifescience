from django.conf.urls.defaults import *
from django.contrib import admin
from django.utils.translation import ugettext as _
admin.autodiscover()
# Sitemaps
from sitemap import *
from core.feeds import *


def i18n_javascript(request):
  return admin.site.i18n_javascript(request)

handler500 = 'core.views.error500' # Override default handler to pass MEDIA_URL

sitemaps = {
    # Structure
    # 'tasks': TaskSitemap,
    'methods': MethodSitemap,
    'articles': ArticleSitemap,
    'applications': ApplicationSitemap,
    # Users
    'profiles': UserProfileSitemap, 
    'publications': PublicationSitemap,
}


urlpatterns = patterns('',

    (r'^admin/jsi18n', i18n_javascript),
    (r'^admin/',    include(admin.site.urls)),

    # Installables
    url(r'^$', 'core.views.home', name='home'),

    #url(r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}, name='about'),
    url(r'^about/$', 'core.views.about', name='about'),
    url(r'^faq/$', 'django.views.generic.simple.direct_to_template', {'template': 'faq.html'}, name='faq'),
    url(r'^contact/$', 'django.views.generic.simple.direct_to_template', {'template': 'contact.html'}, name='contact'),

    #url(r'^partner/$', 'django.views.generic.simple.direct_to_template', {'template': 'partner.html'}, name='partner'),

    (r'^comments/', include('django.contrib.comments.urls')),
#    url('^markdown/', include( 'django_markdown.urls')),

    # Applications
    (r'^profiles/',      include('profiles.urls')),

    (r'^blog/',      include('blog.urls')),
    (r'^methods/',      include('methods.urls')),
    (r'widgets/wordpress/methods/',  'django.views.generic.simple.direct_to_template', {'template': 'widgets/disabled.html'}),
    (r'^publications/',  include('publications.urls')),
    (r'^software/',      include('applications.urls')),


    (r'^messages/',  include('postman.urls')),


    # Search
#    url(r'^tags/$', 'core.views.tag_search', {
#                'template':'search/tag_search.html',
#                'searchqueryset':SearchQuerySet().models(Tag).load_all(),
#                'form_class':SearchForm,
#            }, 
#            name='tags'
#        ),


    # Registration and user management
#    url(r'^accounts/register/$',
#       register,
#       {'backend': 'captcha.backends.default.CaptchaDefaultBackend', # Enable captcha
#        'form_class': RegistrationFormCaptchaNoUserName}, # Allow registration without username
#       name='registration_register'),
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^accounts/', include('registration.backends.default.urls')),

    (r'^search/', include('haystack.urls')),

    # Ajax
    (r'^ajax/',      include('ajax.urls')),

    # RSS
    url(r'^rss/latest/$', LatestAllFeed(), name='all-rss-latest'),
    url(r'^rss/latest/twitter/$', LatestAllFeedTwitter(), name='all-rss-latest-twitter'),
    url(r'^rss/comments/WxR/$', CommentsWxrFeed(), name='all-comments-wxr'),



    #url(r'^welcome/$', 'django.views.generic.simple.direct_to_template', {'template': 'welcome.html'}, name='welcome'),
    
    # The following are included for development purposes (i.e. can view/edit error page without creating an error ;)
    (r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),
    (r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
    
    # Sitemaps
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

	# Localization - /i18n/setlang/
	(r'^i18n/', include('django.conf.urls.i18n')),

    (r'widgets/wordpress/methods/',  'django.views.generic.simple.direct_to_template', {'template': 'widgets/disabled.html'}),

)

