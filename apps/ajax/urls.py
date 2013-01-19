from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^hit/$',
    	        'hitcount.views.update_hit_count_ajax',
    	        name='hitcount_update_ajax'),
)
