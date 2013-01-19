import os.path
import datetime
# Django
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
# Externals
from taggit.models import Tag
from taggit.managers import TaggableManager
from durationfield.db.models.fields.duration import DurationField
from easy_thumbnails.fields import ThumbnailerImageField
from autoslug.fields import AutoSlugField
# Methodmint
from reference.models import Reference


def method_file_path(instance=None, filename=None):
    return os.path.join('method', str(instance.id), filename)
def step_file_path(instance=None, filename=None):
    return os.path.join('step', str(instance.id), filename)


# Method is the implementation of a specific method
class Method(models.Model):
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('method-detail',kwargs={'method_id':str(self.id)})#, 'slug':str(self.slug)})


    # On save, check if reference created/changed & update accordingly
    def save(self, force_insert=False, force_update=False):

        if self.uri:
            # Assign to a temporary reference model
            ref = Reference(uri=self.uri)    
            ref.getnamespace()

            try:
                ref.save()

            except: #already exists in database
                self.reference = Reference.objects.get( namespace=ref.namespace, uri=ref.uri )

            else:
                self.reference = ref      
                ref.autopopulate()
                ref.save()      
        else:
            self.reference = None

        super(Method, self).save(force_insert, force_update)
    # Information
    name = models.CharField('Name', max_length = 50, blank = False)
    slug = AutoSlugField(populate_from='name')
    description = models.TextField(blank = True)
    tags = TaggableManager() #through=TaggedMethod)

    notes = models.TextField(blank = True)

    # Materials: TODO: Improve this with linked models to db of materials;
    # this is a temporary botch until then/parsing is possible.
    materials = models.TextField(blank = True)

    uri = models.CharField('Published URI', max_length = 255, blank = True)
    reference = models.ForeignKey(Reference, null=True, editable = False)

    image = ThumbnailerImageField(max_length=255, upload_to=method_file_path, blank=True)    

    author = models.ForeignKey(User, related_name='authored_methods') # Author originally submitted method
    latest_editor = models.ForeignKey(User, related_name='edited_methods', blank=True, null=True) # Author of current version/sets

    objects = models.Manager()  

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)   

THREAD_CHOICES = ((1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'))


# Steps are consitituent part of each method
class Step(models.Model):
    def __unicode__(self):
        return self.content

    # Wrapper function to provide previous & next step linking
    def previous(self):
        try:
            return self.method.steps.get(order__gt=self.order-1)
        except: 
            return None

    def next(self):
        try:
            return self.method.steps.get(order__gt=self.order+1)
        except: 
            return None
        
    method = models.ForeignKey(Method, related_name='steps')

    order = models.IntegerField(default=0)
 
    # Links to previous steps required completed before starting this one (NB should be attached to same Method)
    # previous = models.OneToOneField("self", blank=True, null=True, related_name='next')
    
    # Text content describing this step (process on save and build meta as appropriate?)
    content = models.TextField(blank = True)
    image = ThumbnailerImageField(max_length=255, upload_to=step_file_path, blank=True)   

    # Additional (optional) information to clarify this step
    tip = models.TextField(blank = True)

    duration = DurationField(null=True, blank=True)
    actual_duration = DurationField(default=300000000, editable=False, blank=True)
    
    # Is this a waiting step
    is_wait = models.BooleanField('Is waiting step', default=False)

    # Work thread, used for compressing on automated steps (same thread must wait, alternate threads may skip)
    thread = models.PositiveIntegerField(default=1, choices=THREAD_CHOICES)

    # Calculated schedule time for this step on the parent method
    # scheduled_at = DurationField()

    objects = models.Manager()  # Swapper around to deprecate the site field, not needed as attached uniquely to a method

    class Meta:
        ordering = ['order']


