import os.path
import datetime, string
import urllib, re
from xml.dom.minidom import parse, parseString
# Django
from django.core import serializers
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse as django_reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
# Methodmint
from references import isbn
from references import autopopulate
from references import autoref
#External
from autoslug.fields import AutoSlugField
#from picklefield.fields import PickledObjectField, PickledObject
from jsonfield.fields import JSONField
from subdomains.utils import reverse

# A reference object, pointing to an external resource via URN or URL
class Reference(models.Model):

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reference',kwargs={'reference_id':str(self.id), 'reference_slug':str(self.slug)}, subdomain=None)
    def get_absolute_path(self):
        return django_reverse('reference',kwargs={'reference_id':str(self.id), 'reference_slug':str(self.slug)})

    # On save, check if reference created/changed & update accordingly
    def save(self, force_insert=False, force_update=False):
        self.getnamespace()
        self.autopopulate()
        super(Reference, self).save(force_insert, force_update)


    def et_al(self):
        if self.author:
            al = self.author.split(', ')
            return '%s et al.' % al[0]

    @property
    def tagline(self):
        if self.published:
            return "%s %s (%s)" % (self.et_al(), self.publisher, self.published.year)
        else:
            return "%s %s" % (self.et_al(), self.publisher)
    

    # Generate an standard resource URL for this resource object
    # Preference is given to doi, then urn, then direct links
    def url(self):
        if self.namespace == 'doi':
            return "http://dx.doi.org/%s" % self.uri
        elif self.namespace == 'isbn':
            if 'asin' in self.meta: # If we have direct product link, use it
                return "http://www.amazon.com/dp/%s?tag=mutadsman-20" % self.meta['asin']
            else:
                return "http://www.amazon.com/gp/search/ref=sr_adv_b/?field-isbn=%s&_encoding=UTF8&tag=mutadsman-20&linkCode=ur2&camp=1789&creative=390957" % self.uri
        elif self.namespace == 'pmid':
            return "http://www.ncbi.nlm.nih.gov/pubmed/%s" % self.uri
        elif self.uri:
            if( string.find(self.uri, 'http://') == 0 ):
                return self.uri
            else:
                return 'http://' + self.uri


    def getnamespace(self):
        # Check if user supplied the namespace in the uri
        if( string.find(self.uri, 'doi:') > -1 ):
            self.uri = string.replace(self.uri,'doi:','')
            self.namespace = 'doi'     
            return 

        if( string.find(self.uri, 'isbn:') > -1 ):
            self.uri = string.replace(self.uri,'isbn:','')
            self.uri = isbn.isbn_strip(self.uri)
            self.namespace =  'isbn'
            return

        if( string.find(self.uri, 'pmid:') > -1 ):
            self.uri = string.replace(self.uri,'pmid:','')
            self.namespace =  'pmid'
            return

        # Check common features of the namespaces
        if( re.match(r"\d+\.\d+/",self.uri) ):
            self.namespace =  'doi' 
            return

        if( isbn.isValid(self.uri) ):
            self.uri = isbn.isbn_strip(self.uri)
            self.namespace =  'isbn' 
            return

    # Autopopulate fields from the url/uri via webservices or direct request
    def autopopulate(self):

        # DOI is available for this resource (preferable)
        if self.namespace == 'doi':
            data = autopopulate.doi(AutoReferenceself.uri)

        # No doi available, attempt lookup of information via ISBN if provided
        elif self.namespace == 'pmid':
            data = autopopulate.pmid(self.uri)

        elif self.namespace == 'isbn':
            # AMAZON WEB SERVICES, Google books, etc.
            data = autopopulate.isbn(self.uri)

        else: # URN value is not set therefore attempt lookup via http directly (html, image, media files)
            data = autopopulate.http(self.uri) # Use url to return, to prevent paths
        
        # DONE. Check we have result data, clear out existing from model & then pull in new
        if data:
            self.title = ''
            self.description = ''
            self.author = ''
            self.publisher = ''
            self.published = None

            for field, value in data['fields'].items():
                self.__setattr__( field, value )

            # Store meta (picklefield)
            self.meta = data['meta']


    # User-supplied URI
    uri = models.CharField('Identifier', max_length = 255, blank = True)

    # Namespace handling (isbn, doi, etc.)
    NAMESPACE_CHOICES = (
        ('isbn', 'ISBN: International Standard Book Number'),
        ('doi', 'DOI: Digital Object Identifier'),
        ('pmid', 'PMID: PubMed Identifier'),
    )
    namespace = models.CharField(max_length=4,choices=NAMESPACE_CHOICES, null = True, blank = True, default=None)
    slug = AutoSlugField(populate_from='title')

    # Information
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    author =  models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=50, blank=True) 
    published = models.DateField(max_length=50, blank=True, null=True) 
    # meta
    meta = JSONField(editable=False,blank=True,default=dict())

    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    updated_at = models.DateTimeField(auto_now = True, editable = False)   
    created_by = models.ForeignKey(User, null=True, blank = True, related_name='created_references') # Who added this reference


    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('namespace','uri','content_type','object_id'),)
        ordering = ['-published']


class AutoReference(models.Model):

    def __unicode__(self):
        return "%s %s" % (self.content_object, self.keywords)

    def autoref(self):
        uris = autoref.pubmed(self.keywords, self.latest_query_at)
        # We have some ids create the references
        for uri in uris:
            r = Reference(uri=uri, content_object=self.content_object)
            try:
                r.save()
            except:
                pass
            else:   
                if r.published:
                   r.created_at = r.published
                   r.save()

        self.latest_query_at = datetime.datetime.now()
        self.save()
        return len(uris)
        

    keywords = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)

    latest_query_at = models.DateTimeField(editable = False, null=True, blank=False)   

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

