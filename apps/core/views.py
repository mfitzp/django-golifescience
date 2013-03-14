import datetime, collections
from random import choice
import itertools
# Django
from django.conf import settings
from django import http
from django.template import Context, RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect, Http404, HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from django.db.models import Q, F
from django.db.models import Avg, Max, Min, Count, Sum
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Avg
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.views.generic.list_detail import object_list
# External
from taggit.models import TaggedItem, Tag
from methods.models import Method
from applications.models import Application
from blog.models import Article
from comments.models import MPTTComment
from tagmeta.models import TagMeta
from taggit.views import tagged_object_list
# Methodmint
from core.utils import actstream_build
from applications.models import Application
from blog.models import Article
from methods.models import Method
from publications.models import Publication

def home(request):
 
   # Build list of 'sections' using site tags & featured methods [TODO: Add 'featured' boolean flag to method model to mark appropriate for front page; or do by vote?]
    # FIXME: Cache the hell out of this
    sections = list()
    
    # Change content for different subdomains
    content_types = {
        None: [Method, Application], # Article],
        'do': [Method],
        'install': [Application],
        'debat': [Method, Application],
    }
        
    features = []
    # Generate tags-based featured items (sticky, standard based on sites)
    features = cache.get('features-%s' % request.subdomain, list() ) 
    if not features: # No tags
        features = sorted( itertools.chain(
                        Application.objects.order_by('-created_at')[:40],
                        Article.objects.order_by('-created_at')[:40],
                        Method.objects.order_by('-created_at')[:40],
                        Publication.objects.order_by('-created_at')[:10],
                    ),  key=lambda x: x.created_at, reverse=True)[:40]

        cache.set('features-%s' % request.subdomain, features ) 

    directory = TagMeta.objects.filter(level__lt=2)

    (stream, latest_stream_timestamp) = cache.get('activity_stream', (None,0) ) 

    if stream == None:
        (stream, latest_stream_timestamp) = actstream_build()
        cache.set('activity_stream', (stream, latest_stream_timestamp) ) 


    context = {
        #'topsection': topsection,
        #'sections': sections,
        'features': features,

        'directory':directory,

        'stream': stream,
        'latest_stream_timestamp': latest_stream_timestamp,
        # Latest/viewed/voted
        #'top': top,
    }
    #/%s.html' % request.subdomain
    return render_to_response('home/None.html', context, context_instance=RequestContext(request))

def error500(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context:
        MEDIA_URL
            Path of static media (e.g. "media.example.org")
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return http.HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL
    })))


def tag_search(request, **kwargs):
    kwargs['extra_context'] = {'all_objects':Tag.objects.filter(method__site=Site.objects.get_current()).distinct().order_by('name'), 'title':_('Tags') }
    return basic_search(request, **kwargs)


def objects_tagged(request, slug, Model, **kwargs):

    tag = get_object_or_404(Tag, slug=slug)

    if 'sort' in request.GET:
        sort_by = request.GET['sort']
    else:
        sort_by = 'views'

    qs = Model.objects
    ct = ContentType.objects.get_for_model(Model)


    if sort_by == 'latest':
        qs = qs.order_by('-created_at') #.exclude(steps=None)

    if sort_by == 'views':
        qs =  qs.extra(
                  select={ 'hit_count': 'SELECT hits from hitcount_hit_count as t WHERE t.content_type_id=%s AND t.object_pk=%s_%s.id' % (ct.id, ct.app_label, ct.model) }
                  ,).order_by('-hit_count')
 
    # Build to a list of the entire set from all of the searches

    if "extra_context" not in kwargs:
        kwargs["extra_context"] = {}

    kwargs['extra_context'].update( {   
        'tagged_model': Model,
        'tag': tag,
        'sorted_by': sort_by,
    } )

    try:
        tagmeta = TagMeta.objects.get(tag__slug=slug)
    except:
        pass
    else:
        # Generate a directory listing of categorised (tagged) things
        kwargs['extra_context'].update( {
            'directory': tagmeta.get_descendants(),
            'tagmeta': tagmeta,
        } )

    return tagged_object_list(request, slug, qs, **kwargs)


def about(request):
        context = {
            'staff': User.objects.filter(is_staff=True).order_by('-is_superuser','last_name'),
        }

	return render_to_response('about.html', context, context_instance=RequestContext(request))

