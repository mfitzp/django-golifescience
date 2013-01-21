import datetime
# Django
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
# Methodmint
from profiles.models import UserSiteProfile

class UserActivityMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            now = datetime.datetime.now()
            site = Site.objects.get_current()
            ( siteprofile, created ) = UserSiteProfile.objects.get_or_create(user=request.user, site=site)

            # Create site profile if there is None, its been 15minutes since last activity, or we're receiving a POST
            if (siteprofile.last_active is None) or ( siteprofile.last_active < now - datetime.timedelta(minutes=15) ) or ( request.method == 'POST' ):
                # update last_active
                siteprofile.last_active = now
                siteprofile.save()

