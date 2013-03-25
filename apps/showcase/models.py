import os.path
import datetime
# Django
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
# Externals
from easy_thumbnails.fields import ThumbnailerImageField

def showcase_file_path(instance=None, filename=None):
    return os.path.join('showcase', str(instance.id), filename)


class ShowcaseItem(models.Model):
    def __unicode__(self):
        return "%s: %s" % (self.content_object, self.description)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    image = ThumbnailerImageField('Image', max_length=255, upload_to=showcase_file_path, blank=True)    

    description = models.TextField(blank = True)

    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    updated_at = models.DateTimeField(auto_now = True, editable = False)   

    objects = models.Manager()  
