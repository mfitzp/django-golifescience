from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
# Methodmint
from comments.models import MPTTComment
# External
from tagmeta.models import TagMeta
from haystack.query import SearchQuerySet, RelatedSearchQuerySet

    
def thread_noid(request, thread_slug):
    thread = get_object_or_404(MPTTComment, slug=thread_slug)
    suffix = request.get_full_path().split('/')[-1] # Required to keep ? and # segments
    return HttpResponsePermanentRedirect( thread.get_absolute_url() + suffix )

def thread_noslug(request, thread_id):
    thread = get_object_or_404(MPTTComment, pk=thread_id)
    suffix = request.get_full_path().split('/')[-1] # Required to keep ? and # segments
    return HttpResponsePermanentRedirect( thread.get_absolute_url() + suffix )

def threads(request, **kwargs):
    
    threads = MPTTComment.threads.all()[:25]


    context = { 'title': 'Discussions',
                'threads': threads,
              }

    return render_to_response('comments/thread-list.html', context, context_instance=RequestContext(request))


# Wrapper provides sorting via GET request url, handling via generic view
@ensure_csrf_cookie
def thread(request, thread_id, thread_slug = None):
    
    thread = get_object_or_404(MPTTComment, pk=thread_id)
    thread_object = thread.content_object

    context = { 'title': thread.name,
                'thread': thread,
                'thread_tree_id_limit': thread.tree_id,
                'object': thread_object, 
                #'tagcount_for_model': Application,
                'morelikethis': SearchQuerySet().more_like_this(thread).models(MPTTComment)[:5],
              }

    return render_to_response('comments/thread.html', context, context_instance=RequestContext(request))

