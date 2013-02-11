import os.path
import datetime
# Django
from django.conf import settings
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse as django_reverse
# Externals
from taggit.models import Tag
from taggit.managers import TaggableManager
from autoslug.fields import AutoSlugField
from subdomains.utils import reverse
# Methodmint

# Blog article
class Article(models.Model):
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article',kwargs={'article_id':str(self.id)}, subdomain=None)

    def get_absolute_path(self):
        return django_reverse('article',kwargs={'article_id':str(self.id)})


    title = models.CharField('Title', max_length = 80, blank = False)
    slug = AutoSlugField(populate_from='title')

    content = models.TextField(blank = True)
    tags = TaggableManager() #through=TaggedArticle)

    author = models.ForeignKey(User, related_name='authored_articles') # Author originally submitted article
    latest_editor = models.ForeignKey(User, related_name='edited_articles', blank=True, null=True) # Author of current version/sets

    objects = models.Manager()  

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)   

    class Meta:
        ordering = ['created_at']


