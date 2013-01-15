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

# Externals
from easy_thumbnails.fields import ThumbnailerImageField

def testimonial_file_path(instance=None, filename=None):
    return os.path.join('testimonial', str(instance.id), filename)

# Testimonial class
class Testimonial(models.Model):
    def __unicode__(self):
        return "%s, %s" % (self.customer_name, self.customer_location)

    def get_absolute_url(self):
        return reverse('testimonial',kwargs={'testimonial_id':str(self.id)})

    # Information
    testimonial = models.TextField(blank = True)
    customer_name = models.CharField('Customer Name', max_length = 50, blank = False)
    customer_location = models.CharField('Customer Location', max_length = 50, blank = True)

    image = ThumbnailerImageField(max_length=255, upload_to=testimonial_file_path, blank=True)    

    objects = models.Manager()  

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)   



