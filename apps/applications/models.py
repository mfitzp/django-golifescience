import os.path
import datetime
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
#from django.core.urlresolvers import reverse as django_reverse
# External
from easy_thumbnails.fields import ThumbnailerImageField
from autoslug.fields import AutoSlugField
from taggit.models import Tag
from taggit.managers import TaggableManager
# Methodmint
from references.models import Reference
from authors.models import Author

def application_file_path(instance=None, filename=None):
    return os.path.join('application', str(instance.id), filename)

# Application class
class Application(models.Model):
    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('application',kwargs={'application_slug':str(self.slug)})

    #def get_absolute_path(self):
    #    return django_reverse('application',kwargs={'method_id':str(self.id), 'method_slug':str(self.slug)})

    # Fields
    name = models.CharField('Name', max_length = 50, blank = False)
    tagline = models.CharField('Tagline', max_length = 200, blank = False)

    slug = AutoSlugField(populate_from='name')
    description = models.TextField(blank = True)
    tags = TaggableManager() #through=TaggedMethod)

    github = models.CharField('Github', max_length = 50, blank = True)

    icon = ThumbnailerImageField('Icon', max_length=255, upload_to=application_file_path, blank=True)    
    image = ThumbnailerImageField('Image', max_length=255, upload_to=application_file_path, blank=True)    

    objects = models.Manager()  

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)   

    created_by = models.ForeignKey(User, related_name='created_methods') # Author originally submitted method
    edited_by = models.ForeignKey(User, related_name='edited_methods', blank=True, null=True) # Author of latest edit

    authors = generic.GenericRelation(Author)
    references = generic.GenericRelation(Reference)

# Release class
class Release(models.Model):
    def __unicode__(self):
        return "%s" % (self.release_date)

    def get_absolute_url(self):
        return reverse('application',kwargs={'application_id':str(self.id)})

    def version(self):
        # We use date-based versioning on all software yyyy.mm.dd
        return '%4d.%2d.%2d' % ( self.release_date.year, self.release_date.month, self.release_date.day )

    # Fields
    application = models.ForeignKey(Application, related_name='releases')

    # This is the date a release will be made available, for partners the software will be available before this date
    # as part of the partner benefits
    release_date = models.DateField() 


    notes = models.TextField(blank = True)

    objects = models.Manager()  

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)   



# Feature class
class Feature(models.Model):
    def __unicode__(self):
        return "%s (%s)" % (self.title, self.application)

    # Fields
    application = models.ForeignKey(Application, related_name='features')

    title = models.CharField('Title', max_length = 50, blank = False)
    description = models.TextField(blank = True)

    image = ThumbnailerImageField(max_length=255, upload_to=application_file_path, blank=True)    

    objects = models.Manager()  

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)   

    class Meta:
        order_with_respect_to = 'application'


