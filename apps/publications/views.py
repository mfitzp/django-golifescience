import datetime
# Django
from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from django.views.decorators.csrf import ensure_csrf_cookie
# abl.es
from core.http import Http403  
from publications.models import Publication
# External
from tagmeta.models import TagMeta
from haystack.query import SearchQuerySet, RelatedSearchQuerySet

def publication_noslug(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    suffix = request.get_full_path().split('/')[-1] # Required to keep ? and # segments
    return HttpResponsePermanentRedirect( publication.get_absolute_url() + suffix )

# Wrapper provides sorting via GET request url, handling via generic view
def publications(request, **kwargs):
    
    # Do method-specific sorting on fields, ratings, etc.
    #    # Check valid
    #    kwargs['queryset'] = kwargs['queryset'].order_by(order_by)

    q = Publication.objects

    if 'sort' in request.GET:
        sort_by = request.GET['sort']
    else:
        sort_by = 'latest'

    if sort_by == 'latest':
        q = q.order_by('-created_at')

    if sort_by == 'views':
        q =  q.extra(
                  select={ 'hit_count': 'SELECT hits from hitcount_hit_count as t WHERE t.content_type_id=' + str(ContentType.objects.get_for_model(Publication).id) + ' AND t.object_pk=publications_publication.id',}
                  ,).order_by('-hit_count')

    kwargs['queryset'] = q.all()
    if 'extra_context' not in kwargs:
        kwargs['extra_context'] = {}

    # Generate a directory listing of categorised (tagged) things
    kwargs['extra_context'].update( {
        'directory': TagMeta.objects.filter(level__lt=2),
        'sorted_by': sort_by,
        'tagcount_for_model': Publication,
         } )

    return object_list(request, **kwargs)


# Wrapper provides sorting via GET request url, handling via generic view
@ensure_csrf_cookie
def publication(request, publication_slug, publication_id=None):
    
    publication = get_object_or_404(Publication, pk=publication_id)


    context = { 'title': publication.title,
                'publication': publication,
                'tagcount_for_model': Publication,
                'morelikethis': SearchQuerySet().more_like_this(publication).models(Publication)[:5],
              }

    #from tagmeta.autotag import opencalais
    #opencalais(publication)

    return render_to_response('publications/publication.html', context, context_instance=RequestContext(request))

