import os.path
import string
import urllib, re
from datetime import datetime
from xml.dom.minidom import parse, parseString
# Django
from django.core import serializers
from django.conf import settings
from django.db import models
# golifescience
from calaisapi import OpenCalais

def opencalais(obj):
    
    # Process object to get taggable content
    # this should be handled by a templating system
    text = obj.title + obj.abstract

    
    ocRequest = OpenCalais(api_key = settings.OPENCALAIS_API_KEY )
    data =ocRequest.analyze( text ) #, content_type='text/text' )

    assert False, data
    

