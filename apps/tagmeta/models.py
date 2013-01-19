import os.path
import datetime
# Django
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.template.defaultfilters import slugify
# Externals
from taggit.models import Tag
from taggit.managers import TaggableManager
from easy_thumbnails.fields import ThumbnailerImageField
from mptt.models import MPTTModel, TreeForeignKey


def sponsor_file_path(instance=None, filename=None):
    return os.path.join('tag', slugify( instance.name ))

def sponsor_icon_file_path(instance=None, filename=None):
    return os.path.join('tag', slugify( instance.name ) + '-icon')

# Metadata for site
class TagMeta(MPTTModel):
    def __unicode__(self):
        return "%s" % (self.tag.name)

    tag = models.ForeignKey(Tag, related_name='meta')

    # Hierarchical tags
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    # Information
    description = models.TextField(blank = True)
    sponsor = models.ForeignKey('TagSponsor', blank=True, null=True)

    objects = models.Manager()  

    class Meta:
        ordering = ['tree_id','lft']

    class MPTTMeta:
        order_insertion_by = ['tag']

class TagSponsor(models.Model):
    def __unicode__(self):
        return "%s" % (self.name)

    # Information
    name = models.CharField('Name', max_length = 50, blank = False)
    description = models.TextField('Description', blank = True)
    links = models.TextField('Sponsored Links', blank = True)

    # Visuals
    icon = ThumbnailerImageField('Tag icon', max_length=255, upload_to=sponsor_icon_file_path, blank=True, default='')    
    image = ThumbnailerImageField('Tag sponsor image', max_length=255, upload_to=sponsor_file_path, blank=True, default='')    

