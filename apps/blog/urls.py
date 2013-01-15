from django.conf.urls.defaults import *
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
# External
#from haystack.forms import SearchForm
#from haystack.views import SearchView
#from haystack.query import SearchQuerySet
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
# Methodmint
from models import Article
from feeds import *

urlpatterns = patterns('',

    url(r'^$', 'blog.views.article_list', {
                'template_name':'blog/article_list.html',
                'paginate_by':20,                
            },
            name='blog'),

    # Methods
    url(r'^(?P<article_id>\d+)/$', 'blog.views.article_noslug', name='article-detail' ),
    #url(r'^(?P<article_id>\d+)/edit/$', 'news.views.article_edit', name='article-edit' ),
    #url(r'^create/$', 'news.views.article_edit', name='article-create' ),

    url(r'^rss/$', LatestArticlesFeed(), name='articles-rss-latest'),

    # oh dear, potentially buggy if slug is 'edit, or answer or :/'
    url(r'^(?P<article_id>\d+)/(?P<article_slug>.+)/$', 'blog.views.article', name='article-detail' ),



)
