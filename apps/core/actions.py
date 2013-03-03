import os.path
import datetime
import urllib, re
from xml.dom.minidom import parse, parseString
# Django
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse as django_reverse
# External
from actstream import action


# Saving of method object
def object_saved(sender, instance, created, **kwargs):
    # Check if creating or editing
    if created:
        action.send(instance.created_by, verb='added', action_object=instance, target=instance)
    else:
        # FIXME: Need to implement instance.editor (or latest_editor)
        # Dirty hack to not update the 'editor' on the first edit
        if instance.edited_by != None:
            action.send(instance.edited_by, verb='edited', action_object=instance, target=instance)      

# Saving of method object
def object_created(sender, instance, created, **kwargs):
    # Check if creating or editing
    if created:
        action.send(instance.created_by, verb='added', action_object=instance, target=instance)

