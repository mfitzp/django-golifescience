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

class Author(models.Model):
    def __unicode__(self):
        return "%s (%d)" % ( self.user.get_full_name(), self.contrib_marker )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User)

    CONTRIBUTION_MARKERS = (
        ( 0, ''),
        ( 1, '*'),
        ( 2, '&dagger;'),
        ( 3, '&curren;'),
        ( 4, '&sect;'),
        ( 5, '&Dagger;'),
    )

    contrib_marker = models.PositiveIntegerField('Equal contribution marker',default=0,choices=CONTRIBUTION_MARKERS)

    class Meta:
        order_with_respect_to = 'content_type'    



