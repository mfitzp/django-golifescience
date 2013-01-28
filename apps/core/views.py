import datetime, collections
from random import choice
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
# External
from taggit.models import Tag
from methods.models import Method
from tagmeta.models import TagMeta
from taggit.views import tagged_object_list
# Methodmint


def home(request):
 
   # Build list of 'sections' using site tags & featured methods [TODO: Add 'featured' boolean flag to method model to mark appropriate for front page; or do by vote?]
    # FIXME: Cache the hell out of this
    sections = list()


    # Generate tags-based featured items (sticky, standard based on sites)
    allsections = cache.get('allsections', list() ) 
    if not allsections: # No tags
        allsections = list()
        # Get featured tags for site based on the root tagmeta fields
        tags = Tag.objects.exclude(meta__tag_id=None).filter(meta__parent=None).order_by('?') # remove the meta__parent none restriction to get more variation

        for tag in tags[:5]:
           # tag = tagm.tag
            items = list( Method.objects.filter(tags__slug=tag.slug).exclude(image='').order_by('?')[:5] ) #.filter(is_featured=True)
            #items += list( Method.on_site.filter(tags__slug=tag.slug).filter(image='').order_by('?')[:5-len(items)] ) #.filter(is_featured=True)
            if len(items) > 0:
                section = { 
                    'type': 'method',
                    'tag': tag,
                    'items': items,
                        }

                allsections.append( section )

        cache.set('allsections', allsections ) 

    directory = TagMeta.objects.filter(level__lt=2)
    sections = allsections

    topsection = {
        'type': 'method',
        'tag': 'all',
        'items': list(),
    }

    for section in allsections:
        topsection['items'].append( choice(section['items']) )

    context = {
        'topsection': topsection,
        'sections': sections,

        'directory':directory,

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

    q = Model.objects
    ct = ContentType.objects.get_for_model(Model)

    if 'sort' in request.GET:
        sort_by = request.GET['sort']
    else:
        sort_by = 'views'

    if sort_by == 'latest':
        q = q.order_by('-created_at').exclude(steps=None)

    if sort_by == 'views':
        q =  q.extra(
                  select={ 'hit_count': 'SELECT hits from hitcount_hit_count as t WHERE t.content_type_id=%s AND t.object_pk=%s_%s.id' % (ct.id, ct.app_label, ct.model) }
                  ,).order_by('-hit_count')
 
    kwargs['queryset'] = q.all()

    # Build to a list of the entire set from all of the searches

    if 'extra_context' not in kwargs:
        kwargs['extra_context'] = {}

    kwargs['extra_context'].update( {   
        'tagged_model': Model,
    } )

    try:
        tagmeta = TagMeta.objects.get(tag__slug=slug)
    except:
        kwargs['extra_context'].update( {   
            'tag': tag,
            'sorted_by': sort_by,
        } )
    else:
        # Generate a directory listing of categorised (tagged) things
        kwargs['extra_context'].update( {
            'directory': tagmeta.get_descendants(),
            'tagmeta': tagmeta,
            'tag': tag,
            'sorted_by': sort_by,
        } )

    return tagged_object_list(request, slug, **kwargs)


