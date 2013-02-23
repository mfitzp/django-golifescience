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
from easy_thumbnails.fields import ThumbnailerImageField
from autoslug.fields import AutoSlugField
from taggit.models import Tag
from taggit.managers import TaggableManager
from subdomains.utils import reverse
from licenses.fields import LicenseField
from jsonfield.fields import JSONField
# Methodmint
from references.models import Reference, AutoReference
from authors.models import Author

def application_file_path(instance=None, filename=None):
    return os.path.join('application', str(instance.id), filename)

# Application class
class Application(models.Model):
    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('application',kwargs={'application_id':str(self.id), 'application_slug':str(self.slug)}, subdomain='install')

    def get_absolute_path(self):
        return django_reverse('application', kwargs={'application_id':str(self.id), kwargs={'application_slug':str(self.slug)})

    # Fields
    name = models.CharField('Name', max_length = 50, blank = False)
    tagline = models.CharField('Tagline', max_length = 200, blank = False)

    slug = AutoSlugField(populate_from='name')
    description = models.TextField(blank = True)
    tags = TaggableManager() #through=TaggedMethod)

    url = models.URLField('URL', blank = True)
    source_url = models.URLField('Source URL (e.g. Github)', blank = True)
    
    icon = ThumbnailerImageField('Icon', max_length=255, upload_to=application_file_path, blank=True)    
    image = ThumbnailerImageField('Image', max_length=255, upload_to=application_file_path, blank=True)    

    license = LicenseField(required=False)

    objects = models.Manager()  

    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    updated_at = models.DateTimeField(auto_now = True, editable = False)   

    created_by = models.ForeignKey(User, related_name='created_applications') # Author originally submitted method
    edited_by = models.ForeignKey(User, related_name='edited_applications', blank=True, null=True) # Author of latest edit

    authors = generic.GenericRelation(Author)
    references = generic.GenericRelation(Reference)
    autoreference = generic.GenericRelation(AutoReference)

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

    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    updated_at = models.DateTimeField(auto_now = True, editable = False)   



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

# Holds ohloh identity, and helper functions for retrieving, parsing and handling OhLoh project metadata
class Ohloh(models.Model):
#    def __unicode__(self):
#        return "
    
    # On first save, check if we have an associated application; if not create it and autopopulate
    # this allows creating applications directly from just their ohloh id
    def save(self, force_insert=False, force_update=False):
        if self.pk == None:
            self.get_updated_data()
            self.update_application_data()
    
        super(Ohloh, self).save(force_insert, force_update)

    # Use ohloh data to autopopulate the parent application where data isn't currently set
    def update_application_data(self):
    
        if self.application.name == '':
            self.application.name = self.data['name']

        if self.application.description == '':
            self.application.description = self.data['description']
    
        for tag in self.data['tags']:
            self.application.tags.add( tag.replace('_','-') ) # replace is due to ohloh style tags being fugyly_as
        
        self.application.save()  
    
    
    # Request data for this project as xml, parse out the data into a local data JSON structure for handling
    def get_updated_data(self):
    
        f = urllib.urlopen("https://www.ohloh.net/p/%s.xml?api_key=%s" % ( self.project_id, settings.OHLOH_API_KEY ) )
        # Build DOM for requested data
        dom = parse(f)
        f.close()
    
        if dom:
    
            data = {
                'languages':[],
                'tags':[],
             }
    
            # Iterate over available basic fields and pull them into our model
            for tag in [
                'name',
                'description',
                'user_count',
                'twelve_month_contributor_count']:

                if dom.getElementsByTagName(tag):
                    data[ tag ] = dom.getElementsByTagName(tag)[0].childNodes[0].data.strip()

            # Find multiple tag elements, tags & languages and build lists

            for field, tag in [
                ('tags','tag'),
                ('languages','language')]:

                if dom.getElementsByTagName(tag):
                    for el in dom.getElementsByTagName(tag):
                        data[ field ].append( el.childNodes[0].data.strip() )

            # Cleanup data
            self.data = data
    
    application = models.OneToOneField('Application', related_name='ohloh')
    project_id = models.CharField('Ohloh project ID/name', max_length = 50, blank = False)

    # data
    data = JSONField(editable=False,blank=True,default=dict())


    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    updated_at = models.DateTimeField(auto_now = True, editable = False)   
    # Below used to delay requests for data < 1/month or similar
    latest_query_at = models.DateTimeField(editable = False, null=True, blank=False)   
    

