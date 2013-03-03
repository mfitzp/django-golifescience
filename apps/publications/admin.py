from django.contrib import admin
# Methodmint
from publications.models import *

class PublicationAdmin(admin.ModelAdmin):
    fields = ('pmid','doi','isbn','title', 'description', 'author', 'publisher', 'published','created_by')
    #readonly_fields =('namespace', 'title', 'description', 'author', 'publisher', 'published',)


admin.site.register(Publication, PublicationAdmin)
admin.site.register(Reference)
admin.site.register(AutoReference)

