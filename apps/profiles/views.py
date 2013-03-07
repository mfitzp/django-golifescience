from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
# Methodmint
from profiles.models import *
from profiles.forms import *
# External
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from haystack.forms import SearchForm
from haystack.views import SearchView


def profile(request, user_id = None, username = None):

    if user_id:
        puser = get_object_or_404(User, pk=user_id)
    else:
        puser = get_object_or_404(User, username=username)

    profile = puser.get_profile()

    #methods = puser.authored_methods.order_by('-created_at')[:10]


    context = {
        'title': profile,
        'puser': puser, 
        'profile': profile,

        #'methods': methods,
    }

    return render_to_response('profiles/profile.html', context, context_instance=RequestContext(request))
    
@login_required
def edit_profile(request):

    user = request.user
    profile = user.get_profile()

    if request.method == 'POST': # If the form has been submitted...
        uform = UserForm(request.POST, instance=user) # A form bound to the POST data
        pform = ProfileForm(request.POST, request.FILES, instance=profile) # A form bound to the POST data
        if pform.is_valid() and uform.is_valid(): # All validation rules pass
            user = uform.save()
            user.save()
            profile = pform.save()
            profile.save()
            return HttpResponseRedirect( reverse('user-profile',kwargs={'user_id':user.id} ) )
    else:
        uform = UserForm(instance=user)
        pform = ProfileForm(instance=profile)
        
    context = {
        'title': _('Edit %(user)s') % { 'user':user.get_full_name() },
        'profile': profile,
        'uform': uform,
        'pform': pform,
    }

    return render_to_response('profiles/profile_edit.html', context, context_instance=RequestContext(request))
    
    
@login_required
def change_avatar(request):

    user = request.user
    profile = user.get_profile()

    if request.method == 'POST': # If the form has been submitted...
        form = AvatarForm(request.POST, request.FILES, instance=profile) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass

            if form.cleaned_data['delete']==True:
                profile.avatar = None

            profile = form.save()
            profile.save()
            return HttpResponseRedirect( reverse('user-profile',kwargs={'user_id':user.id} ) )
    else:
        form = AvatarForm(instance=profile)
        
    context = {
        'title': _('Change profile picture for %(user)s') % { 'user':user.get_full_name() },
        'profile': profile,
        'form': form,
    }

    return render_to_response('profiles/change_avatar.html', context, context_instance=RequestContext(request))    


def search(request):

    sqs = SearchQuerySet().models(UserProfile)

    if request.GET.get('q'):

        form = SearchForm(request.GET, searchqueryset=sqs)

        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
            results = results.filter(user__is_active = True ).order_by('-user__reputation__reputation')
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
        'all_objects':UserProfile.objects.filter(user__is_active = True).order_by('-user__reputation__reputation')
    }
    
    return render_to_response('search/profile_search.html', context, context_instance=RequestContext(request))


