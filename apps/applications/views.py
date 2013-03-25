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
from applications.models import *
from applications.forms import *
# External
from tagmeta.models import TagMeta
from haystack.query import SearchQuerySet, RelatedSearchQuerySet

def application_noid(request, application_slug):
    application = get_object_or_404(Application, slug=application_slug)
    suffix = request.get_full_path().split('/')[-1] # Required to keep ? and # segments
    return HttpResponsePermanentRedirect( application.get_absolute_url() + suffix )

def application_noslug(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    suffix = request.get_full_path().split('/')[-1] # Required to keep ? and # segments
    return HttpResponsePermanentRedirect( application.get_absolute_url() + suffix )

# Wrapper provides sorting via GET request url, handling via generic view
def applications(request, **kwargs):
    
    # Do application-specific sorting on fields, ratings, etc.
    #    # Check valid
    #    kwargs['queryset'] = kwargs['queryset'].order_by(order_by)

    q = Application.objects

    if 'sort' in request.GET:
        sort_by = request.GET['sort']
    else:
        sort_by = 'views'

    if sort_by == 'latest':
        q = q.order_by('-created_at')

    if sort_by == 'views':
        q =  q.extra(
                  select={ 'hit_count': 'SELECT hits from hitcount_hit_count as t WHERE t.content_type_id=' + str(ContentType.objects.get_for_model(Application).id) + ' AND t.object_pk=applications_application.id',}
                  ,).order_by('-hit_count')

    kwargs['queryset'] = q.all()
    if 'extra_context' not in kwargs:
        kwargs['extra_context'] = {}

    # Generate a directory listing of categorised (tagged) things
    kwargs['extra_context'].update( {
        'directory': TagMeta.objects.filter(level__lt=2),
        'sorted_by': sort_by,
        'tagcount_for_model': Application,
         } )

    return object_list(request, **kwargs)


# Wrapper provides sorting via GET request url, handling via generic view
@ensure_csrf_cookie
def application(request, application_id, application_slug = None):
    
    application = get_object_or_404(Application, pk=application_id)


    context = { 'title': application.name,
                'application': application,
                'tagcount_for_model': Application,
                'morelikethis': SearchQuerySet().more_like_this(application).models(Application)[:5],
              }

    return render_to_response('applications/application.html', context, context_instance=RequestContext(request))


# Create the basic outline information for the recipe, then jump through to full edit (steps/etc. above)
@login_required   
def application_edit(request, application_id=None):

    if application_id:
        application = get_object_or_404(Application, pk=application_id)
    else:
        application = None

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, instance=application)
        # If the form is valid, create a new object and redirect to it.
        if form.is_valid():
            application = form.save(commit=False)
            application.created_by = request.user
            application.save()
            form.save_m2m()
        
            if application_id:
                messages.add_message(request, messages.SUCCESS, _(u"You have successfully edited '%s'" % application.name) )
            else:
                messages.add_message(request, messages.SUCCESS, _(u"You have successfully added '%s'" % application.name) )

            # Create default protocol for this task; skip through to editing it immediately to add steps/etc.
            return HttpResponseRedirect(reverse('application', kwargs={'application_id':application.id, 'application_slug':application.slug} ))

    else:
        form = ApplicationForm(instance=application)

    # Render our template
    return render_to_response('applications/application_form.html',
        {
            'form': form,
            'object': application,
        },
        context_instance=RequestContext(request))




