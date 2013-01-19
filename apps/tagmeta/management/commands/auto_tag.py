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
    args = "url"
    help = "Update tag trees, settings parent tags on items tagged with children)"

    option_list = BaseCommand.option_list + (
        make_option('-s', '--search', action='store', dest='search',
            default='', type='string', help='Search for methods with matching name, description containing this string.'
        ),
        make_option('-t', '--tag', action='store', dest='tag',
            default='', type='string', help='Apply this tag.'
        ),
        make_option('-d', '--dummy', action='store_true', dest='dummy',
            default=False, help='Dummy run?'
        ),
    )

    def handle(self, *args, **options):

        try:
            tag = Tag.objects.get(slug=options['tag'])
            print "Found tag: %s" % tag
        except:
            print "Invalid tag: %s" % options['tag']
            exit()

        objects = Method.objects.filter( Q( name__icontains=options['search']) | Q(description__icontains=options['search'] ))
        print "...%d objects" % objects.count()        

        for obj in objects:
            if not options['dummy']:
                print "+ %s" % obj
                obj.tags.add( tag )
            else:
                print "x %s" % obj        
