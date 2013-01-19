from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
# Methodmint
from tagmeta.models import TagMeta, TagSponsor
# External
from mptt.admin import MPTTModelAdmin

admin.site.register(TagMeta, MPTTModelAdmin)
admin.site.register(TagSponsor)

