#from django.conf import settings

from django.http import HttpResponseRedirect
from django.template import RequestContext   
from django.core.exceptions import PermissionDenied    
from django.contrib.auth.views import login
# Methodmint
from core.views import *

