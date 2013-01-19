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
# methodmint
from tagmeta.utils import batch_update_tag_trees

class Command(BaseCommand):
    args = "url"
    help = "Update tag trees, settings parent tags on items tagged with children)"

    def handle(self, *args, **options):
          batch_update_tag_trees()
        
