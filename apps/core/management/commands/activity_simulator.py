# coding=UTF-8
from optparse import make_option
import sys
import datetime, string
import urllib, re
from random import choice
from urlparse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
# methodmint
from applications.models import Application
from methods.models import Method

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        )

    def handle(self, *args, **options):
        objs = []
        objs.extend( [Application])
        objs.extend( [Method] * 20 ) # Compensate for relative numbers of each
        
        obj = choice(objs).objects.all().order_by('?')[0]

        print "Simulating edit to %s" % obj

        obj.updated_at = datetime.datetime.now()
        obj.save()

        
