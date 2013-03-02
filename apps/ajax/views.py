import datetime
import re
# Django
from django.conf import settings
from django import http
from django.template import Context, RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect, Http404, HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from django.db.models.query import QuerySet
from django.db.models import Q, F
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
# Methodmint
# External






# Update the homepage stream of actions
def stream_updated(request):

    if 'timestamp' in request.GET:
        try:    
            latest_stream_timestamp = int(request.GET.get('timestamp'))
            latest_stream_time = datetime.datetime.fromtimestamp( latest_stream_timestamp )
        except:
            return HttpResponseBadRequest()  

        (stream,latest_stream_timestamp) = actstream_build(latest_stream_time) 

        if stream:
            #FIXME: This is a hack, due to the lack of sites support in streams; bug submitted
            stream_html = list()

            for action in stream[:25]:
                if type(action) is Action:
                    stream_html.append( render_to_string('actstream/_action.html', {'action':action , 'is_new':True}) )
                else:
                    stream_html.append( render_to_string('actstream/_action_summary.html', {'summary':action , 'is_new':True}) )

                if len(stream_html) == 25:
                    break

            json = simplejson.dumps({'timestamp': latest_stream_timestamp, 'items':stream_html})
            return HttpResponse(json,mimetype="application/json")

    return HttpResponseBadRequest()        


