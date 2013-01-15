from django.conf.urls.defaults import *
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
# Methodmint
from testimonials.models import Testimonial
# External
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    # Testimonials
    url(r'^$', 'testimonials.views.testimonials', name='testimonials' ),
    url(r'^(?P<testimonial_id>\d+)/$', 'testimonials.views.testimonial', name='testimonial' ),
)
