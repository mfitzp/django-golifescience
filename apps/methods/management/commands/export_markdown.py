# coding=UTF-8
import codecs
from optparse import make_option
import sys,os
import datetime, string
import urllib, re
import settings
from urlparse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.template.loader import render_to_string
# methodmint
from methods.models import Method

class Command(BaseCommand):
    args = "url"
    help = "Export all methods to to markdown format"

    def handle(self, *args, **options):

        path = os.path.join(settings.MEDIA_ROOT, 'pelican')
        methods = Method.objects.all()

        for method in methods:
            md = render_to_string('methods/method.md', {'method':method})
            f = codecs.open(os.path.join(path,'methods','%s.md' % method.slug), 'w', 'utf-8')
            f.write(md)
            f.close()

            for step in method.steps.all():
                # Move the images into a folder
                if step.image:
                    f = codecs.open( step.image.url, 'w', 'utf-8')
                    step.image.save(os.path.join(path,'img', step.image.url),f)
                    f.close()



