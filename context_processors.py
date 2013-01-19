import datetime
# Django
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
# External
# Installables
from applications.models import Application

def languages( context ):
	return { 'LANGUAGES': settings.LANGUAGES, 'LANGUAGE_CODE': context.LANGUAGE_CODE }

def modelglobals( content ):
    return {
        'all_applications': Application.objects.order_by('-name').all(),
    } 
