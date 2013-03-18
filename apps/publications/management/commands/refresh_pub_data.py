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
from publications.models import Publication

class Command(BaseCommand):
    help = "Refresh data for publication"

    option_list = BaseCommand.option_list + (
        make_option('--start',
            action='store',
            type='int',
            dest='start_id',
            default=1,
            help='Start from id'),
        make_option('--end',
            action='store',
            type='int',
            dest='end_id',
            default=99999999,
            help='End at id'),
        )

    def handle(self, *args, **options):
    
        pubs = Publication.objects.exclude(id__lt=options['start_id']).exclude(id__gt=options['end_id'])
        
        for pub in pubs:
            print "Query for - %s" % pub
            pub.autopopulate()
            pub.save()
            


