# coding=UTF-8
from optparse import make_option
import sys
import datetime, string
import urllib, re
from urlparse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
# methodmint
from references.models import AutoReference

class Command(BaseCommand):
    help = "Query services for latest papers on matching autoref topics (gets the longest-since-updated-5)"

    def handle(self, *args, **options):
        
        # Get latest 5
        ars = AutoReference.objects.exclude( latest_query_at__gt=datetime.datetime.now() - datetime.timedelta(days=1) ).order_by('-latest_query_at')[:5]
        
        for ar in ars:
            print "Autoref: %s" % ar
            x = ar.autoref()
            print "- added %d new references" % x


