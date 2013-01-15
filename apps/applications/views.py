import datetime
# Django
from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
# Theproject
from core.http import Http403  
from applications.models import *
# External

# Wrapper provides sorting via GET request url, handling via generic view
def applications(request, **kwargs):
    
    applications = Application.objects.order_by('?')[:20]


    context = { 'title': 'Applications',
                'applications': applications,
              }

    return render_to_response('applications/applications.html', context, context_instance=RequestContext(request))

# Wrapper provides sorting via GET request url, handling via generic view
def application(request, application_slug):
    
    application = get_object_or_404(Application, slug=application_slug)


    context = { 'title': 'Applications',
                'application': application,
              }

    return render_to_response('applications/application.html', context, context_instance=RequestContext(request))

