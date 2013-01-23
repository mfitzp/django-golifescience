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
#from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
# Externals
from countries.models import Country
from easy_thumbnails.fields import ThumbnailerImageField
from subdomains.utils import reverse

def avatar_file_path(instance=None, filename=None):
    return os.path.join('avatar', str(instance.user.username), filename)

class UserProfile(models.Model):
    def __unicode__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse('user-profile',kwargs={'user_id':str(self.user.id)})

    def get_full_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username

    def locationquery(self):
        if self.postcode:
            return self.postcode
        else:
            return self.city + ', ' + self.country.printable_name

    def active_on_sites(self):
        return Site.objects.filter(method__author=self.user).distinct() #.unique('site')

    def usp(self):
        return UserSiteProfile.objects.get(user=self.user, site=Site.objects.get_current())

    def is_online(self):
        usp = self.usp()
        return usp.is_online()

    user = models.ForeignKey(User, unique=True, editable = False)
    
    PROFESSIONAL_TITLE_CHOICES = (
        ('Mr','Mr'),
        ('Miss','Miss'),
        ('Mrs','Mrs'),
        ('Ms','Ms'),
        ('Dr', 'Dr'),
        ('Prof', 'Prof'),
        ('Sir', 'Sir'),
        ('Dame', 'Dame'),
    )
    title = models.CharField(max_length=4,
                                      choices=PROFESSIONAL_TITLE_CHOICES,
                                      blank = True)

    postnomials = models.CharField('Postnomials', max_length = 50, blank = True)


    # Information
    about = models.TextField(blank = True)
    organisation = models.CharField('Organisation', max_length = 50, blank = True)
    avatar = ThumbnailerImageField(max_length=255, upload_to=avatar_file_path, blank=True, resize_source=dict(size=(128, 128), crop=True))
    # Location
    city = models.CharField('City', max_length = 50, blank = True)
    state = models.CharField('State/Province/Region', max_length = 50, blank = True)
    postcode = models.CharField('ZIP/Postal Code', max_length = 15, blank = True)
    country = models.ForeignKey(Country, null = True, blank = True)
    # Contact (email already in user model)
    telno = models.CharField('Telephone', max_length=50, blank = True)
    url = models.URLField(verify_exists = True, blank = True)

    # Social identities
    social_researchgate = models.CharField('ResearchGate', max_length = 50, blank = True)
    social_twitter = models.CharField('Twitter', max_length = 50, blank = True)
    social_facebook = models.CharField('Facebook', max_length = 50, blank = True)
    social_googleplus = models.CharField('Google+', max_length = 50, blank = True)




from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

# LOGIN SIGNAL, create Profile objects
def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
       up = UserProfile(user=user)
       up.save()

post_save.connect(create_profile, sender=User)




