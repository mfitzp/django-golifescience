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
from taggit.models import Tag
from tagmeta.models import TagMeta
from methods.models import Method

class Command(BaseCommand):
    help = "Update all tags which are synonyms to point to parent real tag"

    def handle(self, *args, **options):
        
        # Get a list of all synonym tags that are a synonym
        synonym_tags = Tag.objects.extra(where=[''' tag.name IN (SELECT 'synonym' FROM tagmeta_tagsynonym) AS tagsynonym'''])
        
        # Iterate over the tags and replace the tagging, then delete the tag
        for syn in synonym_tags:
            # Can we get this in the query above?
            st = TagSynonym.objects.get(synonym=syn)

            if syn.tag != None:
                # Update tag record for each item; so we're not using the tag anymore
                TaggedItem.objects.filter(tag=syn).update(tag=st.tag)          

            # Delete the tag from the db
            Tag.objects.filter(tag=syn).delete()
            
            
