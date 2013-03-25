import os
import sys
import datetime
from django.template.loader import add_to_builtins

# Django settings for methodmint project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Martin Fitzpatrick', 'mfitzp@abl.es'),
)

MANAGERS = ADMINS

# When calling via command line copy in SITE_ID from env
# (linux) use export SITE_ID=<site_id> to set
SITE_ID = 1
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'installables',
        'USER': 'smrtr',
        'PASSWORD': 'mould',
    }
}

  
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

MEDIA_URL_ROOT = ''
STATIC_URL_ROOT = ''
ADMIN_MEDIA_URL_ROOT = ''

DEFAULT_HOST = 'golifescience.com'
SESSION_COOKIE_DOMAIN = '.golifescience.com'

BLACKLIST_EMAIL_DOMAINS = ['mail.ru']

# local_settings.py can be used to override environment-specific settings
# like database and email that diffeinstallables/static/admin/css/base.cssr between development and production.
try:
    from local_settings import *
except ImportError:
    pass
    

# *** DEFINE URLS HERE SO LOCAL SETTINGS CAN OVERRIDE PATH BASE ***

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = MEDIA_URL_ROOT + '/media/'
STATIC_URL = STATIC_URL_ROOT + '/static/'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Supported languages
_ = lambda s: s
LANGUAGES = (
	( 'en', _( 'English' ) ),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Get site root (from current file) to make following path specifications easier
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')

# Add paths to external & app folders to make including easier
sys.path.append(os.path.join(SITE_ROOT, 'apps'))
sys.path.append(os.path.join(SITE_ROOT, 'external'))
# Specific addition for MPTT as it supplies admin templates/tags

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'templates'),
)

ROOT_URLCONF = 'urls'


#CSRF_COOKIE_DOMAIN = 'golifescience.com'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u2y=71bj-k%-iubxq+gvtwo7__7#b2gr^^4ug)a4*uzy^c7d#m'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

if 'DJANGO_SETTINGS_MODULE' in os.environ: # We're in a live web session (via wsgi)
    add_to_builtins('django.templatetags.future')

MIDDLEWARE_CLASSES = (

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.middleware.cache.UpdateCacheMiddleware',

    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

	'django.middleware.locale.LocaleMiddleware', # should be after SessionMiddleware and CacheMiddleware, if used
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'core.http.Http403Middleware',

#    'subdomains.middleware.SubdomainURLRoutingMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.comments',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
#    'django.contrib.signals',
# Externals
    'pagination',       #http://code.google.com/p/django-pagination
    'easy_thumbnails',  #http://github.com/SmileyChris/easy-thumbnails
#    'south',            # Database migrations: http://south.aeracode.org/
    'memcache_status',
    'taggit',
    'markdown',
    'haystack',
    'jsonfield',
    'mptt',
    'hitcount',
    'countries',    
#    'subdomains',
#   'djangocalais' We're using the API interface provided by this, but not the models so leave inactive
    'registration',
    'postman',
    'licenses',
    'actstream',
    'disqus',
# installables
    'core',
#    'comments',
    'ajax',
    'testimonials',
    'applications',
    'blog',
    'methods',
    'tagmeta', 
    'publications',
    'profiles',
    'authors',
    'showcase',
)
 

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/accounts/logout/'

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'middleware_anon_cache_'

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# External avatar app setting (storage under /media/avatar)
# The following paths are dependent on setting correct base MEDIA/MEDIAADMIN urls in localsettings
AVATAR_DEFAULT_URL = MEDIA_URL + "img/default_avatar.png"

KEY_PREFIX = 'cache_'

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    # Custom data
	'context_processors.languages',
	'context_processors.modelglobals',
	'context_processors.site',
	'context_processors.top5s',
	'context_processors.showcase',
)


AUTH_PROFILE_MODULE = "profiles.userprofile"


# Haystack configuration
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.xapian_backend.XapianEngine',
        'PATH': os.path.join(SITE_ROOT, 'search_index'),
#        'TIMEOUT': 60 * 5,
#        'INCLUDE_SPELLING': True,
#        'BATCH_SIZE': 100,
#        'DEFAULT_OPERATOR': 'OR',
#        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    },
}

ACTSTREAM_ACTION_MODELS = (
    'auth.User',
#    'auth.AnonymousUser',
    'applications.Application',
    'methods.Method',
    'publications.Publication',
#    'questions.Question',
#    'questions.Answer',
#    'discuss.Forum',
#    'discuss.Thread',
#    'discuss.Post',
#    'badges.Badge',
#    'badges.BadgeToUser',
#    'sites.Site',
    'blog.Article',
#    'comments.MPTTComment',
#    'comments.Comment',
)

ACCOUNT_ACTIVATION_DAYS = 30

REDIRECT_FIELD_NAME = 'next'
FORCE_LOWERCASE_TAGS = True


# Email settings: user/pass combination is stored in local settings for security
EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_SUBJECT_PREFIX ='[golifescience.com] '
DEFAULT_FROM_EMAIL = 'noreply@golifescience.com'
SERVER_EMAIL = 'noreply@golifescience.com'

# Hit count
HITCOUNT_KEEP_HIT_ACTIVE = { 'days': 1 }
HITCOUNT_HITS_PER_IP_LIMIT = 0
#HITCOUNT_EXCLUDE_USER_GROUP = ( 'Admin', )


