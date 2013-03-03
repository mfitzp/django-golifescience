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
from publications.models import AutoReference, Publication
# External
from actstream.models import Action

class Command(BaseCommand):
    help = "Query services for latest papers on matching autoref topics (gets the longest-since-updated-5)"

    def handle(self, *args, **options):
        
        # Get latest 5 min 1 day
        ars = AutoReference.objects.exclude( latest_query_at__gt=datetime.datetime.now() - datetime.timedelta(days=1) ).order_by('-latest_query_at')[:5]
 
        for ar in ars:
            print "Autoref: %s" % ar
            publications_added = ar.autoref() # Assign to Able

            for p in publications_added:
                if p.published:
                    p.created_at = p.published # Update the created date to publication date; stop the flurry
                    p.save() 
                    # Clear up the feed
                    act = Action.objects.get(target_content_type_id=ContentType.objects.get_for_model(Publication), verb='added', target_object_id=p.id )
                    if act:
                        act.timestamp = p.published
                        act.save()

            print "- added %d new references" % len(publications_added)
            


