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
from publications import isbn
from publications import autopopulate
from publications import autoref
#External
from autoslug.fields import AutoSlugField
#from picklefield.fields import PickledObjectField, PickledObject
from jsonfield.fields import JSONField
from subdomains.utils import reverse
from core.actions import object_saved

# A reference object, pointing to an external resource via URN or URL
class Reference(models.Model):
    
    # Dummy functions to passthru to the attached publication (simplifies use avoiding ref.publication.thing)
    def __unicode__(self):
        if self.publication:
            return self.publication.__unicode__()
        else:
            return 'No publication matching %s found' % self.uri

    def get_absolute_url(self):
        if self.publication:
            return self.publication.get_absolute_url()
    def get_absolute_path(self):
        if self.publication:
            return self.publication.get_absolute_path()

    def et_al(self):
        if self.publication:
            return self.publication.et_al()
    
    @property
    def tagline(self):
        if self.publication:
            return self.publication.tagline()

    def url(self):
        if self.publication:
            return self.publication.url()

    # On save, check if reference created/changed & update accordingly
    def save(self, force_insert=False, force_update=False):
        if self.pk == None or self.uri.endswith('!'):
            self.uri = self.uri.strip('!')
            self.getnamespace()
            self.find_or_create_publication()

        super(Reference, self).save(force_insert, force_update)


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

    def find_or_create_publication(self):
        # We have a object var 'namespace' holding the field to go a lookin in for 'uri'
        # do a search of the table and see if we can find it
        # If we can save the reference to the field and let the save continue
        po = Publication.objects

        if self.namespace == 'pmid':
            po = po.filter(pmid=self.uri)
        elif self.namespace == 'doi':
            po = po.filter(doi=self.uri)
        elif self.namespace == 'isbn':
            po = po.filter(isbn=self.uri)

        if po: # We have something
            p = po[0]
            self.publication = p
        else:
            # We don't we must created it!
            p = Publication(created_by=self.created_by)
            if self.namespace == 'pmid':
                p.pmid = self.uri
            elif self.namespace == 'doi':
                p.doi = self.uri
            elif self.namespace == 'isbn':
                p.isbn = self.uri
            p.save() # autopopulates
            self.publication = p
        
    
    # Namespace handling (isbn, doi, etc.)
    NAMESPACE_CHOICES = (
        ('pmid', 'PMID: PubMed Identifier'),
        ('isbn', 'ISBN: International Standard Book Number'),
        ('doi', 'DOI: Digital Object Identifier'),
    )
    namespace = models.CharField(max_length=4,choices=NAMESPACE_CHOICES, null = True, blank = True, default=None)
    # User-supplied URI
    uri = models.CharField('Identifier', max_length = 255, blank = True)

    publication = models.ForeignKey('Publication', blank=True, null=True, related_name='references')

    created_by = models.ForeignKey(User, related_name='created_references') # Who added this reference

    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    updated_at = models.DateTimeField(auto_now = True, editable = False)   

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


    class Meta:
        unique_together = (('publication','content_type','object_id'),)
        ordering = ['-created_at']


# A publication object, holds data about the external resource
class Publication(models.Model):

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('publication',kwargs={'publication_id':str(self.id), 'publication_slug':str(self.slug)}, subdomain=None)
    def get_absolute_path(self):
        return django_reverse('publication',kwargs={'publication_id':str(self.id), 'publication_slug':str(self.slug)})

    # On save, check if reference created/changed & update accordingly
    def save(self, force_insert=False, force_update=False):
        if self.pk == None:
            self.autopopulate()
            
        super(Publication, self).save(force_insert, force_update)

    def et_al(self):
        if self.author:
            al = self.author.split(', ')
            return '%s et al.' % al[0]

    def tagline(self):
        if self.published:
            return "%s %s (%s)" % (self.et_al(), self.publisher, self.published.year)
        else:
            return "%s %s" % (self.et_al(), self.publisher)
    
    # Generate an standard resource URL for this resource object
    # Preference is given to doi, then urn, then direct links
    def url(self):
        if self.doi:
            return "http://dx.doi.org/%s" % self.doi
        elif self.isbn:
            if 'asin' in self.meta: # If we have direct product link, use it
                return "http://www.amazon.com/dp/%s?tag=mutadsman-20" % self.meta['asin']
            else:
                return "http://www.amazon.com/gp/search/ref=sr_adv_b/?field-isbn=%s&_encoding=UTF8&tag=mutadsman-20&linkCode=ur2&camp=1789&creative=390957" % self.isbn
        elif self.pmid:
            return "http://www.ncbi.nlm.nih.gov/pubmed/%s" % self.pmid

    # Autopopulate fields from the url/uri via webservices or direct request
    def autopopulate(self):

        # DOI is available for this resource (preferable)
        if self.doi:
            data = autopopulate.doi(self.doi)

        # No doi available, attempt lookup of information via ISBN if provided
        elif self.pmid:
            data = autopopulate.pmid(self.pmid)

        elif self.isbn:
            # AMAZON WEB SERVICES, Google books, etc.
            data = autopopulate.isbn(self.isbn)
        
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


    # Global identifiers (any one will do; pmid > doi > isbn
    pmid = models.CharField('PMID', max_length = 255, blank = True, null=True, unique=True)
    doi = models.CharField('DOI', max_length = 255, blank = True, null=True, unique=True)
    isbn = models.CharField('ISBN', max_length = 255, blank = True, null=True, unique=True)

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
    created_by = models.ForeignKey(User, related_name='created_publications') # Who added this publication

    class Meta:
        #unique_together = (('pmid','doi','isbn')) # Ideally, we want all fields to be unique *but* allow blanks
        ordering = ['-published']


class AutoReference(models.Model):

    def __unicode__(self):
        return "%s %s" % (self.content_object, self.keywords)

    def autoref(self, user=False):
        if user == False: # Assign to Miss Baker if not specified
                user = User.objects.get(username='missbaker')

        uris = autoref.pubmed(self.keywords, self.latest_query_at)
        # We have some ids create the references
        for uri in uris:
            r = Reference(uri=uri, namespace='pmid', content_object=self.content_object, created_by=user)
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

    content_type = models.ForeignKey(ContentType) #, null=True, blank=True)
    object_id = models.PositiveIntegerField() #null) #=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')


# Action Stream
post_save.connect(object_saved, sender=Publication)


