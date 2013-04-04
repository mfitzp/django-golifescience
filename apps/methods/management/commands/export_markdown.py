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
from django.core.files.base import ContentFile
import Image
# methodmint
from methods.models import Method

class Command(BaseCommand):
    args = "url"
    help = "Export all methods to to markdown format"

    def handle(self, *args, **options):

        path = os.path.join(settings.MEDIA_ROOT, 'pelican')
        methods = Method.objects.all()

        for method in methods:
            # Get a category from the root tagmetas
            # Get tags for this object that have a meta
            tmt = method.tags.filter(meta__parent=None)
            if tmt:
                category = tmt[0].name
            else:
                category = 'misc'

            md = render_to_string('methods/method.md', {'method':method})
            try:
                os.makedirs(os.path.join( path,category ))
            except:
                pass
            f = codecs.open(os.path.join(path,category,'%s.md' % method.slug), 'w', 'utf-8')
            f.write(md)
            f.close()

            if method.image:
                self.moveimage(method.image, path)

            for step in method.steps.all():
                # Move the images into a folder
                if step.image:
                    self.moveimage(step.image, path)

    def moveimage(self, image, path):
        print ": %s" % image.path
        try:
            im = Image.open(image.path)
        except:
            pass
        else:
            imgpathroot = image.path.replace(settings.MEDIA_ROOT + '/','')
            try:
                os.makedirs(os.path.join(path, 'images', *imgpathroot.split('/')[:-1]))
            except:
                pass            


            newpath = os.path.join(path,'images', imgpathroot )
            print "> %s" % newpath
            im.save(newpath)


