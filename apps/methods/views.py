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
from django.core.urlresolvers import reverse
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
from haystack.forms import SearchForm
from haystack.views import SearchView
from taggit.views import tagged_object_list
# Methodmint
from methods.models import *
from methods.forms import *
from tagmeta.models import TagMeta


def method_noslug(request, method_id):
    method = get_object_or_404(Method, pk=method_id)
    suffix = request.get_full_path().split('/')[-1] # Required to keep ? and # segments
    return HttpResponsePermanentRedirect( method.get_absolute_url() + suffix )

@ensure_csrf_cookie
def method(request, method_id, method_slug = None):
# slug is to allow specifying in url, but ignored

    method = get_object_or_404(Method, pk=method_id)

    # task = method.task
    # Get latest 10 revisions for this method
    #action_list  = Version.objects.get_for_object(method)[0:10]

    # Get all steps
    steps = method.steps.all()

    # Build a list of timepoints (durations from 0) + associated steps
    # Use an OrderedDict (Python 2.7)
    schedule = collections.OrderedDict()

    timer = datetime.timedelta(seconds=0)
    total_active = datetime.timedelta(seconds=0)
    thread_timer = dict()

    if steps.count() == 0:

        # No steps, skip the processing
        total_duration = datetime.timedelta(seconds=0)
        total_waiting = datetime.timedelta(seconds=0)

    else:

        # Setup thread-specific timers    
        threads = steps.distinct().values('thread')
        for thread in threads:
            thread_timer[thread['thread']] = datetime.timedelta(seconds=0)

        for step in steps:

            duration = step.duration if step.duration is not None else step.actual_duration

            if(thread_timer[ step.thread ] > timer):
                schedule[timer] = {
                    'wait': thread_timer[ step.thread ] - timer,
                    'thread': step.thread,
                    }                

            # Adjust timer to account for thread durations
            timer = max( timer, thread_timer[ step.thread ])

            # Store step in the schedule at timepoint 'timer'
            schedule[timer] = step
        
            # Update thread and global timers
            thread_timer[step.thread] = timer + duration #max( step.duration, datetime.timedelta(minutes=5) ) 
            
            # If this is not an automatic step, increment global timer by duration of the step (user will be busy for this time)
            if step.is_wait:
                timer += datetime.timedelta(microseconds=1)
            else:
                timer += max( duration, datetime.timedelta(microseconds=1) ) 
                total_active += duration #max( step.duration, datetime.timedelta(minutes=5) ) 
            
        # Get the highest timer value from thread & global timers
        total_duration = max( max( thread_timer.values() ), timer )
        total_waiting = total_duration - total_active

    context = {
        'title':        method,
        'method':       method, 

        'schedule':     schedule,

        'total_duration':   total_duration,
        'total_active':     total_active,
        'total_waiting':    total_waiting,

        'morelikethis':     SearchQuerySet().more_like_this(method).models(Method)[:5],

        'microdata':        True,

        'tagcount_for_model': Method,

    }

    return render_to_response('methods/method.html', context, context_instance=RequestContext(request))

    
@login_required     
def method_edit(request, method_id):

    method = get_object_or_404(Method, pk=method_id)
    steps = method.steps.all()

    if request.method == 'POST': # If the form has been submitted...

        form = MethodForm(request.POST, request.FILES, instance=method) # A form bound to the POST data
        formset = MethodFormSet(request.POST, request.FILES, instance=method) # A form bound to the POST data

        if formset.is_valid() and form.is_valid(): # All validation rules pass

            method = form.save(commit=False)
            # Dirty hack to not update the 'editor' on the first edit
            if method.created_at != method.updated_at:
                method.latest_editor = request.user
            method.save()
            form.save_m2m()
            formset.save()
            messages.add_message(request, messages.SUCCESS, _(u"Saved your changes") )
            return HttpResponseRedirect( reverse('method-detail',kwargs={'method_id':method.id} ) )
        #else: fall out with formset & errors

    else:
        form = MethodForm(instance=method)
        formset = MethodFormSet(instance=method)
        


    context = {
        'title': method,
        'method': method, 

        'form':form,
        'formset': formset,

        'form_template': StepForm(initial={}),

        'steps': steps,

    }

    return render_to_response('methods/method_edit.html', context, context_instance=RequestContext(request))



# Create the basic outline information for the recipe, then jump through to full edit (steps/etc. above)
@login_required   
def method_create(request):
    if request.method == 'POST':
        form = MethodForm(request.POST)
        # If the form is valid, create a new object and redirect to it.
        if form.is_valid():
            method = form.save(commit=False)
            method.author = request.user
            method.save()
            form.save_m2m()

            messages.add_message(request, messages.SUCCESS, _(u"You have successfully added ") + method.name )

            # Create default protocol for this task; skip through to editing it immediately to add steps/etc.
            return HttpResponseRedirect(reverse('method-edit', kwargs={'method_id':method.id} ) + '#tab-method')
    else:
        # Fill in the field with the current user by default
        form = MethodForm(initial={'author': request.user})   
    # Render our template
    return render_to_response('methods/method_form.html',
        {
            'form': form,
            'action': 'create',
        },
        context_instance=RequestContext(request))


# REQUEST: Same as above but skip adding any steps (no recipe: will appear as a reques)
# TODO: Merge this into the previous function method_create
@login_required   
def method_request(request):
    if request.method == 'POST':
        form = MethodForm(request.POST)
        # If the form is valid, create a new object and redirect to it.
        if form.is_valid():
            task = form.save()
            messages.add_message(request, messages.SUCCESS, _(u"Your request has been logged ") )

            return HttpResponseRedirect(method.get_absolute_url())
    else:
        # Fill in the field with the current user by default
        form = MethodForm(initial={})
    # Render our template
    return render_to_response('methods/method_form.html',
        {
            'form': form,
            'action': 'request'
        },
        context_instance=RequestContext(request))



     
def method_history(request, method_id):

    method = get_object_or_404(Method, pk=method_id)

    # Build a list of all previous versions, in order of creation:
    action_list  = Version.objects.get_for_object(method)

    context = {
        'title': method,
        'method': method, 
        'action_list': action_list ,
    }

    return render_to_response('methods/method_history.html', context, context_instance=RequestContext(request))



# Wrapper provides sorting via GET request url, handling via generic view
def method_list(request, **kwargs):
    
    # Do method-specific sorting on fields, ratings, etc.
    #    # Check valid
    #    kwargs['queryset'] = kwargs['queryset'].order_by(order_by)

    q = Method.objects

    if 'sort' in request.GET:
        sort_by = request.GET['sort']
    else:
        sort_by = 'views'

    if sort_by == 'latest':
        q = q.order_by('-created_at')

    if sort_by == 'views':
        q =  q.extra(
                  select={ 'hit_count': 'SELECT hits from hitcount_hit_count as t WHERE t.content_type_id=' + str(ContentType.objects.get_for_model(Method).id) + ' AND t.object_pk=methods_method.id',}
                  ,).order_by('-hit_count')

    kwargs['queryset'] = q.all()
    if 'extra_context' not in kwargs:
        kwargs['extra_context'] = {}

    # Generate a directory listing of categorised (tagged) things
    kwargs['extra_context'].update( {
        'directory': TagMeta.objects.filter(level__lt=2),
        'sorted_by': sort_by,
        'tagcount_for_model': Method,
         } )

    return object_list(request, **kwargs)




def parse_duration_ajax(request):
    
    if 'duration' in request.GET:
        duration_str = " " + request.GET['duration'] + " "

        d = dict()
    
        for match in ['w', 'd','h','m','s']:
            result = re.search('\s(?P<n>[0-9]*)\s?' + match, duration_str)
            if result:
                d[match] = int( result.group('n') )
            else:
                d[match] = 0

        duration = datetime.timedelta( weeks = d['w'], days = d['d'],  hours = d['h'],  minutes = d['m'],  seconds = d['s']) 

        return HttpResponse(simplejson.dumps({
            'success': True,
            'duration': force_unicode(formats.localize_input(duration)),
        }))
   

    return HttpResponse(simplejson.dumps({
        'success': False,
    }))


def search(request):

    sqs = SearchQuerySet().models(Method)

    if request.GET.get('q'):

        form = SearchForm(request.GET, searchqueryset=sqs)

        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
            paginator = Paginator(results, 10)

            try:
                page = paginator.page(int(request.GET.get('page', 1)))
            except InvalidPage:
                raise Http404("No such page of results!")

    else:
        form = SearchForm(searchqueryset=sqs)
        paginator = None
        page = None
        query = request.GET.get('q')
    
    
    context = {
        'form': form,
        'page': page,
        'paginator': paginator,
        'query': query,
        'suggestion': None,
    }
    
    return render_to_response('search/method_search.html', context, context_instance=RequestContext(request))



