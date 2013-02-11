import datetime, collections, itertools, re
# Django 
from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse as django_reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage
from django.forms.models import inlineformset_factory
from django.views.generic.list_detail import object_list
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils import formats
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
# External
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from taggit.views import tagged_object_list
# abl.es
from models import *
from forms import *

def article_noslug(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    suffix = request.get_full_path().split('/')[-1] # Required to keep ? and # segments
    return HttpResponsePermanentRedirect( django_reverse('article-detail',kwargs={'article_id':article.id, 'article_slug':article.slug} ) + suffix )

@ensure_csrf_cookie
def article(request, article_id, article_slug = None): 
# answer_id is to allow #'d links to specific answers
# slug is to allow specifying in url, but ignored

    article = get_object_or_404(Article, pk=article_id)

    #mlt = SearchQuerySet().more_like_this(article).models(Article)[:10]

    context = {
        'title':        article,
        'article':     article, 
    #    'morelikethis':    mlt
    }

    return render_to_response('blog/article.html', context, context_instance=RequestContext(request))

# Wrapper provides sorting via GET request url, handling via generic view
def article_list(request, **kwargs):
    
    # Do article-specific sorting on fields, ratings, etc.
    #    # Check valid
    #    kwargs['queryset'] = kwargs['queryset'].order_by(order_by)

    if 'queryset' in kwargs:
        q = kwargs['queryset']
    else:
        q = Article.objects

    if 'sort' in request.GET:
        sort_by = request.GET['sort']
    else:
        sort_by = 'latest'

    if sort_by == 'latest':
        q = q.order_by('-created_at')

    if sort_by == 'votes':
        q =  q.extra(
                select={ 'votes': 'SELECT SUM(vote) from votes as t WHERE t.content_type_id=' + str(ContentType.objects.get_for_model(Article).id) + ' AND t.object_id=news_article.id GROUP BY t.content_type_id,t.object_id',}
                   ,).order_by('-votes')

    if sort_by == 'views':
        q =  q.extra(
                  select={ 'hit_count': 'SELECT hits from hitcount_hit_count as t WHERE t.content_type_id=' + str(ContentType.objects.get_for_model(Article).id) + ' AND t.object_pk=news_article.id',}
                  ,).order_by('-hit_count')

    kwargs['queryset'] = q.all()

    return object_list(request, **kwargs)




